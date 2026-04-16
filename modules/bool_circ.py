import sys
import os
from modules.open_digraph import open_digraph


class bool_circ(open_digraph):
    def __init__(self, g):
        super().__init__(g.inputs.copy(), g.outputs.copy(), g.nodes.values())
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
        node_map = self.get_id_node_map()
        for id_noeud, noeud in node_map.items():
            for id_parent, multiplicite in noeud.get_parents().items():
                if id_parent not in node_map:
                    return False
                if node_map[id_parent].outdegree() < multiplicite:
                    return False
            for id_enfant, multiplicite in noeud.get_children().items():
                if id_enfant not in node_map:
                    return False
                if node_map[id_enfant].indegree() < multiplicite:
                    return False
        return True

    def compo_parallele(self, other):
        f = self.copy()
        shift = (f.max_id() + 1) if f.max_id() is not None else 0
        g = other.shift_indices(shift)
        inputs = f.inputs_ids() + g.inputs_ids()
        outputs = f.outputs_ids() + g.outputs_ids()
        nodes = f.get_nodes() + g.get_nodes()
        return bool_circ(open_digraph(inputs, outputs, nodes))
    
    def compo_sequentielle(self, other):
        if (len(self.outputs_ids()) != len(other.inputs_ids())):
            raise ValueError("Graphes incompatibles (le nombre de sorties de f doit être égal au nombre d'entrées de g)")
        f = self.copy()
        shift = (f.max_id() + 1) if f.max_id() is not None else 0
        g = other.shift_indices(shift)
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
            parents = list(noeudsortie.get_parents().keys())
            children = list(noeudentree.get_children().keys())
            combined.remove_node_by_id(fid)
            combined.remove_node_by_id(gid)
            if parents and children:
                combined.add_edge(parents[0], children[0])
        return bool_circ(combined)
    
    def longueurs_dfs(self, src, direction = 1) :
        prev = {}
        dist = {}
        if direction == 1:
            self.longueurs_aux(src, prev,dist, 0, None)
            return prev,dist
        elif direction == -1:
            self.longueurs_aux2(src, prev,dist, 0, None)
            return prev,dist
        else:
            prev1, dist1 = self.longueurs_dfs(src, direction = 1)
            prev2, dist2 = self.longueurs_dfs(src, direction = -1)
            return prev1 | prev2,  dist1 | dist2
        
                
    def longueurs_aux(self, src, prev,dist, current_dist, parent):
            childs = self.get_node_by_id(src).get_children()
            if src not in dist or dist[src] > current_dist:
                dist[src] = current_dist
                prev[src] = parent
                for child in childs.keys():
                    self.longueurs_aux(child, prev, dist, current_dist + 1, src)
                
    def longueurs_aux2(self, src, prev,dist, current_dist, enfant):
            parents = self.get_node_by_id(src).get_parents()
            if src not in dist or dist[src] > current_dist:
                dist[src] = current_dist
                prev[src] = enfant
                for parent in parents.keys():
                    self.longueurs_aux2(parent, prev, dist, current_dist + 1, src)         

    def longueurs_bfs(self, src, direction=1, tgt = None):
        dist = {src: 0}
        prev = {}
        queue = [src]
        while queue:
            current = queue.pop(0)
            noeud = self.get_node_by_id(current)
            voisins = []
            if direction == 1 or direction is None:
                voisins.extend(list(noeud.get_children().keys()))
            if direction == -1 or direction is None:
                voisins.extend(list(noeud.get_parents().keys()))
            for voisin in voisins:
                if voisin not in dist:
                    dist[voisin] = dist[current] + 1
                    prev[voisin] = current
                    if voisin == tgt:
                        return dist, prev
                    queue.append(voisin)
        return dist, prev
    
    def shortest_path(self, src, tgt, direction = 1):
        dist, prev = self.longueurs_bfs(src, direction, tgt)
        distance = dist[tgt] if tgt in dist else None
        path = []
        if distance is not None:
            current = tgt
            while current != src:
                path.append(current)
                current = prev[current]
            path.append(src)
            path.reverse()
        return distance, path

    def ancetres_communs_dist(self, id1, id2):
        dist1, _ = self.longueurs_bfs(id1, direction=-1)
        dist2, _ = self.longueurs_bfs(id2, direction=-1)
        resultat = {}
        for id in dist1.keys():
            if id in dist2:
                # ancêtre commun
                resultat[id] = (dist1[id], dist2[id])
        return resultat

    # Tri topologique "compréssé vers le haut"                            
    # On réutilise une partie du code de is_cyclic
    def tri_topologique(self):
        g_copy = self.copy()
        res = []
        while len(g_copy.get_nodes()) > 0:
            cofeuilles = set()
            for id_noeud, noeud in g_copy.get_id_node_map().items():
                if noeud.indegree() == 0:
                    cofeuilles.add(id_noeud)
            if not cofeuilles:
                raise ValueError("Le graphe est cyclique, tri topologique impossible")
            # On retire les feuilles après avoir trouver tout le niveau courant
            res.append(cofeuilles)
            for id in cofeuilles:
                g_copy.remove_node_by_id(id)
        return res
    
    def profondeur_noeud(self, id_noeud):
        tri = self.tri_topologique()
        for i in range(len(tri)):
            if id_noeud in tri[i]:
                return i+1
        raise ValueError("l'id n'est pas dans le graphe")
    def profondeur(self):
        tri = self.tri_topologique()
        return len(tri)
    
    def longest_path(self,u,v):
        tri_topo = self.tri_topologique()
        prof_u = self.profondeur_noeud(u)
        prof_v = self.profondeur_noeud(v)
        if(prof_u >= prof_v):
            return None
        else:
            dist = {u : 0}
            prev = {}
            for profondeur in range(prof_u, prof_v):
                for id in tri_topo[profondeur]: 
                    parents = self.get_node_by_id(id).get_parents()
                    for id_parent in parents:
                        if id_parent in dist.keys():
                            if(id in dist.keys()):
                                if(dist[id_parent]+1>dist[id]):
                                    dist[id] = dist[id_parent]+1
                                    prev[id] = id_parent
                            else:
                                dist[id] = dist[id_parent]+1
                                prev[id] = id_parent   
                    if id == v:
                        path = []
                        distance = dist[v] if v in dist else None 
                        if distance is not None:
                            current = v
                            while current != u:
                                path.append(current)
                                current = prev[current]
                            path.append(u)
                            path.reverse()
                            return distance, path
        return None
      
    @classmethod      
    def formula_to_tree(cls, s):
        g = open_digraph.empty()
        b = bool_circ(g)

        current_node_id = b.add_node()
        current_node = b.get_node_by_id(current_node_id)
        sortie_id = b.add_node()
        b.add_output_id(sortie_id)
        b.add_edge(current_node_id, sortie_id)
        
        s2 = ""
        for char in s:
            if char == '(':
                current_node.set_label(current_node.get_label() + s2)
                nouveau_parent_id = b.add_node()
                b.add_edge(nouveau_parent_id,current_node.get_id())
                current_node = b.get_node_by_id(nouveau_parent_id)
                s2 = ""
            elif char == ')':
                current_node.set_label(current_node.get_label() + s2)
                current_node = b.get_node_by_id(list(current_node.get_children().keys())[0])
                s2 = ""
            else:
                s2 += char
                
        tri_topo = b.tri_topologique()
        niveau1_id = tri_topo[0]
        
        liste_ids = list(niveau1_id)
        for id1 in liste_ids:
            for id2 in liste_ids:
                if id1 != id2 and id1 in niveau1_id and id2 in niveau1_id:
                    if b.get_node_by_id(id1).get_label() == b.get_node_by_id(id2).get_label():
                        b.merge_nodes(id1, id2)
                        niveau1_id.remove(id2)
        # On modifie pour ajouter des noeuds d'entrées liées aux noeuds de copies
        tri_topo = b.tri_topologique()
        niveau1_id = tri_topo[0]
        liste_ids = list(niveau1_id)
        inputs_list = []
        for id1 in liste_ids:
            input_id = b.add_node()
            b.add_input_id(input_id)
            b.add_edge(input_id, id1)
            node_id1 = b.get_node_by_id(id1)
            inputs_list.append(node_id1.get_label())
            node_id1.set_label("") 
               
        return b,inputs_list
    
    @classmethod      
    def formula_to_treeExtend(cls, *args):
        g = open_digraph.empty()
        b = bool_circ(g)

      
        
        for s in args:
            current_node_id = b.add_node()
            current_node = b.get_node_by_id(current_node_id)
            sortie_id = b.add_node()
            b.add_output_id(sortie_id)
            b.add_edge(current_node_id, sortie_id)
            s2 = ""
            for char in s:
                if char == '(':
                    current_node.set_label(current_node.get_label() + s2)
                    nouveau_parent_id = b.add_node()
                    b.add_edge(nouveau_parent_id,current_node.get_id())
                    current_node = b.get_node_by_id(nouveau_parent_id)
                    s2 = ""
                elif char == ')':
                    current_node.set_label(current_node.get_label() + s2)
                    current_node = b.get_node_by_id(list(current_node.get_children().keys())[0])
                    s2 = ""
                else:
                    s2 += char
                
        tri_topo = b.tri_topologique()
        niveau1_id = tri_topo[0]
        
        liste_ids = list(niveau1_id)
        for id1 in liste_ids:
            for id2 in liste_ids:
                if id1 != id2 and id1 in niveau1_id and id2 in niveau1_id:
                    if b.get_node_by_id(id1).get_label() == b.get_node_by_id(id2).get_label():
                        b.merge_nodes(id1, id2)
                        niveau1_id.remove(id2)
        # On modifie pour ajouter des noeuds d'entrées liées aux noeuds de copies
        tri_topo = b.tri_topologique()
        niveau1_id = tri_topo[0]
        liste_ids = list(niveau1_id)
        inputs_list = []
        for id1 in liste_ids:
            input_id = b.add_node()
            b.add_input_id(input_id)
            b.add_edge(input_id, id1)
            node_id1 = b.get_node_by_id(id1)
            inputs_list.append(node_id1.get_label())
            node_id1.set_label("") 
               
        return b,inputs_list
        