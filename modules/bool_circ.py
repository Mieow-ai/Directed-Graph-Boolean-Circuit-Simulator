from open_digraph import open_digraph

class bool_circ(open_digraph):
    def __init__(self, g):
        super().__init__(g.inputs, g.outputs, g.nodes)
        if not self.is_well_formed():
            raise ValueError("Le graphe fourni n'est pas un circuit booléen valide (acyclique avec contraintes de degré respectées)")
        
        
    def is_cyclic(self):
        g_copy = self.copy()
        while len(g_copy.get_nodes()) > 0:
            feuille_id = None
            for id_noeud, noeud in g_copy.get_nodes().items():
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
        for id_noeud, noeud in self.get_nodes().items():
            for id_parent, multiplicite in noeud.get_parents().items():
                if id_parent not in self.get_nodes():
                    return False
                if self.get_nodes()[id_parent].outdegree() < multiplicite:
                    return False
            for id_enfant, multiplicite in noeud.get_children().items():
                if id_enfant not in self.get_nodes():
                    return False
                if self.get_nodes()[id_enfant].indegree() < multiplicite:
                    return False
        return True
    
    
            
         