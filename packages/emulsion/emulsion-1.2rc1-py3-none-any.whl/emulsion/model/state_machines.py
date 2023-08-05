"""
.. module:: emulsion.model.state_machines

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


import sys
from   functools               import partial
from   collections             import Counter

import numpy                   as     np
from   sympy                   import sympify

from   sortedcontainers        import SortedSet

import pydot

import emulsion.tools.graph    as     enx
from   emulsion.agent.action   import AbstractAction
from   emulsion.tools.state    import StateVarDict, EmulsionEnum

from   emulsion.model.functions import AGGREG_COMP, ACTION_SYMBOL, WHEN_SYMBOL, ESCAPE_SYMBOL,\
    COND_SYMBOL, CROSS_SYMBOL, EDGE_KEYWORDS, CLOCK_SYMBOL,\
    make_when_condition, make_duration_condition, make_duration_init_action

from   emulsion.model.exceptions     import SemanticException
from   emulsion.tools.debug          import debuginfo


#   _____ _        _       __  __            _     _
#  / ____| |      | |     |  \/  |          | |   (_)
# | (___ | |_ __ _| |_ ___| \  / | __ _  ___| |__  _ _ __   ___
#  \___ \| __/ _` | __/ _ \ |\/| |/ _` |/ __| '_ \| | '_ \ / _ \
#  ____) | || (_| | ||  __/ |  | | (_| | (__| | | | | | | |  __/
# |_____/ \__\__,_|\__\___|_|  |_|\__,_|\___|_| |_|_|_| |_|\___|



class StateMachine(object):
    """Class in charge of the description of biological or economical
    processes, modeled as Finite State Machines. The formalism
    implemented here is based on UML state machine diagrams, with
    adaptations to biology.

    """
    def __init__(self, machine_name, description, model, aggregation_type):
        """Build a State Machine within the specified model, based on
        the specified description (dictionary).

        Parameters
        ----------
            machine_name: str
                name of the state machine
            description: dict
                dictionary corresponding to the YAML description of the state machine
            model: EmulsionModel
                the EMULSION model which the state machine belongs to
            aggregation_type: str
                type of aggregation (IBM, hybrid...) between the level
                at which this state machine will be executed and the
                upper level - necessary to handle durations properly

        """
        self.model = model
        self.machine_name = machine_name
        self.aggregation_type = aggregation_type
        self.parse(description)

    def _reset_all(self):
        self._statedesc = {}
        self._description = {}
        self.states = None
        self.graph = enx.MultiDiGraph()
        self.stateprops = StateVarDict()
        self.state_actions = {}
#        self.edge_actions = {}

    def parse(self, description):
        """Build the State Machine from the specified dictionary
        (expected to come from a YAML configuration file).

        """
        self._reset_all()
        # keep an exhaustive description
        self._description = description
        # build the enumeration of the states
        self.build_states()
        # build the graph based on the states and the transitions between them
        self.build_graph()
        # build actions associated with the state machine (states or edges)
        self.build_actions()

    def get_property(self, state_name, property_name):
        """Return the property associated to the specified state."""
        if state_name not in self.stateprops or\
           property_name not in self.stateprops[state_name]:
            return self.graph.node[state_name][property_name]\
                if property_name in self.graph.node[state_name]\
                   else None
        return self.stateprops[state_name][property_name]

    def build_states(self):
        """Parse the description of the state machine and extract the existing
        states. States are described as list items, endowed with
        key-value properties. Only one state per list item is allowed
        (to ensure that states are always stored in the same order in
        all executions).

        """
        states = []
        default_state = None
        # retrieve information for each state
        for statedict in self._description['states']:
            for name, value in statedict.items():
                states.append(name)
                # provide a default fillcolor
                if 'fillcolor' not in value:
                    value['fillcolor'] = 'lightgray'
                # provide a default dashed
                if 'line_style' not in value:
                    value['line_style'] = 'solid'
                # if properties are provided, add the corresponding
                # expression to the model
                if 'properties' not in value:
                    value['properties'] = {}
                # store special property: "autoremove: yes"
                value['properties']['autoremove'] = value['autoremove']\
                                                    if 'autoremove' in value else False
                # store special property: "default: yes"
                # if several states are marked "default", take the first one
                value['properties']['default'] = False
                if ('default' in value) and (value['default']) and (default_state is None):
                    value['properties']['default'] = True
                    default_state = name
                self.stateprops[name] = {k: self.model.add_expression(v)
                                         for k, v in value['properties'].items()}
                # store special properties: "next: aState" and
                # "previous: aState" which define
                # successor/predecessor when using "next_state" and
                # "previous_state" in prototype definition (otherwise,
                # next and previous are defined as non-autoremove
                # states after and before in the list)
                if 'next' in value:
                    value['properties']['next'] = value['next']
                    self.stateprops[name]['next'] = value['next']
                if 'previous' in value:
                    value['properties']['previous'] = value['previous']
                    self.stateprops[name]['previous'] = value['previous']
                # store other information
                self._statedesc[name] = value
                # and retrieve available actions if any
                for keyword in ['on_enter', 'on_stay', 'on_exit']:
                    if keyword in value:
                        self._add_state_actions(name, keyword, value[keyword])
        # build the enumeration of the states
        self.states = EmulsionEnum(self.machine_name.capitalize(),
                                   states, module=__name__)
        setattr(sys.modules[__name__], self.states.__name__, self.states)
        # link the states to their state machine
        self.states.state_machine = self
        # define the default value for "autoremove" at the enumeration level
        self.states.autoremove = False

        for state in self.states:
            # check that state names are unique
            if state.name in self.model.states:
                other_machine = self.model.states[state.name].__class__.__name__
                raise SemanticException(
                    'Conflict: State %s found in statemachines %s and %s' %
                    (state.name, other_machine, state.__class__.__name__))
            # check that state names are not parameters
            if state.name in self.model.parameters:
                raise SemanticException(
                    'Conflict: State %s of statemachines %s found in parameters'
                    % (state.name, state.__class__.__name__))
            # associate the state with the state name in the model
            self.model.states[state.name] = state
            # update the autoremove value if the state is defined as such
            if self.stateprops[state.name]['autoremove']:
                state.autoremove = True
            # set next and previous to the state itself (to ensure
            # that all states have a predecessor/successor)
            state.predecessor = state
            state.successor = state

        # handle default states
        self.states.is_default = False
        # if a default state is defined, store it and limit the list
        # of "available" states
        if default_state is not None:
            self.states[default_state].is_default = True
            self.states.default = self.states[default_state]
            self.states.available = (self.states.default,)
        else:
        # otherwise the list of available states is simply those which
        # are not autoremove
            self.states.default = None
            self.states.available = tuple(s for s in self.states if not s.autoremove)

        # define "successor" and "predecessor" properties
        # start from the list of non-autoremove states
        usable = [s for s in self.states if not s.autoremove]
        for state in usable:
            # if the state has a "predecessor" state, use it
            if 'previous' in self.stateprops[state.name]:
                state.predecessor = self.states[self.stateprops[state.name]['previous']]
            else:
                # otherwise use the previous state in the list, the
                # first one being its own previous state
                state.predecessor = usable[max(0, usable.index(state) - 1)]
            # if the state has a "successor" state, use it
            if 'next' in self.stateprops[state.name]:
                state.successor = self.states[self.stateprops[state.name]['next']]
            else:
                # otherwise use the next state in the list, the
                # last one being its own next state
                state.successor = usable[min(len(usable)-1, usable.index(state) + 1)]

        # define function used from model to provide a random state
        self.model._values['_random_' + self.machine_name] = self.get_random_state
        # define function used from model to provide the default state
        # if any, otherwise a random state among non-autoremove ones
        if self.states.default:
            self.model._values['_default_' + self.machine_name] = self.get_default_state
        else:
            self.model._values['_default_' + self.machine_name] = self.get_random_state


    def get_random_state(self, caller=None, qty=None):
        """Return a random state for this state machine."""
        l_available_states = [state for state in self.states if not state.autoremove]
        if qty is None:
            return np.random.choice(l_available_states)
        else:
            return Counter(np.random.choice(l_available_states, qty))

    def get_default_state(self, caller=None, qty=None):
        """Return the default state for this state machine."""
        return self.states.default if qty is None else {self.states.default: qty}

    @property
    def state_colors(self):
        """Return a dictionary of state names associated with fill colors."""
        return {state.name: self._statedesc[state.name]['fillcolor']
                for state in self.states
                if not state.autoremove}

    @property
    def state_style(self):
        """Return a dictionary of state names associated with dashed state."""
        return {state.name: self._statedesc[state.name]['line_style']
                for state in self.states
                if not state.autoremove}


    def build_graph(self):
        """Parse the description of the state machine and extract the
        graph of the transitions between the states. Since a
        MultiDiGraph is used, each pair of nodes can be bound by
        several transitions if needed (beware the associated
        semantics).

        Example of YAML specification:
        ------------------------------
        transitions:
          - {from: S, to: I-, proba: p, cond: not_vaccinated}
          - {from: I-, to: S, proba: m}
          - {from: I-, to: I+m, proba: 'q*plp'}
          - {from: I-, to: I+, proba: 'q*(1-plp)'}

        """
        # add a node for each state
        for state in self.states:
            name = state.name
            self._statedesc[name]['tooltip'] = self.describe_state(name)
            self.graph.add_node(name, **self._statedesc[name])
        # build edges between states according to specified transitions
        if 'transitions' in self._description:
            self._parse_edges(self._description['transitions'],
                              type_id=enx.EdgeTypes.TRANSITION)
        if 'productions' in self._description:
            self._parse_edges(self._description['productions'],
                              type_id=enx.EdgeTypes.PRODUCTION)

    def _parse_edges(self, edges, type_id=enx.EdgeTypes.TRANSITION):
        """Parse the description of edges, with the difference
        transitions/productions

        """
        for edge in edges:
            from_ = edge['from']
            to_ = edge['to']
            others = {k: v for (k, v) in edge.items()
                      if k != 'from' and k != 'to'}
            for kwd in EDGE_KEYWORDS:
                if kwd in others:
                    # parm = pretty(sympify(others[kwd], locals=self.model._namespace))
                    parm = others[kwd]
                    label = '{}: {}'.format(kwd, parm)
            # label = ', '.join([pretty(sympify(x, locals=self.model._namespace))
            #                    for x in others.values()])
                    if str(parm) in self.model.parameters:
                        others['labeltooltip'] = self.model.describe_parameter(parm)
                    else:
                        others['labeltooltip'] = label
            # others['labeltooltip'] = ', '.join([self.model.describe_parameter(x)
            #                                     for x in others.values()
            #                                     if str(x) in self.model.parameters])
            # handle conditions if any on the edge
            cond, esc_cond = None, None
            if 'cond' in others:
                cond = others['cond']
                others['truecond'] = others['cond']
            if ('escape' in others) and (type_id == enx.EdgeTypes.TRANSITION):
                esc_cond = others['escape']
            if cond is not None:
                ### WARNING the operation below is not completely
                ### safe... it is done to replace conditions of the form
                ### 'x == y' by 'Eq(x, y)', but it is a simple
                ### substitution instead of parsing the syntax
                ### tree... Thus it is *highly* recommended to express
                ### conditions directly with Eq(x, y)
                if '==' in str(cond):
                    cond = 'Eq({})'.format(','.join(cond.split('==')))
                    # others['label'] = ', '.join(others.values())
            if esc_cond is not None:
                if '==' in str(esc_cond):
                    esc_cond = 'Eq({})'.format(','.join(esc_cond.split('==')))
            # if duration specified for this state, handle it as an
            # additional condition
            if ('duration' in self._statedesc[from_]) and (type_id == enx.EdgeTypes.TRANSITION):
                if self.aggregation_type != AGGREG_COMP:
                    ## build condition for testing time spent by individuals in the state
                    # duration_cond: _time_to_exit_statemachine >= step
                    duration_cond = make_duration_condition(self.model, self.machine_name)
                    if esc_cond is not None:
                        # escape conditions allow to exit state before _time_to_exit_statemachine
                        # => _time_to_exit_statemachine < step AND escape condition fulfilled
                        exit_cond = 'AND(Not({}),{})'.format(duration_cond, esc_cond)
                    else:
                        # without escape condition, use duration condition as a basis to allow to leave the state
                        exit_cond = duration_cond
                    if cond is None:
                        cond = exit_cond
                    else:
                        # if true conditions are specified, add them to the conjunction
                        cond = 'AND({},{})'.format(exit_cond, cond)
                    others['cond'] = cond
                else:
                    # in compartment-based models, escape conditions are allowed but 'cond' are not
                    if 'cond' in others:
                        raise SemanticException('In transition from {} to {}, individual conditions ({}) are not allowed (compartmental model !)'.format(from_, to_, others['cond']))
                    if esc_cond is not None:
                        others['escape'] = esc_cond
                        self.model._expressions[esc_cond] = sympify(esc_cond, locals=self.model._namespace)

            if cond is not None:
                self.model._expressions[cond] = sympify(cond,
                                                      locals=self.model._namespace)
            # handle 'when' clause if any on the edge
            self._parse_when(others)
            # # handle 'duration', 'escape' and 'condition' clauses if
            # # any on the edge
            # parse actions on cross if any
            if ('on_cross' in others) and (type_id == enx.EdgeTypes.TRANSITION):
                l_actions = self._parse_action_list(others['on_cross'])
                others['actions'] = l_actions
            others['label'] = label
            others['type_id'] = type_id
            self.graph.add_edge(from_, to_, **others)
            # register rate/proba/amount expressions in the model
            for keyword in EDGE_KEYWORDS:
                if keyword in others:
                    self.model.add_expression(others[keyword])


    def _parse_when(self, edge_desc):
        """Parse the edge description in search for a 'when'
        clause. This special condition is aimed at globally assessing
        a time period within the whole simulation.

        """
        if 'when' in edge_desc:
            expression = sympify(edge_desc['when'],
                                 locals=self.model._event_namespace)
            edge_desc['when'] = str(expression)
            self.model._values[str(expression)] = make_when_condition(
                expression, modules=self.model.modules)


    def build_actions(self):
        """Parse the description of the state machine and extract the
        actions that agents running this state machine must have.

        Example of YAML specification:
        ------------------------------
        actions:
          say_hello:
            desc: action performed when entering the S state

        """
        for name, value in self._statedesc.items():
            for keyword in ['on_enter', 'on_stay', 'on_exit']:
                if keyword in value:
                    self._add_state_actions(name, keyword, value[keyword])
            if 'duration' in value:
                val = value['duration']
                self._add_state_duration_actions(name, val)

    def get_value(self, name):
        """Return the value associated with the specified name."""
        return self.model.get_value(name)


    def _add_state_duration_actions(self, state_name, duration_value):
        """Add implicit actions to manage stay duration in the specified state
        name. The `duration_value` can be either a parameter, a
        'statevar' or a distribution.

        """
        # initialize the actions associated to the state if none
        if state_name not in self.state_actions:
            self.state_actions[state_name] = {}
        # retrieve the list of actions on enter for this state, if any
        lenter = self.state_actions[state_name]['on_enter']\
                   if 'on_enter' in self.state_actions[state_name] else []
        if self.aggregation_type == AGGREG_COMP:
            init_action = AbstractAction.build_action('sample_durations', state_machine=self, duration=self.model.add_expression(duration_value))
        else:
            # build a partial function based on the current state machine name
            enter_action = partial(make_duration_init_action,
                                   machine_name=self.machine_name)
            # set the name of the action
            enter_action.__name__ = 'init_duration'
            # set the action parameters (the expression associated to the duration)
            enter_params = [self.model.add_expression(duration_value)]
            # instantiate the action
            init_action = AbstractAction.build_action('duration',
                                                      function=enter_action,
                                                      l_params=enter_params,
                                                      state_machine=self)
        # and insert it at the beginning of the list of actions
        lenter.insert(0, init_action)
        self.model.add_init_action(self.machine_name,
                                   self.states[state_name],
                                   init_action)
        # lstay = self.state_actions[name]['on_stay']\
        #           if 'on_stay' in self.state_actions[name] else []
        # stay_action = partial(make_TTL_increase_action,
        #                       machine_name=self.machine_name)
        # stay_action.__name__ = '+_time_spent'
        # lstay.insert(0, AbstractAction.build_action('duration',
        #                                             function=stay_action,
        #                                             state_machine=self))
        self.state_actions[state_name]['on_enter'] = lenter
        # self.state_actions[name]['on_stay'] = lstay

    def _add_state_actions(self, name, event, actions):
        """Add the specified actions for the state with the given
        name, associated with the event (e.g. 'on_stay', 'on_enter',
        'on_exit'). Expressions contained in the parameters lists or
        dicts are automatically expanded.

        """
        if name not in self.state_actions:
            self.state_actions[name] = {}
        l_actions = self._parse_action_list(actions)
        self.state_actions[name][event] = l_actions

    def _parse_action_list(self, actions):
        """Parse the list of actions associated with a state."""
        l_actions = []
        for d_action in actions:
            if 'action' in d_action:
                action = d_action['action']
                l_params = [self.model.add_expression(expr)
                            for expr in d_action['l_params']]\
                                if 'l_params' in d_action\
                                else []
                d_params = {key: self.model.add_expression(expr)
                            for key, expr in d_action['d_params'].items()}\
                                if 'd_params' in d_action\
                                else {}
                l_actions.append(
                    AbstractAction.build_action('action',
                                                method=action,
                                                l_params=l_params,
                                                d_params=d_params,
                                                state_machine=self))
            else: #TODO: dispatch through AbstractAction (factory),
                  #make subclasses responsible for parameter parsing
                understood = False
                for keyword in ['increase', 'decrease',
                                'increase_stoch', 'decrease_stoch']:
                    if keyword in d_action:
                        # assume that increase statevar with rate
                        l_actions.append(
                            AbstractAction.build_action(
                                keyword,
                                statevar_name=d_action[keyword],
                                parameter=self.model.add_expression(d_action['rate']),
                                delta_t=self.model.delta_t,
                                state_machine=self
                            )
                        )
                        understood = True
                for keyword in ['set_var', 'set_upper_var']:
                    if keyword in d_action:
                        # assume that increase statevar with rate
                        l_actions.append(
                            AbstractAction.build_action(
                                keyword,
                                statevar_name=d_action[keyword],
                                parameter=self.model.add_expression(d_action['value']),
                                model=self.model
                            )
                        )
                        understood = True
                for keyword in ['become', 'clone', 'produce_offspring']:
                    if keyword in d_action:
                        amount = d_action['amount'] if 'amount' in d_action else None
                        probas = d_action['proba'] if 'proba' in d_action else None
                        l_actions.append(
                            AbstractAction.build_action(
                                keyword,
                                prototypes=d_action[keyword],
                                amount = amount,
                                probas = probas,
                                model = self.model
                            )
                        )
                        understood = True
                for keyword in ['log_vars']:
                    if keyword in d_action:
                        vars = [self.model.add_expression(varname)
                                for varname in d_action[keyword]]
                        l_actions.append(
                            AbstractAction.build_action(
                                keyword,
                                parameter=None,
                                l_params=vars
                            )
                        )
                        understood = True
                for keyword in ['message', 'record_change']:
                    if keyword in d_action:
                        l_actions.append(
                            AbstractAction.build_action(
                                keyword,
                                parameter=d_action[keyword]
                            )
                        )
                        understood = True
                if not understood:
                    raise SemanticException('ERROR !!!! action {} not understood'.format(d_action))
        return l_actions




    #----------------------------------------------------------------
    # Output facilities

    def describe_state(self, name):
        """Return the description of the state with the specified
        name.

        """
        desc = self._statedesc[name]
        return "{} ({}):\n\t{}".format(name, desc['name'], desc['desc'])

    def write_dot(self, filename, view_actions=True):
        """Write the graph of the current state machine in the
        specified filename, according to the dot/graphviz format.

        """

        dot_graph = pydot.Dot(self.machine_name, graph_type="digraph", rankdir="LR" if self.graph.edges() else "TB", charset="utf-8")
        dot_graph.set_node_defaults(fontsize=16, fontname="Arial", shape="box", style='"filled,rounded"')
        dot_graph.set_edge_defaults(minlen=1.5, penwidth=1.5, tailtooltip="", headtooltip="")

        for state in self.states:
            name = state.name
            name_lab = name
            if 'duration' in self._statedesc[name]:
                name_lab += '&nbsp;{}'.format(CLOCK_SYMBOL)
            shape = "Mrecord"
            label = name_lab
            nodestyle = "filled,rounded"
            if state.is_default:
                nodestyle += ",bold"
            if state.autoremove:
                nodestyle += ",dotted"
            if view_actions:
                onenter = ACTION_SYMBOL+'|'\
                          if 'on_enter' in self._statedesc[name] else ''
                onstay = '|'+ACTION_SYMBOL\
                         if 'on_stay' in self._statedesc[name] else ''
                onexit = '|'+ACTION_SYMBOL\
                         if 'on_exit' in self._statedesc[name] else ''
                if onenter or onstay or onexit:
                    label = "{%s{\ %s\ %s}%s}" % (onenter, name_lab, onstay, onexit)
            new_node = pydot.Node(name=str(name), shape=shape, label=str(label), tooltip=str(self._statedesc[name]['tooltip']), fillcolor=str(self._statedesc[name]['fillcolor']), style=f'"{nodestyle}"')
            dot_graph.add_node(new_node)
        for from_, to_ in SortedSet(self.graph.edges()):
            for desc in self.graph.edge[from_][to_].values():
                edgetip = ''
                tail = 'none'
                if 'when' in desc:
                    tail += WHEN_SYMBOL
                    edgetip += 'WHEN: {}'.format(desc['when'])
                if 'escape' in desc:
                    tail += ESCAPE_SYMBOL
                    edgetip += 'ESCAPE: {}'.format(desc['escape'])
                if 'truecond' in desc:
                    tail += COND_SYMBOL
                    edgetip += 'COND: {}'.format(desc['truecond'])
                head = 'normalnone'
                if 'on_cross' in desc:
                    head += CROSS_SYMBOL
                    # edgetip += 'ON CROSS: {}\\n'.format(desc['on_cross'])
                new_edge = pydot.Edge(src=str(from_), dst=str(to_), label=str(desc['label']), labeltooltip=str(desc['labeltooltip']), arrowtail=str(tail), arrowhead=str(head), dir="both", tooltip=str(edgetip), minlen=3, style=str(desc['type_id'].linestyle))
                dot_graph.add_edge(new_edge)
        dot_graph.write_raw(filename)
