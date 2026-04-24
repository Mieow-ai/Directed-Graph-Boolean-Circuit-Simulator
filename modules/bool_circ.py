import sys
import os
import random
from modules.open_digraph import open_digraph


class bool_circ(open_digraph):
    def __init__(self, g):
        super().__init__(g.inputs.copy(), g.outputs.copy(), g.nodes.values())
        if not self.is_well_formed():
            raise ValueError("Le graphe fourni n'est pas un circuit booléen valide (acyclique avec contraintes de degré respectées)")
        
    @classmethod      
    def acyclicToBoolRandom(cls, g, nbInput=None,nbOutput=None):
        if g.is_cyclic():
            raise ValueError("Le graphe n'est pas acyclique, impossible")
        else:
            b = g.copy()
        def labelNoeudBinaire():
            return ["|", "&"][random.randint(0,1)]
        def labelNoeudUnaire():
            return ["~",""][random.randint(0,0)]
        
        for id_noeud, noeud in b.copy().get_id_node_map().items():
        # Si un noeud n'a pas de noeuds parents, c'est une entrée du circuit
        # Auparavant un noeud de copie était créé seulement si le noeud d'entrée avait plus d'un enfant, nous avons finalement choisi de créer un noeud de copie
        # à chaque fois, ce qui simplifie la fusion dans le cas où le nbInput est spécifié
        # Nous supprimons les noeuds de copies inutiles à la fin de la fonction
            if noeud.indegree() == 0 and noeud.outdegree() > 0:
                id_entree = b.add_node()
                b.add_input_id(id_entree)
                b.add_edge(id_entree, id_noeud)
        # Plusieurs parents -> opérateur logique
            elif noeud.indegree() > 1:
                b.get_node_by_id(id_noeud).set_label(labelNoeudBinaire())
                if noeud.outdegree() > 1:
                    id_copie = b.add_node()
                    b.add_edge(id_noeud, id_copie)
                    for id_enfant in noeud.get_children().keys():
                        b.add_edge(id_copie, id_enfant)
                        b.remove_parallel_edges(id_noeud, id_enfant) # On retire entièrement les arêtes
                # Si pas d'enfant c'est aussi une sortie 
                elif noeud.outdegree() == 0:           
                    id_sortie = b.add_node()
                    b.add_output_id(id_sortie)
                    b.add_edge(id_noeud, id_sortie)
            # 1 parent -> c'est soit un noeud de copie soit une sortie
            elif noeud.indegree() == 1:
                a = random.randint(0,1)
                label = ""
                if a == 0:
                    label = ""
                else:
                    label = "~"
                    if noeud.outdegree() > 1:
                        id_copie = b.add_node()
                        b.add_edge(id_noeud, id_copie)
                        for id_enfant in noeud.get_children().keys():
                            b.add_edge(id_copie, id_enfant)
                            b.remove_parallel_edges(id_noeud, id_enfant) # On retire entièrement les arêtes
                    elif noeud.outdegree() == 0:           
                        id_sortie = b.add_node()
                        b.add_output_id(id_sortie)
                        b.add_edge(id_noeud, id_sortie)
                b.get_node_by_id(id_noeud).set_label(label)
            else: # cas 0,0, on enlève le noeud
                b.remove_node_by_id(id_noeud)

        if nbOutput!=None:
            if nbOutput <1:
                raise ValueError("Le nombre de sorties doit être supérieur ou égal à 1")
            # Si il y a plus d'ouputs que ce qui est voulu alors on fusionne des sorties avec un opérateur binaire au hasard
            # On relie directements l'unique parent de chaque sortie à l'opérateur
            while len(b.outputs_ids()) > nbOutput:
                id1, id2 = random.sample(b.outputs_ids(), 2)
                id_parent1 = list(b.get_node_by_id(id1).get_parents().keys())[0]
                id_parent2 = list(b.get_node_by_id(id2).get_parents().keys())[0]
                b.remove_node_by_id(id1)
                b.remove_node_by_id(id2) # Supprime directement les arêtes associées
                id_op = b.add_node()
                b.add_edge(id_parent1, id_op)
                b.add_edge(id_parent2, id_op)
                id_sortie = b.add_node()
                b.add_output_id(id_sortie)
                b.add_edge(id_op, id_sortie)
                node_op = b.get_node_by_id(id_op)
                label = ["|", "&"][random.randint(0,1)]
                node_op.set_label(label)
            while len(b.outputs_ids()) < nbOutput:
                id_noeud = random.choice(list(b.get_id_node_map().keys()))
                if id_noeud in b.outputs_ids():
                    continue
                id_sortie = b.add_node()
                b.add_output_id(id_sortie)
                noeud=b.get_node_by_id(id_noeud)
                # Si jamais le noeud choisi est un noeud d'operation alors il est nécessaire de d'ajouter un noeud de copie
                if noeud.get_label() == "~" or noeud.get_label() == "&" or noeud.get_label() == "|":
                    noeud_copie_id = b.add_node()
                    for id_enfant in list(noeud.get_children().keys()):
                        b.add_edge(noeud_copie_id, id_enfant)
                        b.remove_parallel_edges(id_noeud, id_enfant) 
                    b.add_edge(id_noeud, noeud_copie_id)
                    b.add_edge(noeud_copie_id, id_sortie)
                elif noeud.indegree() == 0: # Si c'est une entrée, elle a un seul enfant
                    id_enfant = list(noeud.get_children().keys())[0] # On récupère l'id du noeud de copie
                    noeud_enfant = b.get_node_by_id(id_enfant)
                    if noeud_enfant.get_label() != "":
                        id_copie = b.add_node()
                        for id_enfant2 in list(noeud.get_children().keys()):
                            b.remove_parallel_edges(id_noeud, id_enfant2)
                            b.add_edge(id_copie, id_enfant2)   
                        b.add_edge(id_noeud, id_copie)
                        b.add_edge(id_copie, id_sortie)
                    else: #Sinon l'enfant est un noeud de copie, on peut directement le relier à la sortie
                        b.add_edge(id_enfant, id_sortie)
                #Sinon c'est un noeud de copie, on peut directement le relier à la sortie
                else:
                    b.add_edge(id_noeud, id_sortie)
        if nbInput!=None:
            if nbInput <1:
                raise ValueError("Le nombre d'entrées doit être supérieur ou égal à 1")
            # Si il y a plus d'inputs que ce qui est voulu alors on fusionne des entrées
            while len(b.inputs_ids()) > nbInput:
                id1, id2 = random.sample(b.inputs_ids(), 2)
                b.merge_nodes(id1, id2)
                if(len(b.get_node_by_id(id1).get_children().keys()) != 2):
                    raise ValueError(f"Erreur defusion des noeuds d'entrée, le noeud fusionné n'a pas exactement 2 enfants ({len(b.get_node_by_id(id1).get_children().keys())})")
                enfant1 = list(b.get_node_by_id(id1).get_children().keys())[0]
                enfant2 = list(b.get_node_by_id(id1).get_children().keys())[1]
                # On fusionne les noeuds de copie pour que l'entrée n'ait qu'un seul enfant
                b.merge_nodes(enfant1, enfant2)
                b.remove_edge(id1, enfant1) #La fusion double les arêtes, on en retire une

            while len(b.inputs_ids()) < nbInput:
                nv_id = b.add_node()
                b.add_input_id(nv_id)
                # On veut un noeud qui ne soit pas un noeud d'entrée, de sortie ou de copie 
                id_noeud = random.choice([node for node in b.get_id_node_map().keys() if node not in b.inputs_ids() and node not in b.outputs_ids() and b.get_node_by_id(node).get_label() in ["&", "~", "|"]])
                id_parent = list(b.get_node_by_id(id_noeud).get_parents().keys())[0]
                b.remove_parallel_edges(id_parent, id_noeud)
                noeud_binaire_id = b.add_node()
                b.add_edge(id_parent, noeud_binaire_id)
                b.add_edge(noeud_binaire_id, id_noeud)
                b.add_edge(nv_id, noeud_binaire_id)
                node_binaire = b.get_node_by_id(noeud_binaire_id)
                label = ["|", "&"][random.randint(0,1)]
                node_binaire.set_label(label)
        # On retire les noeuds de copie inutiles
        for id_noeud, noeud in b.copy().get_id_node_map().items():
            if noeud.get_label() == "" and noeud.indegree() == 1 and noeud.outdegree() == 1:
                id_parent = list(noeud.get_parents().keys())[0]
                id_enfant = list(noeud.get_children().keys())[0]
                b.add_edge(id_parent, id_enfant)
                b.remove_node_by_id(id_noeud)

        return bool_circ(b)

    
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
    
    @classmethod      
    def adder(cls,n):
        if(n==0):
            return bool_circ.adder0()
        else:
            adder1 = bool_circ.adder(n-1)
            adder2 = bool_circ.adder(n-1)
            b = adder1.compo_parallele(adder2)
            # l'adder de taille n a 2 registre de taille 2^n et un retenue entrante
            # on sépare chaque registre en bits de poids faible et bits de poids fort
            # Chaque adder a 2^(n-1) bits de poids fort (0 à 2^(n-1) -1) 2^n-1 bits de poids faible et une retenue 
            k = 2**(n-1)
            #On récupére les inputs après la compo (pour avoir le shift_indices)
            inputsAdder1 = b.inputs_ids()[0:2*k + 1]
            inputsAdder2 = b.inputs_ids()[2*k+1:4*k+2]
            inputs_id = inputsAdder1[0:k]
            inputs_id += inputsAdder2[0:k]
            inputs_id += inputsAdder1[k:2*k]
            inputs_id += inputsAdder2[k:2*k]
            retenueEntranteAdder2 = inputsAdder2[2**(n)]
            inputs_id.append(retenueEntranteAdder2)
            b.set_inputs(inputs_id)
            # Pour les sorties il suffit d'enlever la retenue sortante de l'adder 2
            # l'adder 1 a une retenue sortante, 2^n-1 bits de sortie, puis il y a la retenue de l'adder 2
            outputs = b.outputs_ids()
            retenuesortanteAdder2 = outputs[2**(n-1)+1]
            outputs.remove(retenuesortanteAdder2)
            b.set_outputs(outputs)
            # On relie la retenue sortante de l'adder 2 à la retenue entrante de l'adder 1
            retenueEntranteAdder1 = inputsAdder1[2**(n)]
            b.add_edge(retenuesortanteAdder2, retenueEntranteAdder1)
            return b

    @classmethod
    def adder0(cls):
        b = bool_circ(open_digraph.empty())
        entree1 = b.add_node()
        b.add_input_id(entree1)
        entree2 = b.add_node()
        b.add_input_id(entree2)
        retenueEntrante = b.add_node()
        b.add_input_id(retenueEntrante)
        retenueSortante = b.add_node()
        b.add_output_id(retenueSortante)
        sortie1 = b.add_node()
        b.add_output_id(sortie1)
        copie1 = b.add_node()
        b.add_edge(entree1, copie1)
        copie2 = b.add_node()
        b.add_edge(entree2, copie2)
        copieRetenueEntrante = b.add_node()
        b.add_edge(retenueEntrante, copieRetenueEntrante)
        xor1 = b.add_node()
        b.add_edge(copie1, xor1)
        b.add_edge(copie2, xor1)
        b.get_node_by_id(xor1).set_label("^")
        copieXor1 = b.add_node()
        b.add_edge(xor1, copieXor1)
        and1 = b.add_node()
        b.add_edge(copie1, and1)
        b.add_edge(copie2, and1)
        b.get_node_by_id(and1).set_label("&")
        and2 = b.add_node()
        b.add_edge(copieXor1, and2)
        b.add_edge(copieRetenueEntrante, and2)
        b.get_node_by_id(and2).set_label("&")        
        xor2 = b.add_node()
        b.add_edge(copieXor1, xor2)
        b.add_edge(copieRetenueEntrante, xor2)
        b.get_node_by_id(xor2).set_label("^")
        or1 = b.add_node()
        b.add_edge(and1, or1)
        b.add_edge(and2, or1)
        b.get_node_by_id(or1).set_label("|")
        b.add_edge(or1, retenueSortante)
        b.add_edge(xor2, sortie1)
        return b
    
    @classmethod
    def registre(cls,entier, n=8):
        if(entier >= 2**n):
            raise ValueError("Entier trop grand")
        binaire = bin(entier)[2:]
        zeros = ""
        if(len(binaire)<n):
            zeros = "0" * (n-len(binaire))
        binaire = zeros+binaire
        b = bool_circ(open_digraph.empty())
        for i in binaire:
            idN = b.add_node(label=i)
            idS = b.add_node()
            b.add_edge(idN,idS)
            b.add_output_id(idS)
        return b
    
    def simplifier_copie(self):
        b = self.copy()
        for id, noeud in b.get_id_node_map().items():
            if noeud.get_label() == "" and noeud.indegree() == 1 and noeud.outdegree() > 0:
                id_enfants = list(noeud.get_children().keys())
                id_parent = list(noeud.get_parents().keys())[0]
                parent = b.get_node_by_id(id_parent)
                label = parent.get_label()
                if(label == "0" or label == "1"):
                    for id_enfant in id_enfants:
                        idN = b.add_node(label=label)
                        b.add_edge(idN, id_enfant)
                    b.remove_node_by_id(id)
                    b.remove_node_by_id(id_parent)
        return b
    
    def simplifier_non(self):
        b = self.copy()
        for id, noeud in b.get_id_node_map().items():
            if noeud.get_label() == "~":
                id_parent = list(noeud.get_parents().keys())[0]
                parent = b.get_node_by_id(id_parent)
                label = parent.get_label()
                if(label == "0"):
                    parent.set_label("1")
                    b.add_edge(parent.get_id(), list(noeud.get_children().keys())[0])
                    b.remove_node_by_id(id)
                elif(label == "1"):
                    parent.set_label("0")
                    b.add_edge(parent.get_id(), list(noeud.get_children().keys())[0])
                    b.remove_node_by_id(id)
        return b
                
    def simplifier_et(self):
        b = self.copy()
        for id, noeud in b.get_id_node_map().items():
            if noeud.get_label() == "&":
                parents = list(noeud.get_parents().keys())
                if any(b.get_node_by_id(parent).get_label() == "0" for parent in parents):
                    idN = b.add_node(label="0")
                    b.add_edge(idN, list(noeud.get_children().keys())[0])
                    b.remove_node_by_id(id)
                else:
                    for parent in parents:
                        p = b.get_node_by_id(parent)
                        if p.get_label() == "1":
                            b.remove_node_by_id(parent)
        return b
                            
    @classmethod
    def somme(cls, entier1, entier2):
        registre1 = bool_circ.registre(entier1)
        registre2 = bool_circ.registre(entier2)
        registres= registre1.compo_parallele(registre2)
        #On ajoute une retenue vide
        retenue = registres.add_node()
        registres.get_node_by_id(retenue).set_label("0")
        retenueSortie = registres.add_node()
        registres.add_output_id(retenueSortie)
        registres.add_edge(retenue, retenueSortie)
        adder3 = bool_circ.adder(3)
        print(len(registres.outputs_ids()))
        print(len(adder3.inputs_ids()))
        circuit = registres.compo_sequentielle(adder3)
        tri_topo = circuit.tri_topologique()
        for niveau in tri_topo:
            for id in niveau:
                node = circuit.get_node_by_id(id)
                if node.get_label() == "0" or node.get_label() == "1":
                    continue
                elif node.get_label() == "" or node.get_label()==None: #Noeud de copie ou de sortie
                    if len(node.get_parents()) != 1:
                       raise ValueError("Un noeud de copie ou de sortie doit avoir exactement un parent")
                    id_parent= list(node.get_parents().keys())[0] # un seul parent
                    parent = circuit.get_node_by_id(id_parent)
                    node.set_label(parent.get_label())
                elif node.get_label() == "~":
                    if len(node.get_parents()) != 1:
                       raise ValueError("Un noeud unaire doit avoir exactement un parent")
                    id_parent= list(node.get_parents().keys())[0] # un seul parent
                    parent = circuit.get_node_by_id(id_parent)
                    if parent.get_label() == "0":
                        node.set_label("1")
                    elif parent.get_label() == "1":
                        node.set_label("0")
                    else:
                        raise ValueError("Lors de l'évaluation du noeud, son parent doit avoir une valeur binaire")
                elif node.get_label() == "&":
                    if len(node.get_parents()) != 2:
                       raise ValueError("Un noeud binaire doit avoir exactement deux parents")
                    id_parent1= list(node.get_parents().keys())[0]
                    id_parent2= list(node.get_parents().keys())[1]
                    parent1 = circuit.get_node_by_id(id_parent1)
                    parent2 = circuit.get_node_by_id(id_parent2)
                    if parent1.get_label() not in ["0", "1"] or parent2.get_label() not in ["0", "1"]:
                        raise ValueError("Lors de l'évaluation du noeud, ses parents doivent avoir des valeurs binaires")
                    if parent1.get_label() == "0" or parent2.get_label() == "0":
                        node.set_label("0")
                    #Sinon les deux sont à 1
                    else:
                        node.set_label("1")
                elif node.get_label() == "|":
                    if len(node.get_parents()) != 2:
                       raise ValueError("Un noeud binaire doit avoir exactement deux parents")
                    id_parent1= list(node.get_parents().keys())[0]
                    id_parent2= list(node.get_parents().keys())[1]
                    parent1 = circuit.get_node_by_id(id_parent1)
                    parent2 = circuit.get_node_by_id(id_parent2)
                    if parent1.get_label() not in ["0", "1"] or parent2.get_label() not in ["0", "1"]:
                        raise ValueError("Lors de l'évaluation du noeud, ses parents doivent avoir des valeurs binaires")
                    if parent1.get_label() == "1" or parent2.get_label() == "1":
                        node.set_label("1")
                    #Sinon les deux sont à 0
                    else:
                        node.set_label("0")
                elif node.get_label() == "^": #XOR
                    if len(node.get_parents()) != 2:
                       raise ValueError("Un noeud binaire doit avoir exactement deux parents")
                    id_parent1= list(node.get_parents().keys())[0]
                    id_parent2= list(node.get_parents().keys())[1]
                    parent1 = circuit.get_node_by_id(id_parent1)
                    parent2 = circuit.get_node_by_id(id_parent2)
                    if parent1.get_label() not in ["0", "1"] or parent2.get_label() not in ["0", "1"]:
                        raise ValueError("Lors de l'évaluation du noeud, ses parents doivent avoir des valeurs binaires")
                    if (parent1.get_label() == "0" and parent2.get_label() == "0") or (parent1.get_label() == "1" and parent2.get_label() == "1"):
                        node.set_label("0")
                    #Sinon une des deux est à 1 et l'autre à 0
                    else:
                        node.set_label("1")
                else:
                    raise ValueError("Label de noeud invalide lors de l'évaluation du circuit")
        string_sortie = ""
        for id in circuit.outputs_ids():
            node = circuit.get_node_by_id(id)
            if node.get_label() not in ["0", "1"]:
                raise ValueError("Lles noeuds de sortie doivent avoir des valeurs binaires")
            string_sortie += node.get_label()
        
        return int(string_sortie, 2)