import os 
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
    def __eq__(self, other):
        if not isinstance(other, node):
            return False
        return self.id == other.id and self.label == other.label and self.parents == other.parents and self.children == other.children
    
    def indegree(self):
        return sum(self.parents.values())
    
    def outdegree(self):
        return sum(self.children.values())
    
    def degree(self):
        return self.indegree() + self.outdegree()
        

    

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
            
    def add_node(self, label='', parents=None, children=None, id=None):
        if id is None:
            new_id = self.new_id()
        else:
            if id in self.nodes:
                raise ValueError(f"Id {id} déjà dans le graphe")
            new_id = id
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
            for parent_id in list(self.nodes[node_id].get_parents().keys()):
                self.remove_parallel_edges(parent_id, node_id)
            for child_id in list(self.nodes[node_id].get_children().keys()):
                self.remove_parallel_edges(node_id, child_id)
            del self.nodes[node_id]
            if node_id in self.inputs:
                self.inputs.remove(node_id)
            if node_id in self.outputs:
                self.outputs.remove(node_id)
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
                    res[i][i] = 0
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
    def from_adjacency_matrix(cls, matrix):
        """
        Construit et renvoie un multigraphe à partir d'une matrice.
        inputs et outputs restent vides.
        """
        g = cls.empty()
        dim = len(matrix)
        ids = [g.add_node() for _ in range(dim)]
        for i in range(dim):
            for j in range(dim):
                m = matrix[i][j]
                if m > 0:
                    g.add_edgeM(ids[i], ids[j], m)
        return g
    
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
        if form == "free":
            matrix = cls.random_int_matrix(n, bound, null_diag=False)
        elif form == "loop-free":
            matrix = cls.random_int_matrix(n, bound, null_diag=True)
        elif form == "undirected":
            matrix = cls.random_symetric_int_matrix(n, bound, null_diag=False)
        elif form == "loop-free undirected":
            matrix = cls.random_symetric_int_matrix(n, bound, null_diag=True)
        elif form == "oriented":
            matrix = cls.random_oriented_int_matrix(n, bound, null_diag=True)
        elif form == "DAG":
            matrix = cls.random_triangular_int_matrix(n, bound, null_diag=True)
        else:
            raise ValueError(f"Forme de graphe inconnue : {form}")
        g = cls.from_adjacency_matrix(matrix)
        ids = sorted(g.nodes.keys())
        n_inputs = [i for i in ids if not g.nodes[i].get_parents()]
        n_outputs = [i for i in ids if not g.nodes[i].get_children()]
        for i in range(min(inputs, len(n_inputs))):
            g.add_input_node(n_inputs[i])
        for i in range(min(outputs, len(n_outputs))):
            g.add_output_node(n_outputs[i])
        return g
    
    @classmethod
    def identity(cls, n):
        g = cls.empty()
        for i in range(n):
            in_id = g.add_node()
            out_id = g.add_node()
            g.add_input_id(in_id)
            g.add_output_id(out_id)
            g.add_edge(in_id, out_id)
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
    
    def save_as_dot_file(self, path, verbose=False):
        # attribut isInput et isOutput
        with open(path, 'w') as f:
            f.write('Digraph G {\n')
            inputs = self.inputs_ids()
            outputs = self.outputs_ids()
            nodes = self.nodes
            
            for id,node in nodes.items():
                label = node.get_label()
                if verbose:
                    label += f"\\nID : {id}"
                f.write(f"{id} [label=\"{label}\",isInput={id in inputs},isOutput={id in outputs}];\n")
            for id, node in nodes.items():
                for child_id, m  in node.get_children().items():
                    for i in range(m):
                        f.write(f"{id} -> {child_id};\n")
            f.write('}')
            
    @classmethod
    def from_dot_file(self, path):
        with open(path, 'r') as f:
            g = open_digraph.empty()
            while True:
                line = f.readline()
                if "Digraph G {" in line: # Première ligne
                    continue
                if not line or "}" in line: # Fin du fichier
                    break
                # format d'une ligne d'ajout de noeud : id [label="label",isInput=True/False,isOutput=True/False];
                # format d'une ligne d'ajout d'arête : id1 -> id2;
                if "->"  not in line:
                    id, rest = line.split("[")
                    id = int(id)
                    attr = rest.split(",")
                    label = attr[0].split("=")[1][1:-1]
                    is_input = attr[1].split("=")[1] == "True"
                    is_output = attr[2].split("=")[1].split("]")[0] == "True"
                    g.add_node(label, id=id)
                    if is_input:
                        g.add_input_id(id)
                    if is_output:
                        g.add_output_id(id)
                else:
                    src, tgt = line.split("->")
                    src = int(src.strip())
                    tgt = int(tgt.strip().split(";")[0])
                    g.add_edge(src, tgt)
        return g   
    def __eq__(self, other):
        if not isinstance(other, open_digraph):
            return False
        return self.inputs == other.inputs and self.outputs == other.outputs and self.nodes == other.nodes
    def display(self, verbose=False):
        import webbrowser
        self.save_as_dot_file("temp.dot")
        commande = "dot -Tpdf temp.dot -o temp.pdf"
        if verbose:
            print("--- Mode Verbose ---")
            print("Fichier .dot généré : temp.dot")
            print(f"Exécution de la commande : {commande}")
        os.system(commande)
        chemin_pdf = "file://" + os.path.abspath("temp.pdf")
        if verbose:
            print(f"Ouverture du fichier : {chemin_pdf}")
            print("--------------------")
        webbrowser.open(chemin_pdf)
        
    def min_id(self):
        if len(self.nodes) == 0:
            return None
        else:
            return min(self.nodes.keys())
        
    def max_id(self):
        if len(self.nodes) == 0:
            return None
        else:
            return max(self.nodes.keys())
        
    def shift_indices(self, n):
        if n == None:
            return self.copy()
        new_nodes = {}
        for id, node in self.nodes.items():
            new_id = id + n
            new_parents = {parent_id + n: m for parent_id, m in node.get_parents().items()}
            new_children = {child_id + n: m for child_id, m in node.get_children().items()}
            new_nodes[new_id] = node.copy()
            new_nodes[new_id].set_id(new_id)
            new_nodes[new_id].set_parents(new_parents)
            new_nodes[new_id].set_children(new_children)
        new_inputs = [input_id + n for input_id in self.inputs]
        new_outputs = [output_id + n for output_id in self.outputs]
        return open_digraph(new_inputs, new_outputs, new_nodes.values())
    
    def connected_components(self):
        comp_dict = {}
        comp_id = 0
        for node_id in self.get_node_ids():
            if node_id not in comp_dict:
                queue = [node_id]
                comp_dict[node_id] = comp_id
                while queue:
                    current_id = queue.pop(0)
                    current_node = self.get_node_by_id(current_id)
                    voisin = list(current_node.get_parents().keys()) + list(current_node.get_children().keys())
                    for voisin_id in voisin:
                        if voisin_id not in comp_dict:
                            comp_dict[voisin_id] = comp_id
                            queue.append(voisin_id)
                comp_id += 1
        return comp_id, comp_dict
    
    def connected_components_graphs(self):
        (inputs_globaux, outputs_globaux) = (self.inputs_ids().copy(), self.outputs_ids().copy())
        num_comps, comp_dict = self.connected_components()
        graphs = [open_digraph.empty() for _ in range(num_comps)]
        for node_id, c_id in comp_dict.items():
            node_copy = self.get_node_by_id(node_id).copy()
            graphs[c_id].nodes[node_id] = node_copy
        for in_id in self.inputs_ids():
            c_id = comp_dict[in_id]
            graphs[c_id].add_input_id(in_id)
        for out_id in self.outputs_ids():
            c_id = comp_dict[out_id]
            graphs[c_id].add_output_id(out_id)
        return graphs,(inputs_globaux, outputs_globaux)
    
    def merge_nodes(self, id1, id2):
        n1 = self.get_node_by_id(id1)
        n2 = self.get_node_by_id(id2)
        if n1.get_label() != n2.get_label():
            raise ValueError("Pas les mêmes labels")
        n2_parents = n2.get_parents().copy()
        n2_enfants = n2.get_children().copy()
        for p_id, multiplicite in n2_parents.items():
            if p_id == id2:
                self.add_edgeM(id1, id1, multiplicite)
            else :
                self.add_edgeM(p_id, id1, multiplicite)
        for c_id, multiplicite in n2_enfants.items():
            if c_id == id2:
                self.add_edgeM(id1, id1, multiplicite)
            else:
                self.add_edgeM(id1, c_id, multiplicite)
        if id2 in self.inputs and id1 not in self.inputs:
            self.add_input_node(n1)
        if id2 in self.outputs and id1 not in self.outputs:
            self.add_output_node(n2)
        self.remove_node_by_id(id2)
        
    def is_cyclic(self):
        g_copy = self.copy()
        while len(g_copy.get_nodes()) > 0:
            feuille_id = None
            for id_noeud, noeud in g_copy.get_id_node_map().items():
                if noeud.outdegree() == 0:
                    feuille_id = id_noeud
                    break
            if feuille_id is None:
                return True
            g_copy.remove_node_by_id(feuille_id)
        return False
            
        
        
        