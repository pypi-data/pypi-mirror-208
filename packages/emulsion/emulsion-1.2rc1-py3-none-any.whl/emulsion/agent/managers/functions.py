"""
.. module:: emulsion.agent.managers.functions

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

from   collections               import OrderedDict

#  ______                _   _
# |  ____|              | | (_)
# | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
# |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
# | |  | |_| | | | | (__| |_| | (_) | | | \__ \
# |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

def _group_by_populations(transitions):
    """`transitions` is a list of tuples (state, flux, value,
    cond_result, actions) where:
    - state is a possible state reachable from the current state flux
    - is either 'rate' or 'proba' or 'amount' or 'amount-all-but'
    - value is the corresponding rate or probability or amount
    - cond_result is a couple (either ('population', qty, esc) or ('agents', list, esc))
      describing who fulfills the condition to cross the transition
    - actions is the list of actions on cross
    """
    transitions_by_pop = OrderedDict()
    for state, flux, value, population, actions in transitions:
        desc, pop, esc = population
        if desc == 'agents':
            pop = frozenset(pop)    # required to be hashable
        if (desc, pop, esc) not in transitions_by_pop:
            transitions_by_pop[(desc, pop, esc)] = []
        transitions_by_pop[(desc, pop, esc)].append((state, flux, value, actions))
    # rewrite elements as a list
    return list(transitions_by_pop.items())

def _split_populations(list_of_items):
    """Transform a list of transitions into a dictionary based on the
    underlying populations.

    `list_of_items` is composed of pairs
    - the first element is a tuple ('agents', frozenset, None)
    - the second element is a list of tuples (state, flux, value,
      actions) associated with the population/agents

    Greedy algorithm: the first population of agents is compared with
    all others to check if any intersection exists. If so, both are
    replaced by their difference (if not empty) with the intersection,
    and the intersection is added to the list with a concatenation of
    the features attached to both populations.
    """
    # remove 'agents' keyword to facilitate set-like operations
    population_list = [(pop[1], attributes) for pop, attributes in list_of_items]
    i = 0
    while i < len(population_list) - 1:
        # select the first population in the list
        ref_pop, ref_attrib = population_list[i]
        j = i + 1
        intersects = False
        # check if any intersection with another population
        while j < len(population_list) and not intersects:
            # intersection found
            if population_list[j][0] & ref_pop:
                intersects = True
            else:
                j += 1
        if intersects:
            # retrieve features of the other population
            other_pop, other_attrib = population_list[j]
            # compute intersections and differences
            inter = ref_pop & other_pop
            new_ref =  ref_pop - inter
            new_other = other_pop - inter
            # if empty populations, remove them else update the populations
            if not new_other:
                population_list.pop(j)
            else:
                population_list[j] = (new_other, other_attrib)
            if not new_ref:
                population_list.pop(i)
            else:
                population_list[i] = (new_ref, ref_attrib)
            # add the intersection as a new population with a
            # concatenation of other properties
            population_list.append((inter, ref_attrib + other_attrib))
        else:
            # if no intersection was found, move to next item
            # (otherwise keep the same and iterate again on other
            # items)
            i += 1
    return [(('agents', list(agents), None), attributes)
            for agents, attributes in population_list]


def group_and_split_populations(transitions):
    """Transform a list of transitions into a dictionary based on the
    underlying populations.

    `transitions` is a list of tuples (state, flux, value,
    cond_result, actions) where:
    - state is a possible state reachable from the current state
    - flux is either 'rate' or 'proba' or 'amount' or 'amount-all-but'
    - value is the corresponding rate or probability or amount
    - cond_result is a couple (either ('population', qty, esc) or ('agents', list, None))
      describing who fulfills the condition to cross the transition
    - actions is the list of actions on cross

    The goal of this function is to restructure all those elements for
    disjoint sub-populations.

    Return a list of tuples:
      either (('population', qty, esc), attributes)
      or     (('agents', list, None), attributes)
    where attributes is a list of tuples (state, flux, value, actions)

    """
    ### 1st step: gather elements
    # list_of_items is composed of pairs
    # - the first element is a tuple either ('population', qty) or
    #   ('agents', frozenset)
    # - the second element is a list of tuples (state, flux, value,
    #   actions) associated with the population/agents
    list_of_items = _group_by_populations(transitions)
    # if based on population (not on agents) then we're done (assuming
    # that all other values are based on populations)
    if list_of_items[0][0][0] == 'population':
        return list_of_items
    # otherwise we have true agents populations
    ### 2nd step: split sub-populations
    result =  _split_populations(list_of_items)
    #print(result)
    return result
