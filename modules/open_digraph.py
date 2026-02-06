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