"""A Python implementation of the EMuLSion framework (Epidemiologic
MUlti-Level SImulatiONs).

Tools aimed at handling graphs for the state machines
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

from   emulsion.tools.state      import EmulsionEnum


EdgeTypes = EmulsionEnum('EdgeTypes', ['TRANSITION', 'PRODUCTION'], module=__name__)
EdgeTypes.linestyle = 'solid'
EdgeTypes.PRODUCTION.linestyle = 'dashed'



class MultiDiGraph:
    """An oriented multigraph (two nodes can be linked by several
    edges). Replacement for MultiDiGraph in networkx with a
    reproducible order in accessing edges and nodes.

    """
    def __init__(self, **attributes):
        """Create an instance of MultiDiGraph. If keywords arguments
        are specified, they are considered attributes of the whole
        graph.

        """
        self.graph = dict(**attributes)
        self.node = OrderedDict()
        self.edge = OrderedDict()
        self._edge_counter = OrderedDict()

    def add_node(self, node_id, **attributes):
        """Add the specified node to the graph. Node attributes can be
        specified. If the node is already present, updated the
        attributes.

        """
        if node_id not in self.node:
            self.node[node_id] = dict()
        self.node[node_id].update(attributes)


    def add_edge(self, from_id, to_id, type_id=EdgeTypes.TRANSITION,
                 key=None, **attributes):
        """Add the specified edge to the graph. If nodes are not
        already created, they are automatically added. Edge attributes
        can be specified. Since this graph allows multiple edges
        between pairs of nodes, two calls to this method lead to two
        distinct edges (even if the attributes are the same), unless a
        key is specified. The key is used to identify edges between a
        given pair of nodes. By default, keys are consecutive
        integers.

        """
        self.add_node(from_id)
        self.add_node(to_id)
        if from_id not in self.edge:
            self.edge[from_id] = OrderedDict()
            self._edge_counter[from_id] = OrderedDict()
        if to_id not in self.edge[from_id]:
            self.edge[from_id][to_id] = OrderedDict()
            self._edge_counter[from_id][to_id] = 0
        if key is None:
            edge_key = self._edge_counter[from_id][to_id]
            self._edge_counter[from_id][to_id] += 1
        else:
            edge_key = key
        attributes['type_id'] = type_id
        self.edge[from_id][to_id][edge_key] = dict(**attributes)

    def edges(self):
        """Return a list of edge tuples."""
        return [(from_id, to_id)
                for from_id in self.edge
                for to_id in self.edge[from_id]]

    def edges_from(self, from_id, type_id=EdgeTypes.TRANSITION):
        """Return a list of tuples (to_id, attributes) corresponding
        to all edges going out of the `from_id` node.

        """
        if from_id not in self.edge:
            return []
        return [(state, attribs)
                for state in self.edge[from_id]
                for attribs in self.edge[from_id][state].values()
                if (type_id is None) or (attribs['type_id'] == type_id)]
