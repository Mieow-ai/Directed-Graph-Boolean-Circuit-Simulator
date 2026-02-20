class node:
    def __init__(self, identity, label, parents, children):
        '''
        identity: int; its unique id in the graph
        label: string;
        parents: int->int dict; maps a parent node's id to its multiplicity
        children: int->int dict; maps a child node's id to its multiplicity
        '''
        self.id = identity
        self.label = label
        self.parents = parents
        self.children = children

    def __str__(self):
        s = f"Node : {self.id}; label : {self.label}; parents : " + self.parents.__str__() + "; children :" + self.children.__str__() + ";\n"
        return s
    
    def __repr__(self):
        return self.__str__()
    
    def copy(self):
        """
        Renvoie une copie profonde du noeud.
        
        :param self: Description
        """
        return node(self.id, self.label, self.parents.copy(), self.children.copy())
    
    # Getter 

    def get_id(self):
        return self.id
    def get_label(self):
        return self.label
    def get_parents(self):
        return self.parents
    def get_children(self):
        return self.children
    
    # Setter 

    def set_id(self, id):
        self.id = id
    def set_label(self, label):
        self.label = label
    def set_parents(self, parents):
        self.parents = parents
    def set_children(self, children):
        self.children = children
    def add_child_id(self, child_id, multiplicity):
        if child_id in self.children:
            self.children[child_id] += multiplicity
        else:
            self.children[child_id] = multiplicity
    def add_parent_id(self, parent_id, multiplicity):
        if parent_id in self.parents:
            self.parents[parent_id] += multiplicity
        else:
            self.parents[parent_id] = multiplicity
            
    # methods
    
    def remove_parent_once(self, parent_id):
        if parent_id in self.parents:
            if self.parents[parent_id] > 1:
                self.parents[parent_id] -= 1
            elif self.parents[parent_id] == 0:
                raise ValueError(f"Parent_id {parent_id} a une multiplicité nulle dans node {self.id}")
            else:
                del self.parents[parent_id]
        else:
            raise ValueError(f"Parent_id {parent_id} pas dans node {self.id}")
        
    def remove_child_once(self, child_id):
        if child_id in self.children:
            if self.children[child_id] > 1:
                self.children[child_id] -= 1
            elif self.children[child_id] == 0:
                raise ValueError(f"Child_id {child_id} a une multiplicité nulle dans node {self.id}")
            else:
                del self.children[child_id]
        else:
            raise ValueError(f"Child_id {child_id} pas dans node {self.id}")
        
    def remove_parent_id(self, parent_id):
        if parent_id in self.parents:
            del self.parents[parent_id]
        else:
            raise ValueError(f"Parent_id {parent_id} pas dans node {self.id}")
    
    def remove_child_id(self, child_id):
        if child_id in self.children:
            del self.children[child_id]
        else:
            raise ValueError(f"Child_id {child_id} pas dans node {self.id}")
        

    

class open_digraph: # for open directed graph
    def __init__(self, inputs, outputs, nodes):
        '''
        inputs: int list; the ids of the input nodes
        outputs: int list; the ids of the output nodes
        nodes: node iter;
        '''
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = {node.id:node for node in nodes} # self.nodes: <int,node> dict
    def __str__(self):
        s = "Graph :\n"
        s += "Inputs : " + self.inputs.__str__() + "\n"
        s += "Outputs : " + self.outputs.__str__() + "\n"
        s += "Nodes : \n"
        for node in self.nodes.values():
            s += node.__str__()
        return s
    def __repr__(self):
        return self.__str__()
    
    @classmethod
    def empty(cls):
        """
        Renvoie un graphe vide.
        
        :param cls: Description
        """
        return cls([],[],[])
    def copy(self):
        '''
        Renvoie une copie profonde du graphe.
        
        :param self: Description
        '''
        return open_digraph(self.inputs.copy(), self.outputs.copy(), [node.copy() for node in self.nodes.values()])
    
    # Getter

    def inputs_ids(self):
        return self.inputs
    def outputs_ids(self):
        return self.outputs
    def get_id_node_map(self):
        return {id:nodes for id, nodes in self.nodes.items()}
    def get_nodes(self):
        return list(self.nodes.values())
    def get_node_ids(self):
        return list(self.nodes.keys())
    def get_node_by_id(self, id):
        return self.nodes[id]
    def get_nodes_by_ids(self, ids):
        return list(map(lambda id: self.nodes[id], ids))
    
    # Setter
    
    def set_inputs(self, inputs):
        self.inputs = inputs
    def set_outputs(self, outputs):
        self.outputs = outputs
    def add_input_id(self, input_id):
        self.inputs.append(input_id)
    def add_output_id(self, output_id):
        self.outputs.append(output_id)
        
    def new_id(self):
        if len(self.nodes) == 0:
            return 0
        else:
            return max(self.nodes.keys()) + 1
    
    def add_edge(self, src, tgt):
        self.nodes[src].add_child_id(tgt, 1)
        self.nodes[tgt].add_parent_id(src, 1)
    
    def add_edgeM(self, src, tgt, multiplicity):
        self.nodes[src].add_child_id(tgt, multiplicity)
        self.nodes[tgt].add_parent_id(src, multiplicity)
    
    def add_edges(self, edges):
        for src, tgt in edges:
            self.add_edge(src, tgt)
            
    def add_node(self, label='', parents=None, children=None):
        new_id = self.new_id()
        if parents is None:
            parents = {}
        if children is None:
            children = {}
        new_node = node(new_id, label, parents, children)
        self.nodes[new_id] = new_node
        return new_id
    
    # Other methods
    
    def remove_edge(self, src, tgt):
        self.nodes[src].remove_child_once(tgt)
        self.nodes[tgt].remove_parent_once(src)
    
    def remove_parallel_edges(self, src, tgt):
        self.nodes[src].remove_child_id(tgt)
        self.nodes[tgt].remove_parent_id(src)
    
    def remove_node_by_id(self, node_id):
        if node_id in self.nodes:
            for parent_id in self.nodes[node_id].get_parents().keys():
                self.remove_edge(parent_id, node_id)
            for child_id in self.nodes[node_id].get_children().keys():
                self.remove_edge(node_id, child_id)
            del self.nodes[node_id]
        else:
            raise ValueError(f"Node_id {node_id} pas dans le graphe")
        
    def removes_edges(self, edges):
        for src, tgt in edges:
            self.remove_edge(src, tgt)
    
    def remove_several_parallel_edges(self, edges):
        for src, tgt in edges:
            self.remove_parallel_edges(src, tgt)
    
    def remove_nodes_by_id(self, node_ids):
        for node_id in node_ids:
            self.remove_node_by_id(node_id)
            
    def __delitem__(self, node_id):
        self.remove_node_by_id(node_id)
    
    def well_formed(self):
        for node_id in self.inputs + self.outputs:
            if node_id not in self.nodes:
                return False
        
        for node_id in self.inputs:
            node = self.nodes[node_id]
            if len(node.get_parents()) != 0:
                return False
            children = node.get_children()
            if len(children) != 1:
                return False
            if list(children.values())[0] != 1:
                return False
            
        for node_id in self.outputs:
            node = self.nodes[node_id]
            if len(node.get_children()) != 0:
                return False
            parents = node.get_parents()
            if len(parents) != 1:
                return False
            if list(parents.values())[0] != 1:
                return False
            
        for key, node in self.nodes.items():
            if key != node.get_id():
                return False
        
        for node_id, node in self.nodes.items():
            for child_id, m in node.get_children().items():
                if child_id not in self.nodes:
                    return False
                child_node = self.nodes[child_id]
                child_parents = child_node.get_parents()
                if node_id not in child_parents:
                    return False
                if child_parents[node_id] != m:
                    return False
        return True
    
    def assert_is_well_formed(self):
        if not self.well_formed():
            raise ValueError("Graphe pas bien formé")
        
    def add_input_node(self, id, label=''):
        if id not in self.nodes.keys():
            raise ValueError('Pointe vers rien')
        if id in self.outputs:
            raise ValueError('Le noeud id est un noeud de sortie alors que la multiplicité ne peut être que de 1')
        new_id = self.add_node(label, {}, {})
        self.add_input_id(new_id)
        self.add_edge(new_id, id)
        
    def add_output_node(self, id, label=''):
        if id not in self.nodes.keys():
            raise ValueError('Point vers rien')
        if id in self.inputs:
            raise ValueError("Le noeud id est un noeud d'entrée alors que la multiplicité ne peut être que de 1")
        new_id = self.add_node(label, {}, {})
        self.add_output_id(new_id)
        self.add_edge(id, new_id)
    
    @staticmethod
    def random_int_list(n, bound):
        import random
        return [random.randrange(0, bound) for e in range(n)]
    
    @staticmethod
    def random_int_matrix(n, bound, null_diag=True):
        res = [open_digraph.random_int_list(n, bound) for e in range(n)]
        if null_diag:
            for i in range(n):
                for j in range(n):
                    res[i][j] = 0
        return res

    @staticmethod
    def random_symetric_int_matrix(n, bound, null_diag=True):
        res = open_digraph.random_int_matrix(n, bound, null_diag)
        for i in range(n):
            for j in range(i+1, n):
                res[i][j] = res[j][i]
        return res
    
    @staticmethod
    def random_oriented_int_matrix(n, bound, null_diag=True):
        res = open_digraph.random_int_matrix(n, bound, null_diag)
        for i in range(n):
            for j in range(i+1, n):
                if res[i][j] != 0:
                    res[j][i] = 0
        return res
    
    @staticmethod
    def random_triangular_int_matrix(n, bound, null_diag=True):
        res = open_digraph.random_int_matrix(n, bound, null_diag)
        for i in range(n):
            for j in range(i+1, n):
                res[i][j] = 0
        return res
    
    def graph_from_adjacency_matrix(self, matrix):
        dim = len(matrix)
        ids = []
        for i in range(dim):
            n = self.add_node()
            ids.append(n)
            
        for i in range(dim):
            for j in range(dim):
                if matrix[i][j] > 0:
                    self.add_edgeM(ids[i], ids[j], matrix[i][j])
                    
                
    @classmethod
    def random(cls, n, bound, inputs=0, outputs=0, form="free"):
        """
        Génère un graphe aléatoire.
        Options pour form : 
        - "free" : Graphe quelconque
        - "loop-free" : Graphe quelconque sans boucles sur soi-même
        - "undirected" : Graphe symétrique
        - "loop-free undirected" : Graphe symétrique sans boucles
        - "oriented" : Graphe orienté
        - "DAG" : Graphe Acyclique
        """
        g = cls.empty()
        matrix = []
        if form == "free":
            matrix = g.random_int_matrix(n, bound, null_diag=False)
            
        elif form == "loop-free":
            matrix = g.random_int_matrix(n, bound, null_diag=True)
            
        elif form == "undirected":
            matrix = g.random_symetric_int_matrix(n, bound, null_diag=False)
            
        elif form == "loop-free undirected":
            matrix = g.random_symetric_int_matrix(n, bound, null_diag=True)
            
        elif form == "oriented":
            matrix = g.random_oriented_int_matrix(n, bound, null_diag=True)
            
        elif form == "DAG":
            matrix = g.random_triangular_int_matrix(n, bound, null_diag=True)
        else:
            raise ValueError(f"Forme de graphe inconnue : {form}")
        g.graph_from_adjacency_matrix(matrix)
        ids = sorted(list(g.nodes.keys()))
        n_inputs = [i for i in ids if not g.nodes[i].get_parents()]
        n_outputs = [i for i in ids if not g.nodes[i].get_children()]
        for i in range(inputs):
            g.add_input_node(n_inputs[i])
        for i in range(outputs):
            g.add_output_node(n_outputs[i])
        return g
    
    def graph_to_dict(self):
        res = {}
        for i, node_id in enumerate(self.nodes.keys()):
            res[node_id] = i
        return res
    
    def adjacency_matrix(self):
        n = len(self.nodes)
        matrix = [[0 for j in range(n)] for i in range(n)]
        id_to_index = self.graph_to_dict()
        for node_id, node in self.nodes.items():
            for child_id, m in node.get_children().items():
                matrix[id_to_index[node_id]][id_to_index[child_id]] = m
        return matrix
    
    