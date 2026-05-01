import sys
import os
import random
from modules.open_digraph import open_digraph


class bool_circ(open_digraph):
    def __init__(self, inputs, outputs=None, nodes=None):
        if outputs is None and nodes is None:
            g = inputs
            super().__init__(g.inputs.copy(), g.outputs.copy(), g.nodes.values())
        else:
            super().__init__(inputs, outputs, nodes)
            
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

   
    def ancetres_communs_dist(self, id1, id2):
        dist1, _ = self.longueurs_bfs(id1, direction=-1)
        dist2, _ = self.longueurs_bfs(id2, direction=-1)
        resultat = {}
        for id in dist1.keys():
            if id in dist2:
                # ancêtre commun
                resultat[id] = (dist1[id], dist2[id])
        return resultat

    
      
    @classmethod      
    def formula_to_tree(cls, s):
        b = cls.empty()
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
        b = cls.empty()

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
            retenueEntrante = inputsAdder1[2**(n)]
            inputs_id.append(retenueEntrante)
            b.set_inputs(inputs_id)
            # Pour les sorties il suffit d'enlever la retenue sortante de l'adder 2
            # l'adder 1 a une retenue sortante, 2^n-1 bits de sortie, puis il y a la retenue de l'adder 2
            outputs = b.outputs_ids()
            retenuesortante = outputs[2**(n-1)+1]
            outputs.remove(retenuesortante)
            b.set_outputs(outputs)
            # On relie la retenue sortante de l'adder 2 à la retenue entrante de l'adder 1
            b.add_edge(retenuesortante, retenueEntrante)
            return b

    @classmethod
    def adder0(cls):
        b = cls.empty()
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
    def registre(cls, entier, n=8):
        if(entier >= 2**n):
            raise ValueError("Entier trop grand")
        binaire = bin(entier)[2:]
        zeros = ""
        if(len(binaire)<n):
            zeros = "0" * (n-len(binaire))
        binaire = zeros+binaire
        b = cls.empty()
        for i in binaire:
            idN = b.add_node(label=i)
            idS = b.add_node()
            b.add_edge(idN,idS)
            b.add_output_id(idS)
        return b
    
    def simplifier_copie(self):
        res = False
        for id, noeud in list(self.get_id_node_map().items()):
            if id not in self.get_id_node_map(): continue
            if noeud.get_label() == "" and noeud.indegree() == 1 and noeud.outdegree() > 0:
                id_enfants = list(noeud.get_children().keys())
                id_parent = list(noeud.get_parents().keys())[0]
                parent = self.get_node_by_id(id_parent)
                label = parent.get_label()
                if(label == "0" or label == "1"):
                    for id_enfant in id_enfants:
                        idN = self.add_node(label=label)
                        self.add_edge(idN, id_enfant)
                        self.remove_edge(id, id_enfant)
                    if(noeud in self.outputs_ids()):
                        noeud.set_label(label)
                    else: 
                        self.remove_node_by_id(id)
                    res = True
        return res
    
    def simplifier_non(self):
        res = False
        for id, noeud in list(self.get_id_node_map().items()):
            if id not in self.get_id_node_map(): continue
            if noeud.get_label() == "~":
                parents = list(noeud.get_parents().keys())
                for id_parent in parents:
                    parent = self.get_node_by_id(id_parent)
                    label = parent.get_label()
                    if(label == "0" or label == "1"):
                        nouveau_label = "1" if label == "0" else "0"
                        enfants = list(noeud.get_children().keys())
                        for id_enfant in enfants:
                            idN = self.add_node(label=nouveau_label)
                            self.add_edge(idN, id_enfant)
                        if(noeud in self.outputs_ids()):
                            noeud.set_label(nouveau_label)     
                        else:
                            self.remove_node_by_id(id)                  
                        res = True
        return res
                
    def simplifier_et(self):
        res = False
        for id, noeud in list(self.get_id_node_map().items()):
            if id not in self.get_id_node_map(): continue
            if noeud.get_label() == "&":
                parents = list(noeud.get_parents().keys())
                if any(self.get_node_by_id(parent).get_label() == "0" for parent in parents):
                    for id_enfant in list(noeud.get_children().keys()):
                        idN = self.add_node(label="0")
                        self.add_edge(idN, id_enfant)
                    if(noeud in self.outputs_ids()):
                        noeud.set_label(0)
                    else :
                        self.remove_node_by_id(id)
                    res = True
                else:
                    parents_1 = [p for p in parents if self.get_node_by_id(p).get_label() == "1"]
                    for p in parents_1:
                        self.remove_edge(p, id)
                        res = True
        return res

    def simplifier_ou(self):
        res = False
        for id, noeud in list(self.get_id_node_map().items()):
            if id not in self.get_id_node_map(): continue
            if noeud.get_label() == "|":
                parents = list(noeud.get_parents().keys())
                if any(self.get_node_by_id(parent).get_label() == "1" for parent in parents):
                    for id_enfant in list(noeud.get_children().keys()):
                        idN = self.add_node(label="1")
                        self.add_edge(idN, id_enfant)
                    if(noeud in self.outputs_ids()):
                        noeud.set_label(1)
                    self.remove_node_by_id(id)
                    res = True
                else:
                    parents_0 = [p for p in parents if self.get_node_by_id(p).get_label() == "0"]
                    for p in parents_0:
                        self.remove_edge(p, id)
                        res = True
            
        return res
    
    def simplifier_ou_exclusif(self):
        res = False
        for id, noeud in list(self.get_id_node_map().items()):
            if id not in self.get_id_node_map(): continue
            if noeud.get_label() == "^":
                parents = list(noeud.get_parents().keys())
                for id_parent in parents:
                    parent = self.get_node_by_id(id_parent)
                    if(parent.get_label() == "0"):
                        self.remove_edge(id_parent, id)
                        res = True
                    elif(parent.get_label() == "1"):
                        self.remove_edge(id_parent, id)
                        idN = self.add_node(label="~")
                        for id_enfant in list(noeud.get_children().keys()):
                            self.add_edge(idN, id_enfant)
                            self.remove_edge(id, id_enfant)
                        self.add_edge(id, idN)
                        res = True
        return res
    
    def simplifier_neutre(self):
        res = False
        for id, noeud in list(self.get_id_node_map().items()):
            if id not in self.get_id_node_map(): continue
            if noeud.get_label() == "&" and noeud.indegree() == 0 :
                noeud.set_label("1")
                res = True
            elif ((noeud.get_label() == "|" or noeud.get_label() == "^") and noeud.indegree() == 0) :
                noeud.set_label("0")
                res = True
        return res
    
    
    def nettoyer_noeuds_morts(self):
        flag = True
        while flag:
            flag = False
            for id, noeud in list(self.get_id_node_map().items()):
                # Si le nœud n'a pas d'enfant ET n'est pas une sortie officielle
                if noeud.outdegree() == 0 and id not in self.outputs_ids():
                    self.remove_node_by_id(id)
                    flag = True # On relance car sa suppression a peut-être créé un nouveau nœud mort au-dessus

    def simplifier_naif(self):
        flag = True;
        while flag:
            flag = self.simplifier_copie() or self.simplifier_non() or self.simplifier_et() or self.simplifier_ou() or self.simplifier_ou_exclusif() or self.simplifier_neutre()
        self.nettoyer_noeuds_morts()