from open_digraph import open_digraph

class bool_circ(open_digraph):
    def __init__(self, g):
        super().__init__(g.inputs, g.outputs, g.nodes.values())
        if not self.is_well_formed():
            raise ValueError("Le graphe fourni n'est pas un circuit booléen valide (acyclique avec contraintes de degré respectées)")
        
        
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
    
    def is_well_formed(self):
        if self.is_cyclic():
            return False
        for id_noeud, noeud in self.get_id_node_map().items():
            for id_parent, multiplicite in noeud.get_parents().items():
                if id_parent not in self.get_id_node_map():
                    return False
                if self.get_nodes()[id_parent].outdegree() < multiplicite:
                    return False
            for id_enfant, multiplicite in noeud.get_children().items():
                if id_enfant not in self.get_nodes():
                    return False
                if self.get_nodes()[id_enfant].indegree() < multiplicite:
                    return False
        return True

    def Compo_parallele(self, other):
        f = self.copy()
        g = other.shift_indices(f.max_id()+1)
        inputs = f.inputs_ids() + g.inputs_ids()
        outputs = f.outputs_ids() + g.outputs_ids()
        nodes = f.get_nodes() + g.get_nodes()
        return bool_circ(open_digraph(inputs, outputs, nodes))
    
    def Compo_sequentielle(self, other):
        if (len(self.outputs_ids()) != len(other.inputs_ids())):
            raise ValueError("Il faut avoir le même nombre de sorties dans le premier circuit et d'entrées dans le second")
        f = self.copy()
        g = other.shift_indices(f.max_id()+1)
        inputs = f.inputs_ids()
        outputs = g.outputs_ids()
        foutputs = f.outputs_ids()
        ginputs = g.inputs_ids()
        nodes_list = f.get_nodes() + g.get_nodes()
        combined = open_digraph(inputs, outputs, nodes_list)
        for i in range(len(foutputs)):
            fid = foutputs[i]
            gid = ginputs[i]
            noeudsortie = f.get_node_by_id(fid)
            noeudentree = g.get_node_by_id(gid)
            combined.remove_node_by_id(fid)
            combined.remove_node_by_id(gid)
            combined.add_edge(noeudsortie.get_parents()[0], noeudentree.get_children()[0])
        return bool_circ(combined)
            
         