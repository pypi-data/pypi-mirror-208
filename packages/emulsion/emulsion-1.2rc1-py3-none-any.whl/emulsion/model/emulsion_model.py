"""
.. module:: emulsion.model.emulsion_model

.. moduleauthor:: Sébastien Picault <sebastien.picault@inra.fr>

"""


# EMULSION (Epidemiological Multi-Level Simulation framework)
# ===========================================================
# 
# Contributors and contact:
# -------------------------
# 
#     - Sébastien Picault (sebastien.picault@inrae.fr)
#     - Yu-Lin Huang
#     - Vianney Sicard
#     - Sandie Arnoux
#     - Gaël Beaunée
#     - Pauline Ezanno (pauline.ezanno@inrae.fr)
# 
#     INRAE, Oniris, BIOEPAR, 44300, Nantes, France
# 
# 
# How to cite:
# ------------
# 
#     S. Picault, Y.-L. Huang, V. Sicard, S. Arnoux, G. Beaunée,
#     P. Ezanno (2019). "EMULSION: Transparent and flexible multiscale
#     stochastic models in human, animal and plant epidemiology", PLoS
#     Computational Biology 15(9): e1007342. DOI:
#     10.1371/journal.pcbi.1007342
# 
# 
# License:
# --------
# 
#     Copyright 2016 INRAE and Univ. Lille
# 
#     Inter Deposit Digital Number: IDDN.FR.001.280043.000.R.P.2018.000.10000
# 
#     Agence pour la Protection des Programmes,
#     54 rue de Paradis, 75010 Paris, France
# 
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
# 
#         http://www.apache.org/licenses/LICENSE-2.0
# 
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.


from   pathlib                 import Path
from   datetime                import datetime, timedelta
from   copy                    import deepcopy

import yaml
import dateutil.parser         as     dup

from   sympy                   import sympify, Symbol

from   collections             import OrderedDict
from   sortedcontainers        import SortedSet, SortedDict
from   jinja2                  import Environment, PackageLoader

import networkx                as     nx

from   emulsion.tools.state    import StateVarDict
from   emulsion.tools.misc     import read_csv_prototypes, read_from_file, load_class
from emulsion.tools.getters import create_new_serial, create_weighted_random, \
    create_successor_getter, create_predecessor_getter, \
    make_random_prototype_getter, make_generator_prototype_getter, create_state_indexer, create_my_state_indexer, \
    create_lazy_ternary, create_lazy_AND, create_lazy_OR, create_duration_getter, create_state_tester
from   emulsion.tools.calendar import EventCalendar
from   emulsion.tools.debug    import debuginfo

from   emulsion.model.functions      import DEFAULT_LEVEL_INFO, DEFAULT_GROUPING_INFO, AGGREG_COMP, AGGREG_HYBRID, AGGREG_METAPOP, AGGREG_IBM, make_function, make_CSV_function, make_when_condition, make_statevar_getter, make_model_value_getter
from   emulsion.model.exceptions     import SemanticException
from   emulsion.model.state_machines import StateMachine

#  ______                 _     _             __  __           _      _
# |  ____|               | |   (_)           |  \/  |         | |    | |
# | |__   _ __ ___  _   _| |___ _  ___  _ __ | \  / | ___   __| | ___| |
# |  __| | '_ ` _ \| | | | / __| |/ _ \| '_ \| |\/| |/ _ \ / _` |/ _ \ |
# | |____| | | | | | |_| | \__ \ | (_) | | | | |  | | (_) | (_| |  __/ |
# |______|_| |_| |_|\__,_|_|___/_|\___/|_| |_|_|  |_|\___/ \__,_|\___|_|


class EmulsionModel(object):
    """Class in charge of the description of a multi-level
    epidemiological model. Such models are composed of several
    processes which may take place at different
    organization/observation levels. Some of those processes are
    reified through a function implemented within an agent, while
    others are represented by a state machine. The model is also in
    charge of handling symbolic expressions and pre-computing their
    values, e.g. concerning parameters, transmission functions,
    etc.

    """
    def __init__(self, filename=None, description=None, input_dir=None, changed_values=None):
        """Instantiate the model either from a configuration file or from a
        string. Both must contain a YAML-based description of the model.

        Parameters
        ----------
        filename: str
            the path to the YAML file to read
        description: str
            a YAML description of the model
        input_dir: Path
            the path to the directory where additional data files can be found if needed (default: 'data')
        changed_values: dict
            changes if parameter values, if any, specified by command-line option '-p' or '--param'

        """
        self.input_dir = input_dir
        self.filename = filename
        model_description = read_from_file(filename) if self.filename is not None else description
        if changed_values is not None:
            model_description = self.change_parameter_values(model_description, changed_values)
        self.parse(model_description)


    def __repr__(self):
        return '%s "%s"' % (self.__class__.__name__, self.model_name)

    def normalize_format(self):
        """Return a YAML representation of the model, reformatted to to print
        lists and dicts using the flow style (no [], no {}) instead of
        the block style, especially for syntax checking where rules
        are defined only for flow style.

        """
        return yaml.dump(self._description, default_flow_style=False)

    def copy(self):
        """Return a copy of object (naif method).
        TODO: Find a way to avoid recharging compartment class when
        intentiate a MultiProcessManager class with a old model.

        """
        return deepcopy(self)

    def _reset_all(self):
        # namespace for all symbols used in the model
        # dict string -> sympy symbol
        self._namespace = {}
        # namespace for calendar periods in the model
        # dict string -> sympy symbol
        self._event_namespace = {}
        # cache for all expressions encountered in the model
        # dict string -> sympy expression
        self._expressions = {}
        # cache for all values encountered in the model
        # dict string -> value or function
        self._values = {}
        # the original description to parse (dict from YAML document)
        self._description = {}
        # default values for modules used in symbolic computing
        self.modules = ['emulsion.tools.functions', 'numpy', 'numpy.random', 'math', 'sympy']
        # name of the model
        self.model_name = 'New Model'
        # time unit (used to specify parameter values)
        self.time_unit = 'days'
        # duration of a simulation time step (number of time_units)
        self.delta_t = 1
        # duration of a simulation time step ('true' duration)
        self.step_duration = timedelta(days=1)
        # origin date for the simulation
        self.origin_date = datetime.now()
        # dictionary of calendars (keyed by their name)
        self.calendars = SortedDict()
        # reverse dict event -> calendar name
        self._events = {}
        # dict of levels
        self.levels = {}
        # dict of default prototypes associated to levels
        self.default_prototypes = {}
        # dict of aggregate vars by level
        self.aggregate_vars = {}
        # list of the processes involved in the model
        self.processes = []
        # description of the compartment associated with some of the processes
        self.compartments = {}
        # description of the state machines associated with some of the processes
        self.state_machines = {}
        # dict of all 'parameters' encountered in the model
        self.parameters = StateVarDict()
        # dict of all 'statevars' encountered in the model
        self.statevars = StateVarDict()
        # # dict of all conditions encountered in the model
        # self.conditions = {}
        # dict of all actions encountered in the model
        self.actions = {}
        # dict of actions to run for state initialization
        self.init_actions = {}
        # dict of all distributions encountered in the model
        self.distributions = {}
        # dict of all prototypes encountered in the model
        self.prototypes = {}
        # prototype collections: list of functions providing a prototype_name
        # for a given collection name
        self.prototype_collection = {}
        # dict of all initial conditions encountered in the model
        self.initial_conditions = {}
        # dict of enumerate types used in special variables
        self.types = {}
        # dict of all states existing in state machines
        self.states = StateVarDict()
        # dict of parameters to log when explicitly changed
        self.params_to_log = StateVarDict()
        # dict of data-based parameters {level -> {filename -> (key variables, parameter names)}}
        self.databased_parameters = {}
        # set of parameters associated with a level-specific value
        # CRUCIAL ROLE in get_information mechanisms (subsumes others)
        self.parameters_by_level = set()




    def add_init_action(self, machine_name, state, action):
        """Add an action to be performed when initializing agents for
        the specified state of the state machine. Mainly used for
        durations.

        """
        if machine_name not in self.init_actions:
            self.init_actions[machine_name] = {}
        if state not in self.init_actions[machine_name]:
            self.init_actions[machine_name][state] = [action]
        else:
            self.init_actions[machine_name][state].append(action)


    def _init_namespace(self):
        """Init the list of all encountered symbols, which have to be
        either parameters or state variables. The association between
        the name and the corresponding Symbol is stored in the
        namespace attribute.

        """
        # name space for 'regular' symbols (i.e. parameters, statevars)
        self._namespace.clear()

        for keyword in ['parameters', 'statevars']:
            if keyword in self._description:
                self._namespace.update({param: Symbol(param)
                                        for param in self._description[keyword]})
            else:
                self._description[keyword] = {}

    def get_value(self, name):
        """Return the value associated with the specified name. If the method
        is called with a name that is not in the model values, try to
        parse the expression, to prevent failures when called with a
        final value.

        """
        if name == "delta_t":
            return self.delta_t
        try:
            return self._values[name]
        except KeyError:
            try:
                return float(sympify(name, locals=self._namespace))
            except TypeError:
                ### cases of string parameters ?
                return name
                # result = sympify(name, locals=self._namespace)
                # import sys
                # sys.exit(-1)

    def change_parameter_values(self, description, d_changes):
        """Naive method to change several parameter values at the same time.

        Parameters
        ----------
        description: str
            the YAML description of the model
        d_changes: dict
            the dict of parameters that will be modified (name -> new value)

        Returns
        -------
        str:
            the new YAML description of the model with modified parameter _values

        """
        for name, value in d_changes.items():
            if name == 'delta_t':
                description['time_info']['delta_t'] = value # was int(value) previously
            else:
                description['parameters'][name]['value'] = value
        return description
        ## TODO: below log_params is DEPRECATED and not used anymore
        # self.parse(self._description)
        # self.params_to_log.clear()
        # if log_params:
        #     for name in changes:
        #         value = self.get_value(name) if name != 'delta_t'\
        #                                      else self.delta_t
        #         self.params_to_log[name] = value

    def set_value(self, name, value):
        """Naif method to change a parameter's value.
        Will be more efficient when treating several parameters at
        the same time.

        """
        self._description['parameters'][name]['value'] = value
        self.parse(self._description)

    def parse(self, description):
        """Build the EmulsionModel from the specified dictionary
        (expected to come from a YAML configuration file).

        """
        self._reset_all()
        # keep an exhaustive description
        self._description = description
        # retrieve the name of the model
        self.model_name = self._description['model_name']
        # build association between symbols names (all parameter and
        # statevars names) and true sympy symbols
        self._init_namespace()
        # parse data-based information
        self.build_input_data()
        # parse time informations
        self.build_timeinfo()
        # parse output options
        self.build_outputs_options()
        #  rapidly check state machines to build is_state and
        #  duration_in_state_machine properties
        self.check_state_machines()
        # parse parameters, state variables and distributions
        self.build_parameters()
        self.build_statevars()
        self.build_levels()
        self.build_distributions()
        # parse processes
        self.build_processes()
        # parse compartment description
        self.build_compartment_desc()
        # parse state machines
        self.build_state_machines()
        # parse prototypes
        self.build_prototypes()
        # parse initial_conditions
        self.build_initial_conds()
        # parse actions
        self.build_actions()
        # # calculate expressions from parameters
        # self.calculate_compound_params()
        # replace expressions by values or lambdas
        self.compute_values()
        self._description['parameters']['delta_t'] = {
            'desc': 'duration of the simulation time step',
            'value': self.delta_t
        }

    def build_outputs_options(self):
        """Parse the outputs options of the model.
        The agents will treat extra variables for outputs (TODO), and
        the simulation classes will treat period outputs.

        Example of YAML specification:
        ------------------------------
        outputs:
          # level
          herd:
            period:1
          # level
          metapop:
            period: 7
            extra_vars:
              - step
              - infection_date
        """
        if 'outputs' in self._description:
            self.outputs = self._description['outputs']
        else:
            self.outputs = {}

    def build_timeinfo(self):
        """Parse the description of the model and extract the
        information related to time management, i.e. time unit,
        duration of a simulation step, origin date, calendars for
        specific events, etc.

        Example of YAML specification:
        ------------------------------
        time_info:
        time_unit: days
        delta_t: 7
        origin: 'May 1'
        calendar:
          name:
          period: {days: 52}
          events:
            spring: {begin: 'April 8', end: 'April 23'}
            summer: {begin: 'July 8', end: 'September 3'}
            national: {date: 'July 14'}
        """
        self._event_namespace.clear()
        if 'time_info' in self._description:
            tinfo = self._description['time_info']
            # compute effective duration of one time step
            self.time_unit = tinfo['time_unit']
            # parse expression for delta_t if any and store its value
            # into the delta_t attribute
            # self.delta_t = tinfo['delta_t']
            self.delta_t = float(sympify(tinfo['delta_t'], locals=self._namespace))
            timedesc = {self.time_unit: self.delta_t}
            self.step_duration = timedelta(**timedesc)
            # origin date for the simulation
            if 'origin' in tinfo:
                self.origin_date = dup.parse(tinfo['origin'])
            # total duration for the simulation (in time units)
            if 'total_duration' in tinfo:
                self.parameters['total_duration'] = sympify(tinfo['total_duration'], locals=self._namespace)

            if 'stop_condition' in tinfo:
                self.parameters['stop_condition'] = sympify(tinfo['stop_condition'], locals=self._namespace)
                self.conditional_stop = True
            else:
                self.conditional_stop = False
            # handle calendars
            if 'calendars' in tinfo:
                self.build_calendar(tinfo['calendars'])


    def build_calendar(self, calendar_desc):
        """Build a representation of calendars."""
        # init name space for 'event' symbols (periods of
        # time) and handle period definitions
        for cal_name, cal in calendar_desc.items():
            events = {}
            if 'events' in cal:
                cal_period = timedelta(**cal['period']) if 'period' in cal else None
                for event_name, definition in cal['events'].items():
                    # register the event name in the events namespace
                    self._event_namespace[event_name] = Symbol(event_name)
                    # if keyword "date" is used, begin = end
                    if 'date' in definition:
                        events[event_name] = (dup.parse(definition['date']),
                                              dup.parse(definition['date']))
                    else:
                        events[event_name] = (dup.parse(definition['begin']),
                                              dup.parse(definition['end']))
                        # if begin and end date are specified,
                        # register events corresponding to "begin_event"
                        # and "end_event"
                        for keyword in ['begin', 'end']:
                            event_limit = keyword + '_' + event_name
                            self._event_namespace[event_limit] = Symbol(event_limit)
                            events[event_limit] = (dup.parse(definition[keyword]),
                                                   dup.parse(definition[keyword]))
                    # register the durations of each event
                    # compute duration of event
                    begin, end = events[event_name]
                    if end >= begin:
                        dur = end - begin
                    else:
                        dur = end - begin + cal_period
                    # compute duration of 1 time unit
                    unit = {self.time_unit: 1}
                    dur_unit = timedelta(**unit)
                    if (dur_unit > timedelta(days=1)):
                        dur += timedelta(days=1)
                    else: # 1h / 1min / 1s ...
                        dur += dur_unit
                    # convert duration to time units
                    event_duration = dur / dur_unit
                    duration_param = 'duration_of_{}'.format(event_name)
                    self._namespace[duration_param] = Symbol(duration_param)
                    self._values[duration_param] = sympify(event_duration)
                    # cal_name = cal['name']
            self.calendars[cal_name] = EventCalendar(cal_name,
                                                     self.step_duration,
                                                     self.origin_date,
                                                     cal_period,
                                                     **events)
            for event in self.calendars[cal_name].get_events():
                self._events[event] = cal_name
                expression = sympify(event, locals=self._event_namespace)
                self._values[str(expression)] = make_when_condition(
                    expression, modules=self.modules)


    def get_calendar_for_event(self, name):
        """Return the calendar providing the specified event name."""
        return self.calendars[self._events[name]]

    def build_parameters(self):
        """Parse the description of the model and extract the
        parameters, either with their value, or with the expression to
        compute them.

        Example of YAML specification:
        ------------------------------
        parameters:
          p:
            desc: infection probability
            value: '(1-exp(-E_total)) * (1 - phi*vaccinated)'
          phi:
            desc: efficiency of vaccination
            value: 0.79

        """
        if 'modules' in self._description:
            self.modules += self._description['modules']
        if 'parameters' in self._description:
            for (key, val) in self._description['parameters'].items():
                # experimental
                if isinstance(val['value'], dict):
                    self._values[key] = self.parse_dict(key, val['value'])
                    self._namespace[key] = Symbol(key)
                else:
                    self.parameters[key] = sympify(val['value'], locals=self._namespace)



    def build_statevars(self):
        """Parse the description of the model and extract the state
        variables that agents running this model must have.

        Example of YAML specification:
        ------------------------------
        statevars:
          E_total:
            desc: total bacteria deposited in the environment
          vaccinated:
            desc: 0/1 value describing the vaccination state

        """
        ## at this point, data-based level-dependent parameters (if
        ## any) have already been added to the 'statevars' section
        if 'statevars' in self._description:
            self.statevars = StateVarDict(self._description['statevars'])


    def build_distributions(self):
        """Parse the description of the model and extract the
        distributions, either with their value, or with the expression
        to compute them. A distribution is a dictionary of the form
        {quantity: probability}. It is stored as a list of tuples
        (quantity, probability) which is more convenient for
        subsequent processing.

        TODO: check if completely obsolete ??? deprecated ???

        Example of YAML specification:
        ------------------------------
        distributions:
          - shedding_dist1:
              desc: distribution of shedding
              value:
                low_shedding: 0.85
                med_shedding: 0.15

        """
        if 'distributions' in self._description:
            for list_item in self._description['distributions']:
                for (key, val) in list_item.items():
                    self.distributions[key] = [
                        (sympify(quantity, locals=self._namespace),
                         sympify(probability, locals=self._namespace))
                        for quantity, probability in val['value'].items()]

    def build_initial_conds(self):
        """Parse the description of the model and extract the initial
        conditions for each level, either with their value, of with
        the expression to compute them. An initial condition is a
        dictionary containing a description of the 'content' of the
        level (i.e. the quantity and initial state of sub-levels),
        defined by a list of prototypes and corresponding amounts

        Example of YAML specification:
        ------------------------------
        initial_conditions:
          metapop:
            - prototype: healthy_herd # defines init_prevalence
              amount: 100
            - prototype: infected_herd
              amount: 1
          herd:
            - prototype: [healthy_animal, infected_animal]
              amount: 'init_pop'
              proba: ['1 - init_prevalence', 'init_prevalence']

        """
        if 'initial_conditions' in self._description:
            for level, desc in self._description['initial_conditions'].items():
                self.initial_conditions[level] = []
                for list_items in desc:
                    l_protos = list_items['prototype']
                    if not isinstance(l_protos, list):
                        l_protos = [l_protos]
                        list_items['prototype'] = l_protos
                    amount = list_items['amount']
                    if 'proba' in list_items:
                        l_probas = list_items['proba']
                        if not isinstance(l_probas, list):
                            l_probas = [l_probas]
                    else:
                        l_probas = ['1'] * len(l_protos)
                    list_items['proba'] = l_probas
                    if not (0 <= len(l_protos) - len(l_probas) <= 1):
                        raise SemanticException('In initial conditions: inconsistent numbers of prototypes/probabilities\n\tprototypes: {}, probabilities: {}'.format(l_protos, l_probas))
                    self.initial_conditions[level].append(
                        (l_protos, self.add_expression(amount), [self.add_expression(p) for p in l_probas]))

    def build_prototypes(self):
        """Parse the description of the model and extract the list of
        prototypes for each level, either with their value, or with
        the expression to compute them. A prototype is a dictionary of
        the form {statevar: value}..

        Example of YAML specification:
        ------------------------------

        .. code-block:: yaml

           prototypes:
             animals:           # name of a level
               - newborn:       # prototype name
                   # description of the prototype
                   desc: 'prototype for new calves'
                   # list of variables with values
                   health_state: M
                   life_state: NP
                   age: 0

        """
        if 'prototypes' in self._description:
            for level, prototypes in self._description['prototypes'].items():
                self.prototypes[level] = {}
                for list_item in prototypes:
                    # read all prototypes for a given level
                    for (key, val) in list_item.items():
                        prototype = OrderedDict()
                        # read all variables for prototype named "key"
                        for variable, value in val.items():
                            result = self.parse_prototype_line(variable, value)
                            if result is not None:
                                prototype[variable] = result
                        # test if an ordered affectation is defined:
                        # if so, parse the list of variable
                        # assignation as a list of tuples (name of
                        # variable, value)
                        for keyword in ['begin_with', 'end_with']:
                            if keyword in val:
                                l_items = []
                                for proto_item in val[keyword]:
                                    for variable, value in proto_item.items():
                                        result = self.parse_prototype_line(variable, value)
                                        l_items.append((variable, result))
                                prototype[keyword] = l_items
                        # test if a collection is defined
                        if 'file' in val:
                            # this is not an isolated prototype but a
                            # collection of prototypes specified in a
                            # CSV file
                            # check if any filtering condition on the lines of the CSV file
                            cond = make_CSV_function(self.expand_expression(val['filter']), self.modules) if 'filter' in val else None
                            include_values = val['include_values'] if 'include_values' in val else []
                            exclude_values = val['exclude_values'] if 'exclude_values' in val else []
                            # check the selection method that will be used to pick real prototypes in the collection
                            if 'select' not in val:
                                raise SemanticException('No selection method provided for prototype collection {}'.format(key))
                            method = val['select']
                            par_start = method.find('(')
                            if par_start > 0:
                                par_end = method.find(')')
                                if par_end < par_start:
                                    raise SemanticException('Bad parenthesis in selection method {} for prototype collection {}'.format(method, key))
                                special_column = method[(par_start+1):par_end]
                                method = method[0:par_start]
                            else:
                                special_column = None
                            if method not in ['ordered', 'ordered_cycle', 'random_replace', 'random_noreplace']:
                                raise SemanticException('Unknown selection method {} for prototype collection {}'.format(method, key))
                            collection = read_csv_prototypes(key, self.input_dir.joinpath(val['file']), method=method,
                                                             condition=cond, weight_column=special_column, include=include_values, exclude=exclude_values)
                            for proto_freq, proto_name, proto_desc in collection:
                                specific_prototype = OrderedDict()
                                # parse each
                                for spec_var, spec_val in proto_desc.items():
                                    result = self.parse_prototype_line(spec_var, spec_val)
                                    if result is not None:
                                        specific_prototype[spec_var] = result
                                # correct prototype defined in CSV
                                # file with information provided in
                                # YAML model
                                specific_prototype.update(prototype)
                                # add each concrete prototype
                                self.prototypes[level][proto_name] = specific_prototype
                            # register collection named "key"
                            freqs, names, _ = zip(*collection)
                            if method == 'random_replace':
                                self.prototype_collection[key] = make_random_prototype_getter(names, freqs)
                            else:
                                self.prototype_collection[key] = make_generator_prototype_getter(names, freqs, key, method, (method == 'ordered_cycle'))
                        else:
                            self.prototypes[level][key] = prototype


    def parse_prototype_line(self, variable, value):
        """Parse a line in a prototype definition, udpate the model if needed,
        and return the resulting value.

        """
        if variable in ['desc', 'begin_with', 'end_with', 'file', 'filter', 'select', 'include_values', 'exclude_values']:
            return None
        # default case
        result = value
        if value == 'random':
            result = '_random_' + variable
        elif value == 'default':
            result = '_default_' + variable
        elif value == 'next_state':
            result = '_next_state_' + variable
            # associate to a function that returns the successor of
            # the state contained in the variable (or a random state
            # if the variable was not defined)
            self._values[result] = create_successor_getter(variable)
        elif value == 'previous_state':
            result = '_previous_state_' + variable
            # associate to a function that returns the predecessor of
            # the state contained in the variable (or a random state
            # if the variable was not defined)
            self._values[result] = create_predecessor_getter(variable)
        elif type(value) == str and value.startswith('random('):
            # result = '_weighted_random_' + variable
            result = '{}_{}'.format(variable, value)
            if value[6] == '(' and value[-1] == ')':
                weights = [self.add_expression(e) for e in value[7:-1].split(',')]
            self._values[result] = create_weighted_random(variable, weights, model=self)
        elif type(value) == str and value.startswith('serial'):
            result = '_serial_' + variable
            if value != 'serial' and value[6] == '(' and value[-1] == ')':
                end = self.add_expression(value[7:-1])
            else:
                start, end = 0, None
            self._values[result] = create_new_serial(end=end, model=self)
        elif isinstance(value, list):
            result = tuple(value)
        elif value in self.statevars:
            self._values[result] = make_statevar_getter(result)
        elif value in self.parameters:
            self._values[result] = make_model_value_getter(result)
        elif value not in self.states:
            self._values[value] = self.add_expression(value)
        # debuginfo(variable, value, result)
        return result


    def get_prototype(self, level, name, simu_id=None):
        """Return a ready-to-use prototype, i.e. a StateVarDict corresponding
        to the prototype for the specified level and name, where
        symbols associated to statevariables are already replaced by
        their value in the model. 'Hard-coded' lists are transformed
        into tuples (to be hashable).

        """
        if name in self.prototype_collection:
            # use the associated function to retrieve concrete prototype
            prototype_name = self.prototype_collection[name](simu_id)
        else:
            prototype_name = name
        ## compute concrete prototype by getting relevant values
        result = StateVarDict()
        for var, val in self.prototypes[level][prototype_name].items():
            if var in ['begin_with', 'end_with']:
                ordered = []
                for k, v in val:
                    value = tuple(v) if isinstance(v, list) else self.get_value(v)
                    ordered.append((k, value))
                result[var] = ordered
            else:
                result[var] = tuple(val) if isinstance(val, list) else self.get_value(val)
        return result

    def build_input_data(self):
        """Parse the description of input data (for now, data-based parameters
        associated with a level).

        EXPERIMENTAL FEATURE

        Example of YAML specification:
        ------------------------------

        input_data:
          databased_parameters:
            - level: herd
              file: myparams.csv
              key_variables: population_id
              parameters:
                herd_size:
                  desc: 'initial size of the herd'
                biosecurity:
                  desc: 'biosecurity level (0-1)'

        """
        self.preprocessing = []
        if 'input_data' in self._description:
            input_data = self._description['input_data']
            # parse pre-processing instructions
            if 'preprocessing' in input_data:
                self.preprocessing = input_data['preprocessing']
                ## the management of preprocessing actions is left to Simulation class
            # debuginfo(self.preprocessing)
            # parse parameters which are time- and entity-dependent
            # (functions provided in extension as a CSV file)
            if 'data_based_parameters' in input_data:
                # parse all descriptions (list))
                for csv_desc in input_data['data_based_parameters']:
                    # retrieve level, filename, key variables and description of parameters
                    level = csv_desc['level']
                    filename = csv_desc['file']
                    key_variables = csv_desc['key_variables']
                    # if needed transform into list
                    if not isinstance(key_variables, list):
                        key_variables = [key_variables]
                    param_desc = csv_desc['parameters']
                    l_params = list(param_desc.keys())
                    if level not in self.databased_parameters:
                        self.databased_parameters[level] = {}
                    self.databased_parameters[level][filename] = (key_variables, l_params)
                    # self.parameters_by_level |= set(l_params)
                    # parse parameter specification
                    for param_name, param_spec in param_desc.items():
                        # add parameter name to local namespace
                        self._namespace[param_name] = Symbol(param_name)
                        # add parameter description to 'statevars' section in the _description
                        if 'statevars' not in self._description:
                            self._description['statevars'] = {}
                        self._description['statevars'][param_name] = {
                            'desc': param_spec['desc'],
                            'source': filename
                        }
        for level in self.databased_parameters:
            # debuginfo(level)
            for filename, desc in self.databased_parameters[level].items():
                key_variables, l_params = desc
                # debuginfo('\t', filename, ':', key_variables, '->', l_params)

    def build_levels(self):
        """Parse the description of different level of simulations.
        Most of time, there are tree differents levels:
        individual, herd, metapopulation.

        Example of YAML specification:
        ------------------------------
        levels:
          individuals:
            super:
              class: AtomAgent
            class_name: Cow
          herd:
            super:
              class: MultiProcessManager
            class_name: QfeverHerd
          metapop:
            super:
              class: MultiProcessManager
              master_class: StructuredView
            class_name: QfeverMetaPop

        """
        if 'levels' in self._description:
            self.levels = self._description['levels']
            self.root_level = None
            self.levels_graph = nx.DiGraph()

        # build levels graph
        for level in self.levels:
            self.levels_graph.add_node(level)
            desc = self.levels[level]
            if 'contains' in desc:
                for sublevel in desc['contains']:
                    self.levels_graph.add_edge(level, sublevel)

        # check consistency
        if nx.is_arborescence(self.levels_graph):
            self.root_level = list(nx.topological_sort(self.levels_graph))[0]
        else:
            debuginfo('Warning, levels do not consitute an arborescence!')
            debuginfo(self.levels_graph.edges, self.levels_graph.nodes)

        # add default information if missing
        for level in self.levels:
            desc = self.levels[level]
            if 'module' not in desc:
                # try to build module from file
                if 'file' in desc:
                    path = Path(desc['file'])
                    desc['module'] = '.'.join(path.parent.parts + (path.stem,))
                    # if no class name build one ("DefaultLevelnameClass")
                    if 'class_name' not in desc:
                        desc['class_name'] = "Default{}Class".format(level.capitalize())
                else:
                    # if level built by aggregation use default level class
                    if 'aggregation_type' in desc:
                        desc['module'] = DEFAULT_LEVEL_INFO[desc['aggregation_type']]['level']['module']
                        desc['class_name'] = DEFAULT_LEVEL_INFO[desc['aggregation_type']]['level']['class_name']
                    else:
                        # try to retrieve upper level if any
                        predecessors = list(self.levels_graph.predecessors(level))
                        if not predecessors:
                            desc['module'] = DEFAULT_LEVEL_INFO['IBM']['sublevels']['module']
                            desc['class_name'] = DEFAULT_LEVEL_INFO['IBM']['sublevels']['class_name']
                        else: # take first information regarding aggregation type
                            ## TODO (research topic on multi-level
                            ## design patterns): hierarchize possibly
                            ## different aggregation types from upper
                            ## levels
                            for pred in predecessors:
                                desc_pred = self.levels[pred]
                                if not 'aggregation_type' in desc_pred:
                                    continue
                                pred_info = DEFAULT_LEVEL_INFO[desc_pred['aggregation_type']]
                                if 'sublevels' not in pred_info:
                                    continue
                                desc['module'] = pred_info['sublevels']['module']
                                desc['class_name'] = pred_info['sublevels']['class_name']
                            if 'module' not in desc:
                                desc['module'] = None
                                desc['class_name'] = None
            if 'default_prototype' in desc:
                self.default_prototypes[level] = desc['default_prototype']
            if 'aggregation_type' in desc:
                if not 'contains' in desc:
                    raise SemanticException('No sublevels defined for aggregation type {} at level {}'.format(desc['aggregation_type'], level))
                default = DEFAULT_LEVEL_INFO[desc['aggregation_type']]
                if 'super' not in desc:
                    desc['super'] = default['level']
                if not desc['module'].startswith('emulsion.agent'):
                    if 'sublevels' in default:
                        for sublevel in desc['contains']:
                            if ('module' not in self.levels[sublevel] or\
                                (not self.levels[sublevel]['module'].startswith('emulsion.agent')))\
                               and ('super' not in self.levels[sublevel]):
                                self.levels[sublevel]['super'] = default['sublevels']
                if 'aggregate_vars' in desc:
                    if desc['aggregation_type'] == AGGREG_COMP:
                        raise SemanticException('Compartment-based models cannot define aggregate variables')
                    if level not in self.aggregate_vars:
                        self.aggregate_vars[level] = []
                    for agg_desc in desc['aggregate_vars']:
                        newvar = agg_desc['name']
                        sourcevar = agg_desc['collect']
                        oper = agg_desc['operator'] if 'operator' in agg_desc else 'sum'
                        self.aggregate_vars[level].append((newvar, sourcevar, oper))

    def get_agent_class_for_level(self, level):
        return load_class(module=self.levels[level]['module'],
                          class_name=self.levels[level]['class_name'])

    def build_processes(self):
        """Parse the description of the model and retrieve the list of
        processes with different level.

        Example of YAML specification:
        ------------------------------
        processes:
          herd:
            - bacterial_dispersion
            - culling_process
            - infection
          metapop:
            - inbox_distribution
            - outbox_distribution
        """
        self.processes = self._description['processes'] if 'processes' in self._description else {}
        for level in self.levels:
            if level not in self.processes:
                self.processes[level] = []
        # if any compartment-based aggregation, add the most specific grouping as 'MASTER' in the groupings section
        for level in self.processes:
            if 'aggregation_type' in self.levels[level] and self.levels[level]['aggregation_type'] == AGGREG_COMP:
                if 'grouping' not in self._description:
                    self._description['grouping'] = {level: {} for level in self.levels}
                l_sublevels = self.levels[level]['contains']
                if len(l_sublevels) > 1:
                    raise SemanticException('Compartment-based models cannot aggregate several sublevels: main level {} vs. subevels {}'.format(level, l_sublevels))
                sublevel = l_sublevels[0]
                l_processes = []
                for process_name in self.processes[sublevel]:
                    if process_name in self.state_machines:
                        l_processes.append(process_name)
                self._description['grouping'][level]['MASTER'] = l_processes
                ## rewrite list of processes as a list {process_name: grouping}
                ## where grouping is set to None for processes defined in python add-ons
                self.processes[sublevel] = [{name: None}
                                            if name not in l_processes else {name: 'MASTER'}
                                            for name in self.processes[sublevel]]
        # create a dict to associate each state machine to the appropriate level
        self.statemachines_by_level = {level: [] for level in self.levels}
        for level, l_processes in self.processes.items():
            l_d_processes = []
            for process in l_processes:
                if isinstance(process, dict):
                    l_d_processes.append(process)
                    self.statemachines_by_level[level] += [process_name
                                                           for process_name in process
                                                           if process_name in self.state_machines]
                else:
                    l_d_processes.append({process: None})
                    if process in self.state_machines:
                        self.statemachines_by_level[level].append(process)
            self.processes[level] = l_d_processes

    def check_state_machines(self):
        """Rapidly inspect the name of state machines and of their states to
        pre-register automatically built statevars.

        """
        if 'state_machines' in self._description:
            for machine_name, description in self._description['state_machines'].items():
                self.state_machines[machine_name] = None # to build later

                prop_name = 'duration_in_{}'.format(machine_name)
                desc = "duration elapsed (time units) in current {} state".format(machine_name)
                # self._description['statevars'][prop_name] = {'desc': desc}
                self.statevars[prop_name] = {'desc': desc}
                self._description['statevars'][prop_name] = {'desc': desc}
                self._namespace[prop_name] = Symbol(prop_name)
                self._values[prop_name] = create_duration_getter(machine_name)

                prop_name = '_time_entered_{}'.format(machine_name)
                desc = "time step when agent entered current {} state".format(machine_name)
                self.statevars[prop_name] = {'desc': desc}
                self._description['statevars'][prop_name] = {'desc': desc}
                self._namespace[prop_name] = Symbol(prop_name)

                prop_name = '_time_to_exit_{}'.format(machine_name)
                desc = "time step after which agent is allowed to leave current {} state".format(machine_name)
                self.statevars[prop_name] = {'desc': desc}
                self._description['statevars'][prop_name] = {'desc': desc}
                self._namespace[prop_name] = Symbol(prop_name)

                desc = "Numeric value associated to current state of state machine {}".format(machine_name)
                prop_name = 'index_my_{}'.format(machine_name)
                self._description['statevars'][prop_name] = {'desc': desc}
                self.statevars[prop_name] = desc
                self._values[prop_name] = create_my_state_indexer(machine_name)
                self._namespace[prop_name] = Symbol(prop_name)

                for statedict in description['states']:
                    for state_name in statedict:
                        ## define "is_X"
                        desc = "Test if {} = {}".format(machine_name, state_name)
                        prop_name = 'is_{}'.format(state_name)
                        self._description['statevars'][prop_name] = {'desc': desc}
                        # self.statevars[prop_name] = desc
                        self._namespace[prop_name] = Symbol(prop_name)
                        self._values[prop_name] = create_state_tester(state_name)

                        ## same for "index_X"
                        desc = "Return numeric value of state {} in state machine {}".format(state_name, machine_name)
                        prop_name = 'index_{}'.format(state_name)
                        self._description['statevars'][prop_name] = {'desc': desc}
                        # self.statevars[prop_name] = desc
                        self._namespace[prop_name] = Symbol(prop_name)
                        self._values[prop_name] = create_state_indexer(state_name)
                        

    def build_state_machines(self):
        """Parse the description of the model and build all the
        required state machines.

        """
        if 'state_machines' in self._description:
            for machine_name, description in self._description['state_machines'].items():
                level_of_machine = None
                for level, l_machines in self.statemachines_by_level.items():
                    ## ASSUMING THAT A STATE MACHINE IS USED BY ONLY ONE LEVEL !!!
                    if machine_name in l_machines:
                        level_of_machine = level
                        break
                if level_of_machine is None:
                    raise SemanticException('Statemachine {} is associated with no level!'.format(machine_name))
                ## ASSUMING THAT EACH LEVEL HAS AT MOST UPPER LEVEL
                l_upper_levels = list(self.levels_graph.predecessors(level_of_machine))
                if any(l_upper_levels):
                    upper_level = l_upper_levels[0]
                    aggregation_type = self.levels[upper_level]['aggregation_type']
                else:
                    aggregation_type = 'hybrid'
                self.state_machines[machine_name] = StateMachine(machine_name, description, self, aggregation_type)

    def build_compartment_desc(self):
        """Inspect the `grouping` part of the model (if any) in order to store
        the corresponding information.

        """
        # create a graph for grouping nesting
        grouping_graphs = { level_name: nx.DiGraph() for level_name in self.levels }
        # susbtitution grouping -> most detailed sub-grouping
        self.substitution_dict = { level_name: {} for level_name in self.levels }
        self.compartments = self._description['grouping'] if 'grouping' in self._description else {}
        for level in self.levels:
            if level not in self.compartments:
                self.compartments[level] = {}
            if 'aggregation_type' in self.levels[level]:
                agg_type = self.levels[level]['aggregation_type']
                if len(self.compartments[level]) == 0:
                    continue
                for grouping_name, desc in self.compartments[level].items():
                    grouping_info = {'key_variables': desc, 'state_machines': []}
                    if agg_type in DEFAULT_GROUPING_INFO:

                    # raise SemanticException('Unsupported aggregation_type: {}'.format(agg_type))
                        default = DEFAULT_GROUPING_INFO[agg_type]
                        if 'compart_manager' not in grouping_info:
                            grouping_info['compart_manager'] = default['compart_manager'] if  'state_machines' in grouping_info else default['fallback_view']
                        if 'compart_class' not in grouping_info:
                            grouping_info['compart_class'] = default['compart_class']
                    self.compartments[level][grouping_name] = grouping_info

                ## identify nesting between groupings
                for grouping_name1 in self.compartments[level]:
                    grouping_graphs[level].add_node(grouping_name1)
                    for grouping_name2 in self.compartments[level]:
                        if grouping_name1 == grouping_name2:
                            continue
                        key1 = self.compartments[level][grouping_name1]['key_variables']
                        key2 = self.compartments[level][grouping_name2]['key_variables']
                        if set(key1) == set(key2):
                            raise SemanticException('Two groupings with same variables (not allowed): {} and {} (keep only one of them)'.format(grouping_name1, grouping_name2))
                        if set(key1) < set(key2):
                            grouping_graphs[level].add_edge(grouping_name1, grouping_name2)
        # compute substitution in groupings: e.g. if a grouping on var x and a grouping on variables x, y, z exist, the first one must be kept only to define total_X, but state machines must operate only on the grouping based on x, y, z
            leaf_groupings = [grouping_name for grouping_name in grouping_graphs[level].nodes() if grouping_graphs[level].out_degree(grouping_name)==0 and grouping_graphs[level].in_degree(grouping_name)>=1]
            self.substitution_dict[level] = {grouping_name: substitution for substitution in leaf_groupings for grouping_name in grouping_graphs[level].nodes() if grouping_name in nx.ancestors(grouping_graphs[level], substitution)}
        # rewrite grouping section to add relevant state machines
        for level in self.processes:
            for process in self.processes[level]:
                for process_name, grouping in process.items():
                    if grouping is not None:
                        ## add current process_name to state_machines in groupings
                        for upper_level in self.levels_graph.predecessors(level):
                            ## if any substitution, do it !
                            grouping_name = self.substitution_dict[upper_level][grouping] if grouping in self.substitution_dict[upper_level] else grouping
                            self.compartments[upper_level][grouping_name]['state_machines'].append(process_name)


    def get_sublevels(self, level_name):
        """Return the list of sublevels of the given *level_name*"""
        return list(self.levels_graph.successors(level_name))


    # def calculate_compound_params(self):
    #     """Inspect all edges of the health states graph and compute
    #     the actual probabilities associated to expressions.
    #     ### TODO: check that the ultimate symbols are declared properties.
    #
    #     """
    #     for cond, expr in self.conditions.items():
    #         self.conditions[cond] = self.expand_expression(expr)


    def add_expression(self, expression):
        """Add the specified expression to the dictionary of known
        expressions.

        """
        if expression not in self.parameters\
           and expression not in self.statevars\
           and expression not in self._expressions:
            self._expressions[expression] = self.expand_expression(expression)
        return expression

    def expand_expression(self, expression):
        """Transform the specified expression so as to replace all
        parameters by actual values or state variables or
        attributes.

        """
        ### WARNING: expand_expressions should iterate over all
        ### expressions at the same time (halting when no change
        ### occurs) instead of iterating over each expression one by
        ### one

        # experimental
        # if isinstance(expression, dict):
        #     return self.parse_if(expression)

        result = sympify(expression, locals=self._namespace)
        expr = result
        symbs = {s: self.parameters[s.name]
                 for s in expr.free_symbols
                 if s.name in self.parameters}
        while symbs:
            result = expr.subs(symbs)
            expr = sympify(result, locals=self._namespace)
            symbs = {s: self.parameters[s.name]
                     for s in expr.free_symbols
                     if s.name in self.parameters}
        return result

    # experimental
    def parse_dict(self, param_name, expression_dict):
        if 'if' in expression_dict:
            return self.parse_if(param_name, expression_dict)
        if 'or' in expression_dict:
            return self.parse_or(param_name, expression_dict)
        if 'and' in expression_dict:
            return self.parse_and(param_name, expression_dict)
        raise SemanticException('Unknown expression for parameter {}:\n\t{}'.format(param_name, expression_dict))

    # experimental
    def parse_if(self, param_name, expression_dict):
        if 'then' not in expression_dict:
            raise SemanticException('THEN clause missing in expression {}'.format(expression_dict))
        if 'else' not in expression_dict:
            raise SemanticException('ELSE clause missing in expression {}'.format(expression_dict))

        cond = expression_dict['if']
        if_true = expression_dict['then']
        if_false = expression_dict['else']

        if isinstance(cond, dict):
            val_cond = self.parse_dict(param_name, cond)
            self._values[str(cond)] = val_cond
        else:
            val_cond = self.add_expression(str(cond))

        if isinstance(if_true, dict):
            val_true = self.parse_dict(param_name, if_true)
            self._values[str(if_true)] = val_true
        else:
            val_true = self.add_expression(str(if_true))

        if isinstance(if_false, dict):
            val_false = self.parse_dict(param_name, if_false)
            self._values[str(if_false)] = val_false
        else:
            val_false = self.add_expression(str(if_false))

        return create_lazy_ternary(str(cond), str(if_true), str(if_false))

    # experimental
    def parse_or(self, param_name, expression_dict):
        l_conditions = expression_dict['or']
        if not isinstance(l_conditions, list):
            raise SemanticException('"or:" clause must be followed by a list, found instead: {}'.format(l_conditions))

        l_expressions = []
        for condition in l_conditions:
            if isinstance(condition, dict):
                val_cond = self.parse_dict(param_name, condition)
                self._values[str(condition)] = val_cond
                l_expressions.append(condition)
            else:
                val_cond = self.add_expression(str(condition))
                l_expressions.append(str(val_cond))

        return create_lazy_OR(l_expressions)

    # experimental
    def parse_and(self, param_name, expression_dict):
        l_conditions = expression_dict['and']
        if not isinstance(l_conditions, list):
            raise SemanticException('"and:" clause must be followed by a list, found instead: {}'.format(l_conditions))

        l_expressions = []
        for condition in l_conditions:
            if isinstance(condition, dict):
                val_cond = self.parse_dict(param_name, condition)
                self._values[str(condition)] = val_cond
                l_expressions.append(str(condition))
            else:
                val_cond = self.add_expression(str(condition))
                l_expressions.append(str(val_cond))

        return create_lazy_AND(l_expressions)


    def build_actions(self):
        """Parse the description of the model and extract the actions
        that agents must have.

        Example of YAML specification:
        ------------------------------
        actions:
          say_hello:
            desc: action performed when entering the S state

        """
        if 'actions' in self._description:
            self.actions = StateVarDict(self._description['actions'])

    def compute_values(self):
        """Check parameters and calculated compound parameters, so as
        to make them computable. In the case of parameters, number
        values are left unchanged, but strings (representing an
        expression) are replaced by a function. Regarding calculated
        compound parameters, expressions corresponding to numbers are
        converted to float values, while other expressions are
        replaced by a function.

        """
        # collect 'true' values in the parameters
        for (param, expression) in self.parameters.items():
            # # experimental
            # if isinstance(expression, dict):
            #     self._values[param] = create_lazy_ternary(expression['if'], expression['then'], expression['else'])
            #     continue
            value = self.expand_expression(expression)
            try:
                self._values[param] = float(value)
            except:
                self._values[param] = make_function(value, modules=self.modules)
        for (param, expression) in self._expressions.items():
            # # experimental
            # if isinstance(expression, dict):
            #     self._values[param] = create_lazy_ternary(expression['if'], expression['then'], expression['else'])
            #     continue
            value = self.expand_expression(expression)
            ## DO NOT REALLOCATE EXPRESSIONS ALREADY COMPUTED AS CALLABLE OBJECTS --- NOR STATEVARS !!!
            ## (introduced to support data-based parameters)
            if param in self._values and callable(self._values[param]):
                debuginfo(param, 'from EXPRESSIONS has value', self._values[param], 'instead of', value)
                continue
            if param in self.statevars:
                # debuginfo(param, 'already in STATEVARS')
                continue
            try:
                self._values[param] = float(value)
            except:
                self._values[param] = make_function(value, modules=self.modules)
        # for (cond, expression) in self.conditions.items():
        #     value = self.expand_expression(expression)
        #     if any([str(symb) in self.statevars
        #             for symb in expression.free_symbols]):
        #         self._values[cond] = make_function(value, dtype=bool, modules=self.modules)
        #     else:
        #         self._values[cond] = bool(value)
        for (statename, state) in self.states.items():
            self._values[statename] = state

    def get_modifiable_parameters(self):
        """Return a dictionary containing all true parameters with their
        value.

        """
        d_true_params =  {p: self.get_value(p)
                        for p in self.parameters
                        if not callable(self.get_value(p))}
        d_true_params['delta_t'] = self.delta_t
        return d_true_params

    def describe_parameter(self, name):
        """Return the description of the parameter with the specified
        name.

        """
        # pretty_name = pretty(sympify(name, locals=self._namespace))
        # param_name = name if pretty_name == name\
        #              else "{} ({})".format(pretty_name, name)
        param_name = name
        return "{} [parameter]:\n\t{: <72}\n\t{}".format(
            param_name,
            self._description['parameters'][name]['desc'],
            self._description['parameters'][name]['value']
        )

    def describe_variable(self, name):
        """Return the description of the statevar with the specified
        name.

        """
        # pretty_name = pretty(sympify(name, locals=self._namespace))
        # var_name = name if pretty_name == name\
        #            else "{} ({})".format(pretty_name, name)
        var_name = name
        return "{} [variable]:\n\t{: <72}".format(
            var_name,
            self._description['statevars'][name]['desc'],
        )

    def describe_name(self, name):
        """Return the description of the specified name in the model
        name.

        """
        if name in self._description['parameters']:
            return self.describe_parameter(name)
        elif name in self._description['statevars']:
            return self.describe_variable(name)
        else:
            return "{}: UNKNOWN NAME".format(name)

    def write_dot(self, parent_dir):
        """Write the graph of the each state machine in the
        specified directer name, according to the dot/graphviz format.

        """
        for name, statemachine in self.state_machines.items():
            name = self.model_name + '_' + name + '.dot'
            path = str(Path(parent_dir, name))
            statemachine.write_dot(path)

    def generate_skeleton(self, module):
        """Output a code skeleton to help writing specific pieces of code for
        the specified module to make the model work under Emulsion.

        """
        env = Environment(
            loader=PackageLoader('emulsion', 'templates'),
            extensions=['jinja2.ext.do']
        )
        template = env.get_template('specific_code.py')
        output = template.render(model=self, src_module=module)
        return output

EmulsionModel.get_modifiable_parameters.__USER_METHOD__ = ['Introspection']
EmulsionModel.describe_parameter.__USER_METHOD__ = ['Introspection']
