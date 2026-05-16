import os 
from modules import open_digraph_mx as mx
# MARK: - Node
class node:
    """
    Classe qui représente un noeud dans un graphe.
    """
    def __init__(self, identity, label, parents, children):
        """
        Initialise le noeud.
        param identity: int, l'ID unique du noeud dans le graphe.
        param label: string, l'étiquette du noeud.
        param parents: dict (int->int), relie l'ID d'un parent à sa multiplicité.
        param children: dict (int->int), relie l'ID d'un enfant à sa multiplicité.
        """
        self.id = identity
        self.label = label
        self.parents = parents
        self.children = children

    def __str__(self):
        """Affiche le noeud de manière lisible."""
        s = f"Node : {self.id}; label : {self.label}; parents : " + self.parents.__str__() + "; children :" + self.children.__str__() + ";\n"
        return s
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        """Permet de vérifier si deux noeuds sont strictement identiques."""
        if not isinstance(other, node):
            return False
        return self.id == other.id and self.label == other.label and self.parents == other.parents and self.children == other.children
    
    def copy(self):
        """
        Renvoie une copie profonde du noeud.
        param self: Description
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
        """Ajoute un enfant ou augmente le nombre de liens vers lui s'il y est déjà."""
        if child_id in self.children:
            self.children[child_id] += multiplicity
        else:
            self.children[child_id] = multiplicity
    def add_parent_id(self, parent_id, multiplicity):
        """Ajoute un parent ou augmente le nombre de liens depuis lui s'il y est déjà."""
        if parent_id in self.parents:
            self.parents[parent_id] += multiplicity
        else:
            self.parents[parent_id] = multiplicity
            
    # Méthodes
    def remove_parent_once(self, parent_id):
        """Retire un seul lien avec un parent. S'il n'y est pas on lève l'erreur, s'il y est avec une multiplicité de 1 on le retire, s'il y est avec une multiplicité superieur à 1 on decrease la multiplicité"""
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
        """Retire un seul lien avec un enfant. S'il n'y est pas on lève l'erreur, s'il y est avec une multiplicité de 1 on le retire, s'il y est avec une multiplicité superieur à 1 on decrease la multiplicité"""
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
        """Retire complètement un parent"""
        if parent_id in self.parents:
            del self.parents[parent_id]
        else:
            raise ValueError(f"Parent_id {parent_id} pas dans node {self.id}")
    
    def remove_child_id(self, child_id):
        """Retire complètement un enfant"""
        if child_id in self.children:
            del self.children[child_id]
        else:
            raise ValueError(f"Child_id {child_id} pas dans node {self.id}")
    
    def indegree(self):
        """Retourne le degré entrant du noeud"""
        return sum(self.parents.values())
    
    def outdegree(self):
        """Retourne le degré sortant du noeud"""
        return sum(self.children.values())
    
    def degree(self):
        """Retourne le degré total du noeud"""
        return self.indegree() + self.outdegree()
        

    
# MARK: - Digraph
class open_digraph(mx.MatrixMixin, mx.DisplayMixin, mx.CompositionMixin, mx.AlgoMixin): # for open directed graph
    """
    Classe représentant un graphe orienté ouvert.
    Hérite des Mixins
    """
    def __init__(self, inputs, outputs, nodes):
        """
        Initialise le graphe.
        param inputs: liste d'ID (les entrées)
        param outputs: liste d'ID (les sorties)
        param nodes: itérable de noeuds
        """
        self.inputs = inputs
        self.outputs = outputs
        self.nodes = {node.id:node for node in nodes} # self.nodes: <int,node> dict

    def __str__(self):
        """ Affichage du graphe """
        s = "Graph :\n"
        s += "Inputs : " + self.inputs.__str__() + "\n"
        s += "Outputs : " + self.outputs.__str__() + "\n"
        s += "Nodes : \n"
        for node in self.nodes.values():
            s += node.__str__()
        return s
    
    def __repr__(self):
        """ Affichage du graphe """
        return self.__str__()
    
    def __eq__(self, other):
        """ Test d'égalité entre deux graphes """
        if not isinstance(other, open_digraph):
            return False
        return self.inputs == other.inputs and self.outputs == other.outputs and self.nodes == other.nodes
    
    @classmethod
    def empty(cls):
        """
        Renvoie un graphe vide.
        """
        return cls([],[],[])
    
    def copy(self):
        """
        Renvoie une copie profonde du graphe.
        """
        return self.__class__(self.inputs.copy(), self.outputs.copy(), [node.copy() for node in self.nodes.values()])
    
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
    def remove_output_id(self,output_id):
        self.outputs.remove(output_id)
    def remove_input_id(self,input_id):
        self.inputs.remove(input_id)
    
    # Méthodes ajouts
    def new_id(self):
        """ Génère un nouvel ID unique pour un noeud """
        if len(self.nodes) == 0:
            return 0
        else:
            return max(self.nodes.keys()) + 1
    
    def add_edge(self, src, tgt):
        """ Ajoute une arête entre src et tgt """
        self.nodes[src].add_child_id(tgt, 1)
        self.nodes[tgt].add_parent_id(src, 1)
    
    def add_edgeM(self, src, tgt, multiplicity):
        """ Ajoute une arête entre src et tgt avec une multiplicité """
        self.nodes[src].add_child_id(tgt, multiplicity)
        self.nodes[tgt].add_parent_id(src, multiplicity)
    
    def add_edges(self, edges):
        """ Ajoute des arêtes entre src et tgt """
        for src, tgt in edges:
            self.add_edge(src, tgt)
            
    def add_node(self, label='', parents=None, children=None, id=None):
        """ Ajoute un noeud au graphe et renvoie l'ID de ce noeud ajouté """
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
    
    def add_input_node(self, id, label=''):
        """ Crée une entrée et ajoute une arête entre l'entrée et le noeud id """
        if id not in self.nodes.keys():
            raise ValueError(f"Le noeud {id} n'existe pas dans le graphe")
        if id in self.outputs:
            raise ValueError(f"Le noeud {id} est déjà un noeud de sortie")
        new_id = self.add_node(label, {}, {})
        self.add_input_id(new_id)
        self.add_edge(new_id, id)
        
    def add_output_node(self, id, label=''):
        """ Crée une sortie et ajoute une arête entre le noeud id et la sortie """
        if id not in self.nodes.keys():
            raise ValueError(f"Le noeud {id} n'existe pas dans le graphe")
        if id in self.inputs:
            raise ValueError(f"Le noeud {id} est déjà un noeud d'entrée")
        new_id = self.add_node(label, {}, {})
        self.add_output_id(new_id)
        self.add_edge(id, new_id)
    
    # Méthodes de retrait
    
    def remove_edge(self, src, tgt):
        """ Retire une arête entre src et tgt """
        self.nodes[src].remove_child_once(tgt)
        self.nodes[tgt].remove_parent_once(src)
    
    def remove_parallel_edges(self, src, tgt):
        """ Retire toutes les arêtes entre src et tgt """
        self.nodes[src].remove_child_id(tgt)
        self.nodes[tgt].remove_parent_id(src)
    
    def remove_node_by_id(self, node_id):
        """ Retire un noeud du graphe par son id """
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
        """ Retire plusieurs arêtes du graphe """
        for src, tgt in edges:
            self.remove_edge(src, tgt)
    
    def remove_several_parallel_edges(self, edges):
        """ Retire plusieurs arêtes parallèles du graphe """
        for src, tgt in edges:
            self.remove_parallel_edges(src, tgt)
    
    def remove_nodes_by_id(self, node_ids):
        """ Retire plusieurs noeuds du graphe par leur id """
        for node_id in node_ids:
            self.remove_node_by_id(node_id)
            
    def __delitem__(self, node_id):
        """ Retire un noeud du graphe par son id """
        self.remove_node_by_id(node_id)
    
    # Autres méthodes
    def well_formed(self):
        """ Vérifie si le graphe est bien formé """
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
        """ Vérifie si le graphe est bien formé et lève une exception s'il ne l'est pas """
        if not self.well_formed():
            raise ValueError("Graphe pas bien formé")
        
    
    @classmethod
    def identity(cls, n):
        """ Renvoie un graphe avec n entrées et n sorties """
        g = cls.empty()
        for i in range(n):
            in_id = g.add_node()
            out_id = g.add_node()
            g.add_input_id(in_id)
            g.add_output_id(out_id)
            g.add_edge(in_id, out_id)
        return g
    
    # A quoi ça sert ? 
    def graph_to_dict(self):
        """ Renvoie un dictionnaire qui associe chaque noeud du graphe à un entier """
        res = {}
        for i, node_id in enumerate(self.nodes.keys()):
            res[node_id] = i
        return res
        
    def min_id(self):
        """ Renvoie le plus petit ID du graphe """
        if len(self.nodes) == 0:
            return None
        else:
            return min(self.nodes.keys())
        
    def max_id(self):
        """ Renvoie le plus grand ID du graphe """
        if len(self.nodes) == 0:
            return None
        else:
            return max(self.nodes.keys())
        
    
        
    
            
        
        
        