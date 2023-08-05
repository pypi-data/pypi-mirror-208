""".. module:: emulsion.tools.state

This module defines:

- a class ``StateVarDict`` which is a special auto-referential
  dictionary to handle state variables
- a class ``EmulsionEnum`` which is a special kind of enumeration
  intended to handle states from state machines

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


from   enum                       import Enum
from   functools                  import total_ordering


class StateVarDict(dict):
    """A special dictionary aimed at handling the state variables of
    agents in EMULSION models. In addition to the classical dict
    key-based access, it provides an attribute-like access syntax.

    This class is used in EMULSION to store agent properties. Such
    properties include those defined automatically and used by the
    EMULSION engine, such as the values of the states for each state
    machine, the current time step, or "hidden" values such as the
    time spent in the current state for each state machine. They are
    also used to include user-defined attributes (e.g. age,
    weight...).

    When searching for a model ``statevar``, the engine tries first to
    find a classical instance variable (which can be mimicked by a
    Python ``@property``-decored function), then looks inside the
    agent's ``statevar`` attribute; finally, the search continues in
    the agent's host (if any).

    Example
    -------

    .. code-block:: python

        s = StateVarDict(age=10, sick=True)
        s['age'] += 1
        s.sick = False
        s.new_property = 'Wow !'

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # make self its own attributes dictionary (nice, hey ?)
        self.__dict__ = self


@total_ordering
class EmulsionEnum(Enum):
    """This class represents enumerations for states of state machines in
    EMULSION. They are endowed with some special features:

    #. They provide total ordering between items (based on ``__lt__``
       and ``__eq__`` methods).
    #. A comparison with ``None`` is provided (any state is always
       greater than ``None``).
    #. Underlying values can be used to get/set states

    """

    def __lt__(self, other):
        """Return a less-than comparison for enumeration items. An enum item
        is always greater than ``None``and than any other item of
        another enumeration. Then, the ``value`` attribute of the item
        is used.

        Parameters
        ----------
        other: EmulsionEnum
            Another state from the same enumeration (or ``None``)

        Returns
        -------
        boolean:
            True if the current state is less than *other*
            (i.e. defined before *other* in the list of states), False
            otherwise (including the case where *other* is ``None``).

        """
        return False if other is None or other.__class__ != self.__class__\
          else self.value < other.value

    def __eq__(self, other):
        """Return a equality comparison for enumeration items. An enum item is
        always greater than ``None``and than any other item of another
        enumeration. Then, the ``value`` attribute of the item is
        used.

        Parameters
        ----------
        other: EmulsionEnum
            Another state from the same enumeration (or ``None``)

        Returns
        -------
        boolean:
            True if the current state is equal to *other* (having the
            same value), False otherwise (including the case where
            *other* is ``None``).

        """
        return False if other is None or other.__class__ != self.__class__\
          else self.value == other.value

    def __int__(self):
        """Return the *int* value mapped to this item."""
        return self.value

    def __repr__(self):
        """Return a string representation of the instances of the enumeration,
        hiding associated numerical value.

        """
        return f'<{self.__class__.__name__}.{self.name}>'

    def __hash__(self):
        """Use the value as hashcode."""
        return self.value
