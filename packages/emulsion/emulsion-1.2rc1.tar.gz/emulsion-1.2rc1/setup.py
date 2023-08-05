"""Configuration file for distributing the Emulsion package.
"""

# [HEADER]

from   setuptools import setup, find_packages

VERSION = '1.2rc1'
LICENSE = 'Apache-2.0'

if LICENSE.startswith('Apache'):
    LONG_LICENSE = 'License :: OSI Approved :: Apache Software License'
elif 'BSD' in LICENSE:
    LONG_LICENSE = 'License :: OSI Approved :: BSD License'
else:
    LONG_LICENSE = 'License :: Other/Proprietary License'

LONG_DESC = """
Framework EMULSION is intended for modellers in epidemiology, to help
them design, simulate, and revise complex mechanistic stochastic
models, without having to write or rewrite huge amounts of code.

It comes with a *Domain-Specific Language* to represent all components
of epidemiological models (assumptions, model structure,
parameters...) in an explicit, intelligible and revisable way, and
thus facilitate interactions with other scientists (biologists,
veterinarians, economists...) throughout the modelling
process. EMULSION models are automatically processed by a modular
simulation engine, which, if needed, can also incorporate small code
add-ons for representing very specific features of a model.

Models can use classical modelling paradigms (compartments,
individual-based models, metapopulations) and multiple scales (from
individuals to metapopulations), thanks to recent research in
Artificial Intelligence.
"""


setup(
    # This is the name of your project. The first time you publish this
    # package, this name will be registered for you. It will determine how
    # users can install this project, e.g.:
    #
    # $ pip install sampleproject
    #
    # And where it will live on PyPI: https://pypi.org/project/sampleproject/
    #
    # There are some restrictions on what makes a valid project name
    # specification here:
    # https://packaging.python.org/specifications/core-metadata/#name
    name='emulsion',       # Required
    # Versions should comply with PEP 440:
    # https://www.python.org/dev/peps/pep-0440/
    #
    # For a discussion on single-sourcing the version across setup.py and the
    # project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=VERSION, # Required
    license=LICENSE,
    # This is a one-line description or tagline of what your project does. This
    # corresponds to the "Summary" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#summary
    description='Epidemiological Multi-Level Simulation framework',
    long_description = LONG_DESC,
    # This should be a valid link to your project's main homepage.
    #
    # This field corresponds to the "Home-Page" metadata field:
    # https://packaging.python.org/specifications/core-metadata/#home-page-optional
    url='https://sourcesup.renater.fr/emulsion-public/',
    download_url='https://pypi.org/project/emulsion/',
    # url='https://github.com/pypa/emulsion',  # Optional
    # This should be your name or the name of the organization which owns the
    # project.
    author='Sébastien Picault, Yu-Lin Huang, Vianney Sicard and Pauline Ezanno',  # Optional
    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='sebastien.picault@inrae.fr',  # Optional
    maintainer='Sébastien Picault',
    maintainer_email='sebastien.picault@inrae.fr',  # Optional
    # Classifiers help users find your project by categorizing it.
    #
    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Education',
        # Pick your license as you wish
        LONG_LICENSE,
        # 'License :: The 3-Clause BSD License (BSD-3-Clause)',
        'Natural Language :: English',
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Unix Shell',
        # Specify the Operating Systems supported by your package
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix', # not tested in general - report bugs
        'Operating System :: Microsoft :: Windows :: Windows 10', # not tested in general - report bugs,
        # Specify the environment
        'Environment :: Console',
        'Environment :: MacOS X',

    ],
    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a string of words separated by whitespace, not a list.
    keywords='epidemiological modelling, computational epidemiology, '
    'multilevel modelling, compartment-based models, individual-based models, '
    'metapopulations, agent-based simulation, animal health, artificial intelligence, '
    'stochastic models, mechanistic models',
    packages=find_packages(where='src',
                           exclude=['emulsion_examples',
                                    'emulsion_examples.*']),
    # packages=find_packages(exclude=['emulsion_examples']),
    # You can just specify package directories manually here if your project is
    # simple. Or you can use find_packages().
    #
    # Alternatively, if you just want to distribute a single Python file, use
    # the `py_modules` argument instead as follows, which will expect a file
    # called `my_module.py` to exist:
    #
    #   py_modules=["my_module"],
    #
    ##  cd src && for file in `find emulsion -name "*.py" | cut -d '.' -f 1` ; do echo "'$file',";  done
    # py_modules=[
    #     'emulsion/tools/simulation',
    #     'emulsion/tools/functions',
    #     'emulsion/tools/misc',
    #     'emulsion/tools/plot',
    #     'emulsion/tools/graph',
    #     'emulsion/tools/__init__',
    #     'emulsion/tools/calendar',
    #     'emulsion/tools/timing',
    #     'emulsion/tools/view',
    #     'emulsion/tools/parallel',
    #     'emulsion/tools/state',
    #     'emulsion/__init__',
    #     'emulsion/agent/core/__init__',
    #     'emulsion/agent/core/groups',
    #     'emulsion/agent/core/emulsion_agent',
    #     'emulsion/agent/core/abstract_agent',
    #     'emulsion/agent/managers/functions',
    #     'emulsion/agent/managers/compart_process_manager',
    #     'emulsion/agent/managers/abstract_process_manager',
    #     'emulsion/agent/managers/metapop_process_manager',
    #     'emulsion/agent/managers/multi_process_manager',
    #     'emulsion/agent/managers/ibm_process_manager',
    #     'emulsion/agent/managers/__init__',
    #     'emulsion/agent/managers/group_manager',
    #     'emulsion/agent/__init__',
    #     'emulsion/agent/action',
    #     'emulsion/agent/comparts',
    #     'emulsion/agent/exceptions',
    #     'emulsion/agent/process',
    #     'emulsion/agent/atoms',
    #     'emulsion/agent/views',
    #     'emulsion/agent/meta',
    #     'emulsion/model/functions',
    #     'emulsion/model/__init__',
    #     'emulsion/model/emulsion_model',
    #     'emulsion/model/exceptions',
    #     'emulsion/model/state_machines',
    #     'emulsion/templates/specific_code',
    #     'emulsion/__main__',
    # ],
    # packages=find_packages(where='src',
    #                        include=['*.py'],
    #                        exclude=['emulsion.dynpop']),
    package_dir = {'': 'src'},
    # This field lists other packages that your project depends on to run.
    # Any package you put here will be installed by pip when your project is
    # installed, so they must be valid existing projects.
    #
    # For an analysis of "install_requires" vs pip's requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'numpy>=1.23',             # BSD
        'scipy>=1.9',              # BSD
        'matplotlib>=3.5',         # Python Software Foundation ## only used in emulsion.tools.views which is not used anywhere now
        'sympy>=1.11',            # BSD
        'mpmath>=1.2',             # BSD
        'pandas>=1.4',            # Simplified BSD
        'pydot>=1.4',           # MIT
        'sqlalchemy>=1.4',      # MIT
        'sortedcontainers>=2.4', # Apache
        'tqdm>=4.23',              # MIT
        'pyyaml>=3.12',            # MIT
        'docopt>=0.6.2',           # MIT
        'jinja2>=3.1',            # BSD  ## only used to generate .py file templates, soon obsolete
        'python-dateutil>=2.8',    # BSD
        # 'utm>=0.7',                # MIT ## no more in use (was used in Qfever model)
        'bokeh>=2.4',             # BSD 3-Clause
        'networkx>=2.8',           # BSD
        'colorama>=0.4',           # BSD
        # 'ggplot',                  # BSD 2-Clause "Simplified" License
    ],
    python_requires='>=3.9',
    # List additional groups of dependencies here (e.g. development
    # dependencies). Users will be able to install these using the "extras"
    # syntax, for example:
    #
    #   $ pip install sampleproject[dev]
    #
    # Similar to `install_requires` above, these must be valid existing
    # projects.
    extras_require={  # Optional
        'doc': [
            # 'doxypypy',              # GPL2
            'sphinx>=5.1',             # BSD
            'alabaster',               # BSD
        ],
        'dev': [
            'setuptools>=63.4',        # MIT
            'wheel>=0.37',                   # MIT
            'twine>=4.0',                   # Apache-2.0
            'pylint>=2.14',           # GPL
            'cython>=0.29',            # Apache
            'jupyter>=1.0',                 # Modified (3-clause) BSD
            # 'graphviz-python>=2.32', # Eclipse Public License
        ],
    },

    include_package_data=True,

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # `pip` to create the appropriate form of executable for the target
    # platform.
    #
    # For example, the following would provide a command called `emulsion` which
    # executes the function `main` from this package when invoked:
    entry_points={  # Optional
        'console_scripts': [
            'emulsion = emulsion.__main__:main',
            'init_emulsion = emulsion.init_emulsion:main',
        ],
    },
    # List additional URLs that are relevant to your project as a dict.
    #
    # This field corresponds to the "Project-URL" metadata fields:
    # https://packaging.python.org/specifications/core-metadata/#project-url-multiple-use
    #
    # Examples listed include a pattern for specifying where the package tracks
    # issues, where the source is hosted, where to say thanks to the package
    # maintainers, and where to support the project financially. The key is
    # what's used to render the link text on PyPI.
    # project_urls={  # Optional
    #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #     'Funding': 'https://donate.pypi.org',
    #     'Say Thanks!': 'http://saythanks.io/to/example',
    #     'Source': 'https://github.com/pypa/sampleproject/',
    # },
    project_urls={
        # "Bug Tracker": "https://bugs.example.com/HelloWorld/",
        "Documentation": "https://sourcesup.renater.fr/emulsion-public/",
        "Source Code": "https://git.renater.fr/emulsion-public.git",
    }
)
