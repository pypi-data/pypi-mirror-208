"""Usage:
    emulsion run [--plot] MODEL [options] [(-p KEY=VALUE)...]
    emulsion show MODEL [options] [(-p KEY=VALUE)...]
    emulsion describe MODEL PARAM...
    emulsion diagrams MODEL [options]
    emulsion plot MODEL [options]
    emulsion check MODEL [options]
    emulsion generate MODEL
    emulsion (-h | --help | -V | --version | -L | --license)

Commands:
  run MODEL                   Run simulations based on the specified MODEL
                              (MODEL is the path to the YAML file describing the
                              model to run).
  show MODEL                  Print all MODEL parameter values and exit.
  describe MODEL PARAM...     Describe the role of specified PARAMeters in the
                              MODEL and exit.
  diagrams MODEL              Produce model diagrams (as option --view-model
                              when running/plotting) and open them
  plot MODEL                  Plot outputs for MODEL (assumed already run) and
                              exit.
  generate MODEL              Generate a skeleton to help writing specific
                              pieces of code before the MODEL can be run, and
                              exit.

Options:
  -h --help                   Display this page and exit.
  -V --version                Display version number and exit.
  -L --license                Display license and exit.
  --plot                      Plot outputs just after running the model.
  -r RUNS --runs RUNS         Specify the number of repetitions of the same
                              model [default: 10].
  -t STEPS --time STEPS       Specify the number of time steps to run in each
                              repetition. If the model defines a total_duration,
                              it is used as time limit, unless the '-t' option
                              is explicitly specified. Otherwise, the default
                              value is 100 steps.
  -p KEY=VAL --param KEY=VAL  Change parameter named KEY to the specified VALue.
  --view-model                Produce diagrams to represent the state machines
                              of the model (requires Graphviz). Figures are
                              stored in figure-dir.
  --silent                    Show only the progression of repetitions instead
                              of the progression of each simulation.
  --quiet                     Show no progression information at all.
  --no-count                  Disable the production of file counts.csv (hence
                              accelerates simulation)
  --save FILE                 Save simulation state (all agents state and
                              parameters) at the end of the simulation.
  --load FILE                 Use a saved simulation to start the current one.
  --output-dir OUTPUT         Specify a directory for simulation outputs
                              [default: outputs].
  --input-dir INPUT           Specify a directory for simulation inputs
                              [default: data].
  --figure-dir FIG            Specify a directory for graphic outputs (figures)
                              [default: img].
  --code-path CODE            Specify a path for Python add-ons [default: .].
  --log-params                When producing CSV outputs, insert the name and
                              value of each parameter explicitly changed by
                              option -p/--param. (DEPRECATED)
  --format FORMAT             Specify an image format for diagram outputs (svg,
                              pdf, png, jpg) [default: svg].
  --table-params              Display a table of the parameters and initial
                              conditions.
  --aggregate                 Together with --plot, force the aggregation of
                              runs to display median, min-max and 10-90
                              percentiles instead of the detail of each run.
                              This is the default behaviour for 20 runs or more.
  --detail                    Together with --plot, force the display of each
                              run (default for less than 20 runs).

Advanced options:
  --seed SEED                 Set a seed value for random numbers. When not
                              specified, the seed is set according to system
                              time and the process id.
  --show-seed                 Print the seed used for random numbers.
  --start-id ID               ID of the first repetition of the same model
                              [default: 0].
  --echo                      Just print command-line arguments parsed by Python
                              docopt module and exit.
  --deterministic             Run the simulation in deterministic mode if
                              available.
  --modifiable                Output the list of modifiable parameters and exit.
  --level LEVEL               Specify the LEVEL (scale) for running the model.
                              Valid values are those defined in the 'level'
                              section of the MODEL. The corresponding agent
                              class will be used to manage the simulation of
                              lower-level entities. When no value is given, the
                              highest level (if any) is used.


EMULSION (Epidemiological Multi-Level Simulation framework)
===========================================================

Contributors and contact:
-------------------------

    - Sébastien Picault (sebastien.picault@inrae.fr)
    - Yu-Lin Huang
    - Vianney Sicard
    - Sandie Arnoux
    - Gaël Beaunée
    - Pauline Ezanno (pauline.ezanno@inrae.fr)

    INRAE, Oniris, BIOEPAR, 44300, Nantes, France


How to cite:
------------

    S. Picault, Y.-L. Huang, V. Sicard, S. Arnoux, G. Beaunée,
    P. Ezanno (2019). "EMULSION: Transparent and flexible multiscale
    stochastic models in human, animal and plant epidemiology", PLoS
    Computational Biology 15(9): e1007342. DOI:
    10.1371/journal.pcbi.1007342


License:
--------

    Copyright 2016 INRAE and Univ. Lille

    Inter Deposit Digital Number: IDDN.FR.001.280043.000.R.P.2018.000.10000

    Agence pour la Protection des Programmes,
    54 rue de Paradis, 75010 Paris, France

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""

## TO BE IMPLEMENTED LATER:

  #   emulsion sensitivity MODEL DESIGN [options]
  #   emulsion change MODEL NEW_MODEL (-p KEY=VALUE)...


  # sensitivity MODEL DESIGN    Run a sensitivity analysis for the specified MODEL
  #                             using the provided experimental DESIGN.
  #                             NOT IMPLEMENTED YET.
  # change MODEL NEW_MODEL      Modify the initial MODEL into a NEW_MODEL using
  #                             appropriate options, and exit. NOT IMPLEMENTED YET

  # --init INIT_FILE            Speficy a file for initial conditions.
  #                             NOT USED YET.
  # --test                      Run the simulation in test mode. NOT USED YET.
  # --metamodel META            Specify a metamodel for syntax checking
  #                             [default: ../../scripts/emulsion.tx]


import sys
import os
import time
import datetime                     as dt
import webbrowser

from   pathlib                      import Path

import yaml
import numpy                        as np

from   docopt                       import docopt
import colorama
import pydot

import emulsion
from   emulsion.model.emulsion_model import EmulsionModel
from   emulsion.tools.state         import StateVarDict
from   emulsion.tools.misc          import load_class
from   emulsion.tools.plot          import plot_outputs
from   emulsion.tools.simulation    import MultiSimulation

VERSION = '1.2rc1'
DEFAULT_VERSION = "1.2"
LICENSE = 'Apache-2.0'
DEFAULT_LICENSE = "Apache-2.0"

def get_metamodel():
    """Return the path to the metamodel used for checking syntax of
    EMULSION YAML files.

    """
    # retrieve path to EMULSION repository
    parts = Path(emulsion.__file__).parts[:-1] + ("resources", "emulsion.tx")
    return Path(*parts)

def get_version():
    """Retrieve the version number of current program.

    """
    # try:
    #     proc = subprocess.Popen(["git", "describe",
    #                              "--tags", "--dirty", "--always"],
    #                             stdout=subprocess.PIPE)
    # except EnvironmentError:
    #     print("unable to run git")
    #     return 'Unknown'
    # stdout = proc.communicate()[0].strip().decode('utf-8')
    # if proc.returncode != 0:
    #     print("unable to run git")
    #     return DEFAULT_VERSION
    # return stdout
    return DEFAULT_VERSION if VERSION.startswith('[') else VERSION

def get_license():
    """Retrieve the license  of current program.

    """
    return DEFAULT_LICENSE if LICENSE.startswith('[') else LICENSE

def change_parameters(d_params, l_changes):
    """Change either the model or local parameters according to the list
    of new values. First, check that all parameter changes are enabled, then
    reparse the model with new values.

    Parameters
    ----------
    d_params: StateVarDict
        the dictionary built from command-line options
    l_changes: list
        the list of all parameter changes parsed from '-p' or '--param' command-line options
    """
    d_model_changes = {}
    d_modifiable = d_params.model.get_modifiable_parameters()
    for key, val in [p.split('=') for p in l_changes]:
        if key in d_params:
            # if the new value is the name of another parameter,
            # retrieve its current value
            if val in d_params:
                val = d_params[val]
            # retrieve the value with correct type
            d_params[key] = type(d_params[key])(val)
        elif key in d_modifiable:
            d_model_changes[key] = val
        else:
            print(colorama.Fore.RED + colorama.Style.BRIGHT + 'Unknown parameter:{}'.format(key) + colorama.Style.RESET_ALL)
            sys.exit(-1)
    if any(d_model_changes):
        d_params.model = EmulsionModel(filename=d_params.filename, input_dir=d_params.input_dir, changed_values=d_model_changes)

def describe_parameters(params):
    """Display the role of all parameters specified in the PARAM argument
    and exit.

    """
    model = params.model
    print(colorama.Style.BRIGHT + '\n{!s: ^72}'.format(params.model))
    print('{: ^72}'.format('ROLE OF PARAMETERS (AND CURRENT DEFINITION)') + colorama.Style.RESET_ALL)
    print('-'*72)
    for name in params.to_describe:
        print(model.describe_name(name))
    print('-'*72)


def show_parameters(params, short=False):
    """Display all parameters involved in the current program and model
    and exit.

    """
    modifiable = params.model.get_modifiable_parameters()
    if short:
        print(' '.join('{}={}'.format(key, params.model.get_value(key))
                       for key in modifiable))
        sys.exit()
    print(colorama.Style.BRIGHT + '\n{!s: ^72}'.format(params.model))
    print('{: ^72}'.format('AVAILABLE PARAMETERS (with their current value)'))
    print('-'*72)
    print('MODEL PARAMETERS')
    print('-'*72 + colorama.Style.RESET_ALL)
    for key, val in modifiable.items():
        print('  {:.<34}{!s:.>34}'.format(key, val))
    print('-'*72)
    # print('PROGRAM PARAMETERS')
    # print('-'*72)
    # for key, val in params.items():
    #     print('  {:.<34}{!s:.>34}'.format(key, val))
    sys.exit()


def generate_model(params):
    """Generate a skeleton for the pieces of specific code to write. If
    needed, create subdirectories. If files already exist, add a timestamp
    to the filename.

    """
    model = params.model
    src_path = Path(__file__).parent.parent
    paths = sorted(set([Path(level_desc['file'])
                        for level_desc in model.levels.values()
                        if 'file' in level_desc
                        # if not level_desc['module'].startswith('emulsion.agent')
    ]))
    for mod_path in paths:
        # mod_path = Path(src_path, *module.split('.')).with_suffix('.py')
        module = '.'.join(mod_path.parent.parts + (mod_path.stem,))
        if mod_path.exists():
            print(colorama.Fore.YELLOW, 'WARNING, file {} already exists, '.format(mod_path))
            mod_path = mod_path.with_suffix('.py.%s' %
                                            (dt.datetime.now().timestamp()))
            print('Writing in {} instead'.format(mod_path) + colorama.Style.RESET_ALL)
        mod_path.parent.mkdir(parents=True, exist_ok=True)
        print(colorama.Fore.GREEN + colorama.Style.BRIGHT + 'GENERATING CODE SKELETON {}\nFOR MODULE {}'.format(mod_path, module) + colorama.Style.RESET_ALL)
        with open(mod_path, 'w') as f:
            print(model.generate_skeleton(module), file=f)


def run_model(params):
    """Run the model with the specified local parameters.

    Args:
        params: a dictionary with all parameters required to carry out the
          simulations

    Returns:
        The instance of MultiSimulation class which carried out the simulations

    See also:
        `emulsion.tools.simulation.MultiSimulation`_
    """
    count_path = Path(params.output_dir, 'counts.csv')
    if count_path.exists():
        count_path.unlink()
    log_path = Path(params.output_dir, 'log.txt')
    if log_path.exists():
        log_path.unlink()
    multi_simu = MultiSimulation(**params)
    # multi_simu.write_dot()
    start = time.perf_counter()
    multi_simu.run()
    end = time.perf_counter()
    print(colorama.Style.BRIGHT + 'Simulation finished in {:.2f} s'.format(end-start))
    if not params.nocount:
        print(colorama.Fore.GREEN + 'Outputs stored in {}'.format(count_path) + colorama.Style.RESET_ALL)
    return multi_simu


def produce_diagrams(params, view=False):
    """Use Graphviz to render state machines of the model. If *view* is
    set to True, opens the diagrams with system viewer.

    Args:
        params: a dictionary with all parameters required to carry out the
          simulations
        view: a boolean indicating whether or not diagrams have to be opened
          directly

    """
    model = params.model
    model.write_dot(params.output_dir)
    prefix = model.model_name
    for name, _ in model.state_machines.items():
        inpath = Path(params.output_dir, prefix + '_' + name + '.dot')
        outpath = Path(params.figure_dir,
                       prefix + '_' + name + '_machine.' + params.img_format)

        dot_graph = pydot.graph_from_dot_file(inpath)[0]
        ## bug when reading file (node named "\n" added!)
        for node in list(dot_graph.get_nodes()):
            if str(node) == '"\\n";':
                dot_graph.del_node(node)
        if params.img_format == "svg":
            method = dot_graph.write_svg
        elif params.img_format == "pdf":
            method = dot_graph.write_pdf
        elif params.img_format == "png":
            method = dot_graph.write_png
        else:
            method = dot_graph.write_jpg
        method(outpath)
        print(colorama.Fore.GREEN + 'Generated state machine diagram {}'.format(outpath) + colorama.Style.RESET_ALL)
        if view:
            webbrowser.open(outpath.absolute().as_uri())

def not_implemented(_):
    """Default behavior for unimplemented features.

    """
    print(colorama.Fore.RED + colorama.Style.BRIGHT + 'Feature not implemented in this model.' + colorama.Style.RESET_ALL)
    sys.exit(0)

def set_seed(params, seed=None, show=False):
    """Initialize the numpy's Random Number Generator, either with the
    specified seed, or with a seed calculated from current time and
    process ID.

    """
    if seed is None:
        params.seed = int(os.getpid() + time.time())
    else:
        params.seed = int(seed)
    np.random.seed(params.seed)
    if show:
        print(colorama.Style.BRIGHT + 'RANDOM SEED: {}'.format(params.seed) + colorama.Style.RESET_ALL)


def init_main_level(params):
    """Initialize the upper simulation level, in charge of making all
    sub-levels work properly.

    """
    if params.level not in params.model.levels:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 'ERROR, level {} not found'.format(params.level) + colorama.Style.RESET_ALL)
        sys.exit(-1)

    module_name = params.model.levels[params.level]['module']
    class_name = params.model.levels[params.level]['class_name']
    try:
        params.target_agent_class = load_class(module_name,
                                               class_name=class_name)[0]
    except AttributeError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 'ERROR, agent class not found for level {}: {}.{}'.format(params.level, module_name, class_name) + colorama.Style.RESET_ALL)
        sys.exit(-1)
    except ModuleNotFoundError:
        print(colorama.Fore.RED + colorama.Style.BRIGHT +  'ERROR, module not found for level {}: {}'.format(params.level, module_name) + colorama.Style.RESET_ALL)
        sys.exit(-1)


def table_param(params):
    """Display a table of parameters and initial conditions.

    """
    parameters = params.model._description['parameters']
    strOutput = 'PARAMETERS\n__________\n\n'
    strOutput += '|   name                 |    value '+(' '*41)+'| description\n'
    strOutput += '-' * 200 + '\n'
    for p in parameters:
        if '{' not in p:
            strOutput += create_desc(parameters, p)
    print(strOutput)

    initials = params.model._description['initial_conditions']
    strOutput = '\n\nINITIAL CONDITIONS\n__________________\n\n'
    strOutput += '|   name                 |    value\n'
    strOutput += '-' * 200 + '\n'
    strOutput += create_initial(initials)
    print(strOutput)

def create_desc(parameters, p):
    name = p
    result = '| ' + name + ' '*(23 - len(name)) + '| '

    val = str(parameters[p]['value'])
    result += val + ' '*(50 - len(val)) + '| '

    desc = parameters[p]['desc']
    result += desc+'\n'

    return result

def create_initial(initials):
    result = ''
    for i in initials:
        result += colorama.Style.DIM + '  ' + i + '\n' + colorama.Style.RESET_ALL
        desc = initials[i]
        for elem in desc:
            for e in elem:
                result += '  ' + e + ' '*(23 - len(e))
                result += '| ' + str(elem[e]) + '\n'
            result += '\n'
    return result


def main(args=None):
    """Run EMuLSion's main program according to the command-line
    arguments.

    """
    colorama.init()
    if args is None:
        args = docopt(__doc__, version=get_version())

    if args['--license']:
        print(colorama.Fore.CYAN + get_license() + colorama.Style.RESET_ALL)
        sys.exit(0)

    if not Path(args['MODEL']).exists():
        print(colorama.Fore.RED + colorama.Style.BRIGHT + 'ERROR: file {} not found'.format(args['MODEL']) + colorama.Style.RESET_ALL)
        sys.exit(-1)

    params = StateVarDict()
    params.filename = args['MODEL']
    params.input_dir = Path(args['--input-dir'])
    params.model = EmulsionModel(filename=params.filename, input_dir=params.input_dir)
    params.nb_simu = int(args['--runs'])
    params.stochastic = not args['--deterministic']
    params.to_describe = args['PARAM']

    params.img_format = args['--format']
    if params.img_format not in ['pdf', 'png', 'svg', 'jpg']:
        print(colorama.Fore.RED + colorama.Style.BRIGHT + f'Invalid diagram format: {params.img_format}' + colorama.Style.RESET_ALL)
        sys.exit(-1)

    params.save_to_file = args['--save']
    params.load_from_file = args['--load']

    params.level = args['--level']
    if params.level is None:
        params.level = params.model.root_level
    if not args['--modifiable']:
        print(colorama.Style.DIM + 'Simulation level:{}'.format(params.level) + colorama.Style.NORMAL)

    params.silent = args['--silent']
    params.quiet = args['--quiet']
    params.nocount = args['--no-count']
    params.start_id = int(args['--start-id'])
    params.output_dir = Path(args['--output-dir'])
    params.figure_dir = Path(args['--figure-dir'])
    params.code_path = Path(args['--code-path'])
    params.aggregate_plot = args['--aggregate']
    params.detail_plot = args['--detail']
    sys.path.append(str(params.code_path))

    if not params.output_dir.exists():
        params.output_dir.mkdir(parents=True)
    if not params.figure_dir.exists():
        params.figure_dir.mkdir(parents=True)
    params.output_dir = str(params.output_dir)

    params.log_params = args['--log-params'] ## TODO: WARNING DEPRECATED

    params.stock_agent = False
    params.keep_history = False

    if args['--param']:
        change_parameters(params, args['--param'])

    if args['--time']:
        params.steps = int(args['--time'])
    elif 'total_duration' in params.model.parameters:
        params.steps = int(np.ceil(params.model.get_value('total_duration') / params.model.delta_t))
    else:
        params.steps = 100

    if args['--modifiable']:
        show_parameters(params, short=True)

    set_seed(params, seed=args['--seed'], show=args['--show-seed'])

    if args['--echo']:
        print(args)
        sys.exit(0)

    params.view_machines = False
    if args['--view-model']:
        produce_diagrams(params)
        params.view_machines = True

    if args['--table-params']:
        table_param(params)

    if args['diagrams']:
        produce_diagrams(params, view=True)
        sys.exit(0)
    elif args['generate']:
        generate_model(params)
    elif args['run']:
        init_main_level(params)
        run_model(params)
        if args['--plot']:
            plot_outputs(params)
    elif args['show']:
        show_parameters(params)
    elif args['describe']:
        describe_parameters(params)
    elif args['plot']:
        plot_outputs(params)
    elif args['change']:
        not_implemented(params)
    elif args['sensitivity']:
        not_implemented(params)
    else:
        return params


################################################################
#                  _
#                 (_)
#  _ __ ___   __ _ _ _ __
# | '_ ` _ \ / _` | | '_ \
# | | | | | | (_| | | | | |
# |_| |_| |_|\__,_|_|_| |_|
#
################################################################

if __name__ == '__main__':
    main()
