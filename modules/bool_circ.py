import sys
import os
import random
from modules.open_digraph import open_digraph


class bool_circ(open_digraph):
    """
    Représente un circuit booléen
    Hérite de open_digraph
    """
    def __init__(self, inputs, outputs=None, nodes=None):
        """
        Initialise le circuit booléen.
        param inputs: liste d'ID (les entrées)
        param outputs: liste d'ID (les sorties)
        param nodes: itérable de noeuds
        """
        if outputs is None and nodes is None:
            g = inputs
            super().__init__(g.inputs.copy(), g.outputs.copy(), g.nodes.values())
        else:
            super().__init__(inputs, outputs, nodes)
            
        if not self.is_well_formed():
            self.save_as_pdf("graphe_non_valide.pdf", verbose=True)
            print(g.inputs_ids())
            raise ValueError("Le graphe fourni n'est pas un circuit booléen valide (acyclique avec contraintes de degré respectées)")
    
    def is_well_formed(self):
        """
        Vérifie que le circuit n'a pas de boucle infinie et que les portes logiques ont le bon nombre de connexions.
        return: True si le circuit est bien formé, False sinon
        """
        if self.is_cyclic():
            print("Le graphe est cyclique")
            return False
        node_map = self.get_id_node_map()
        for id_noeud, noeud in node_map.items():
            for id_parent, multiplicite in noeud.get_parents().items():
                if id_parent not in node_map:
                    print(f"Le noeud {id_parent} n'existe pas dans le graphe")
                    return False
                if node_map[id_parent].outdegree() < multiplicite:
                    print(f"Le noeud {id_parent} a un degré sortant insuffisant")
                    return False
            for id_enfant, multiplicite in noeud.get_children().items():
                if id_enfant not in node_map:
                    print(f"Le noeud {id_enfant} n'existe pas dans le graphe")
                    return False
                if node_map[id_enfant].indegree() < multiplicite:
                    print(f"Le noeud {id_enfant} a un degré entrant insuffisant")
                    return False
        return True
    
    @classmethod      
    def acyclicToBoolRandom(cls, g, nbInput=None,nbOutput=None):
        """
        Convertit un graphe acyclique en circuit booléen aléatoire.
        param g: graphe acyclique
        param nbInput: nombre d'entrées
        param nbOutput: nombre de sorties
        return: circuit booléen aléatoire
        """
        if g.is_cyclic():
            raise ValueError("Le graphe n'est pas acyclique, impossible")
        else:
            b = g.copy()
        if g.get_node_ids() == [] and (nbInput is not None or nbOutput is not None):
            b = cls.identity(1)

        def labelNoeudBinaire():
            """
            Renvoie un label pour un noeud binaire aléatoire.
            return: label "|" ou "&"
            """
            return ["|", "&"][random.randint(0,1)]

        def ajout_copie_outdegree(id_noeud,noeud):
            """
            Ajoute un noeud de copie en sortie du noeud
            param id_noeud: ID du noeud
            param noeud: noeud
            """
            id_copie = b.add_node()
            for id_enfant in list(noeud.get_children().keys()):
                b.add_edge(id_copie, id_enfant)
                b.remove_parallel_edges(id_noeud, id_enfant) # On retire entièrement les arêtes
            b.add_edge(id_noeud, id_copie)

        def ajout_sortie(id_noeud):
            """
            Ajoute une sortie au noeud
            param id_noeud: ID du noeud
            """
            id_sortie = b.add_node()
            b.add_output_id(id_sortie)
            if id_noeud in b.outputs_ids():
                b.remove_output_id(id_noeud)
            b.add_edge(id_noeud, id_sortie)

        def ajouts_operateur(noeud,id_noeud):
            """
            Gère les ajouts de noeuds en sortie pour respecter les contraintes de degré des opérateurs et des sorties
            param noeud: noeud
            param id_noeud: ID du noeud
            """
            # Un operateur a une seule sortie, sinon il faut ajouter un noeud de copie après lui
            if noeud.outdegree() > 1:
                    ajout_copie_outdegree(id_noeud,noeud)
            # Si il n'a pas d'enfant c'est aussi une sortie 
            elif noeud.outdegree() == 0:           
                    ajout_sortie(id_noeud)

        for id_noeud, noeud in b.copy().get_id_node_map().items(): # On utilise une copie car le graphe est modifié pendant l'itération
        # Si un noeud n'a pas de noeuds parents, c'est une entrée du circuit
        # Auparavant pour les noeuds d'entrées, un noeud de copie était créé seulement si le noeud d'entrée avait plus d'un enfant
        # Nous avons finalement choisi de créer un noeud de copie à chaque fois, ce qui simplifie la fusion dans le cas où le nbInput est spécifié
        # Nous supprimons les noeuds de copies inutiles à la fin de la fonction
            if noeud.indegree() == 0 and noeud.outdegree() > 0:
                id_entree = b.add_node()
                b.add_input_id(id_entree) 
                if id_noeud in b.inputs_ids():
                    b.remove_input_id(id_noeud)
                b.add_edge(id_entree, id_noeud) # le noeud devient un noeud de copie et un noeud d'entrée est créé
        
            # Plusieurs parents -> opérateur logique
            elif noeud.indegree() > 1:
                b.get_node_by_id(id_noeud).set_label(labelNoeudBinaire())
                ajouts_operateur(noeud,id_noeud)
           
            # 1 parent -> c'est soit un noeud de copie soit une négation
            elif noeud.indegree() == 1:
                a = random.randint(0,1)
                label = ""
                if a == 1:
                    label = "~"
                    ajouts_operateur(noeud,id_noeud)
                b.get_node_by_id(id_noeud).set_label(label)
            
            else: # cas 0,0, on enlève le noeud
                b.remove_node_by_id(id_noeud)

        def get_unique_parent(id_noeud):
            """
            Renvoie l'unique parent du noeud
            Lève une erreur si le noeud n'a pas exactement un parent
            param id_noeud: ID du noeud
            return: ID du parent
            """
            parents = b.get_node_by_id(id_noeud).get_parents()
            if len(parents) != 1:
                raise ValueError(f"Le noeud {id_noeud} n'a pas exactement un parent ({len(parents)} parents)")
            return list(parents.keys())[0]
        
        if nbOutput is not None:
            if nbOutput <1:
                raise ValueError("Le nombre de sorties doit être supérieur ou égal à 1")
            # Si il y a plus d'ouputs que ce qui est voulu alors on fusionne des sorties avec un opérateur binaire au hasard
            # On relie directements l'unique parent de chaque sortie à l'opérateur pour enlever les noeuds inutiles
            while len(b.outputs_ids()) > nbOutput:
                id1, id2 = random.sample(b.outputs_ids(), 2) 
                id_parent1 = get_unique_parent(id1)
                id_parent2 = get_unique_parent(id2)
                b.remove_node_by_id(id1)
                b.remove_node_by_id(id2) # Supprime directement les arêtes associées
                id_op = b.add_node()
                b.add_edge(id_parent1, id_op)
                b.add_edge(id_parent2, id_op)
                node_op = b.get_node_by_id(id_op)
                node_op.set_label(labelNoeudBinaire())
                id_sortie = b.add_node()
                b.add_output_id(id_sortie)
                b.add_edge(id_op, id_sortie)
            # Si il y a moins d'outputs, on en ajoute en reliant des noeuds du graphe à de nouvelles sorties
            while len(b.outputs_ids()) < nbOutput:
                id_noeud = random.choice([id for id in b.get_node_ids() if id not in b.inputs_ids()]) # On choisit un noeud qui n'est pas une entrée 
                if id_noeud  in b.outputs_ids(): # Si le noeud est un noeud de sortie on dédouble la sortie
                    b.remove_output_id(id_noeud)
                    id_sortie1 = b.add_node()
                    id_sortie2 = b.add_node()
                    b.add_output_id(id_sortie1)
                    b.add_output_id(id_sortie2)
                    b.add_edge(id_noeud, id_sortie1)
                    b.add_edge(id_noeud, id_sortie2)

                else :
                    id_sortie = b.add_node()
                    b.add_output_id(id_sortie)
                    noeud=b.get_node_by_id(id_noeud)
                    # Si jamais le noeud choisi est un noeud d'operation alors il est nécessaire de d'ajouter un noeud de copie
                    if noeud.get_label() == "~" or noeud.get_label() == "&" or noeud.get_label() == "|":
                        b.add_edge(id_noeud, id_sortie) # l'arête sera déplacées sur le noeud de copie dans l'appel suivant
                        ajout_copie_outdegree(id_noeud, noeud)
                    #Sinon c'est un noeud de copie, on peut directement le relier à la sortie
                    else:
                        b.add_edge(id_noeud, id_sortie)
        if nbInput is not None:
            if nbInput <1:
                raise ValueError("Le nombre d'entrées doit être supérieur ou égal à 1")
            # Si il y a plus d'inputs que ce qui est voulu alors on fusionne des entrées
            while len(b.inputs_ids()) > nbInput:
                id1, id2 = random.sample(b.inputs_ids(), 2)
                b.get_node_by_id(id1).set_label("") # On enlève le label des noeuds d'entrée pour la fusion
                b.get_node_by_id(id2).set_label("")
                b.merge_nodes(id1, id2)
                if(len(b.get_node_by_id(id1).get_children().keys()) != 2):
                    raise ValueError(f"Erreur de fusion des noeuds d'entrée, le noeud fusionné n'a pas exactement 2 enfants ({len(b.get_node_by_id(id1).get_children().keys())})")
                enfant1 = list(b.get_node_by_id(id1).get_children().keys())[0]
                enfant2 = list(b.get_node_by_id(id1).get_children().keys())[1]
                # On fusionne les noeuds de copie pour que l'entrée n'ait qu'un seul enfant
                b.merge_nodes(enfant1, enfant2)
                b.remove_edge(id1, enfant1) #La fusion double les arêtes, on en retire une

            while len(b.inputs_ids()) < nbInput:
                # On dédouble une entrée
                id_noeud = random.choice([id for id in b.inputs_ids()]) # Il y a forcément une entrée car le graphe est acyclique 
                entree1 = b.add_node()
                b.add_input_id(entree1)
                entree2 = b.add_node()
                b.add_input_id(entree2)
                b.remove_input_id(id_noeud)
                op = b.add_node(label=labelNoeudBinaire())
                b.add_edge(entree1, op)
                b.add_edge(entree2, op)
                b.add_edge(op, id_noeud)
                
        
        # Enfin on retire les noeuds de copie inutiles
        for id_noeud in b.copy().get_node_ids():
            if id_noeud not in b.get_node_ids(): 
                continue
            noeud = b.get_node_by_id(id_noeud)
            if noeud.get_label() == "" and noeud.indegree() == 1 and noeud.outdegree() == 1:
                id_parent = list(noeud.get_parents().keys())[0]
                id_enfant = list(noeud.get_children().keys())[0]
                b.add_edge(id_parent, id_enfant)
                b.remove_node_by_id(id_noeud)


        return bool_circ(b)

    @classmethod      
    def formula_to_tree(cls, s):
        """
        Convertit une formule logique en arbre (circuit booléen).
        param s: formule
        return: arbre
        """
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
        """
        Convertit plusieurs formules en arbres.
        param args: formules
        return: arbres
        """
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
        """
        Crée un additionneur de taille n
        param n: taille de l'additionneur
        return: additionneur
        """
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
        """
        Crée un additionneur de taille 0
        return: additionneur
        """
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
    def half_adder(cls,n,retenue=0):
        """
        Crée un additionneur de taille n et initialise la retenue entrante (0 par défaut)
        param n: taille de l'additionneur
        param retenue: retenue entrante
        return: additionneur
        """
        adder = cls.adder(n)
        # on enlève la retenue entrante de l'adder
        inputs = adder.inputs_ids()
        id = inputs.pop()
        adder.set_inputs(inputs)
        adder.get_node_by_id(id).set_label(str(retenue)) 
        return adder 
    
    @classmethod
    def registre(cls,entier, n=8):
        """
        Crée un registre de taille n représentant un entier. 
        Lève une erreur si l'entier ne peut pas être représenté sur n bits.
        param entier: entier à convertir en registre
        param n: taille du registre
        return: registre
        """
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
        """
        Simplifie les copies de noeuds
        return: True si des copies ont été simplifiées, False sinon
        """
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
        """
        Simplifie les non de noeuds
        return: True si des non ont été simplifiés, False sinon
        """
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
        """
        Simplifie les et de noeuds
        return: True si des et ont été simplifiés, False sinon
        """
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
        """
        Simplifie les ou de noeuds
        return: True si des ou ont été simplifiés, False sinon
        """
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
        """
        Simplifie les ou exclusif de noeuds
        :return: True si des ou exclusif ont été simplifiés, False sinon
        """
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
        """
        Simplifie les neutres de noeuds
        return: True si des neutres ont été simplifiés, False sinon
        """
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
        """
        Simplifie le circuit de manière naïve
        """
        flag = True
        while flag:
            flag = self.simplifier_copie() or self.simplifier_non() or self.simplifier_et() or self.simplifier_ou() or self.simplifier_ou_exclusif() or self.simplifier_neutre()
        self.nettoyer_noeuds_morts()

    @classmethod
    def somme(cls, entier1, entier2):
        """
        Calcule la somme de deux entiers en passant par les additionneurs de half_adder
        :param entier1: premier entier
        :param entier2: deuxième entier
        :return: somme
        """
        registre1 = bool_circ.registre(entier1)
        registre2 = bool_circ.registre(entier2)
        registres= registre1.compo_parallele(registre2)
        adder3 = bool_circ.half_adder(3)
        circuit = registres.compo_sequentielle(adder3)
        return circuit.evaluer() 
    
    def evaluer(self):
        """
        Parcours le circuit de haut en bas (via un tri topologique) 
        et calcule la sortie finale en appliquant les règles des portes logiques (&, |, ^, ~)
        return : entier correspondant à la sortie du circuit
        """
        circuit = self.copy() # On travaille sur une copie du circuit pour ne pas modifier le circuit
        tri_topo = circuit.tri_topologique()
        for niveau in tri_topo:
            for id in niveau:
                node = circuit.get_node_by_id(id)
                if node.get_label() == "0" or node.get_label() == "1": # Cette ligne n'est utilisée que lors du passage du premier niveau
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
                raise ValueError("Les noeuds de sortie doivent avoir des valeurs binaires")
            string_sortie += node.get_label()
        
        return int(string_sortie, 2)

    @classmethod
    def cla_adder4(cls,retenue=None, superCla = False):
        """
        Crée un additionneur de 4 bits via un Carry Look Ahead
        param: retenue : valeur de la retenue entrante (0 ou 1), None sinon (la retenue entrante est alors une entrée du circuit)
        param: superCla : True si l'adder est utilisé pour un adder cla de taille supérieure (ajoute le bit de génération et de propagation de groupe en sortie)
        return: additionneur
        """
        cla = cls.empty()
        copies = []
        for i in range(8): # 2x 4 bits entrées
            id_i = cla.add_node()
            cla.add_input_id(id_i)
            id_copie_i = cla.add_node()
            cla.add_edge(id_i, id_copie_i)
            copies.append(id_copie_i)
        c0 = cla.add_node() #retenue entrante
        if retenue is None:
            cla.add_input_id(c0)
        else:
            cla.get_node_by_id(c0).set_label(retenue)

        Gi = []
        Pi = []
        for i in range(4):
            and_i = cla.add_node(label="&")
            gi = cla.add_node()
            cla.add_edge(copies[i], and_i)
            cla.add_edge(copies[i+4], and_i)
            cla.add_edge(and_i, gi)
            Gi.append(gi)
            xor_i = cla.add_node(label="^")
            pi = cla.add_node()
            cla.add_edge(copies[i], xor_i)
            cla.add_edge(copies[i+4], xor_i)
            cla.add_edge(xor_i, pi)
            Pi.append(pi)
        Ci = []
        
        retenues, P_groupe, G_groupe, c4 = cla.cla_comp(Pi, Gi, c0)
        if superCla is None or (not superCla):
                cla.add_output_id(c4)
        for i in range(4):
            si = cla.opbin(Pi[i], retenues[i], "^")
            cla.add_output_id(si)
        if superCla:
            cla.add_output_id(P_groupe)
            cla.add_output_id(G_groupe)
        return cla
    
    def opbin(self, node1, node2, op):
        """
        Lie deux noeuds à un opérateur binaire et retourne le noeud opérateur
        param node1: id du premier noeud
        param node2: id du second noeud
        param op: opérateur binaire ("&", "|", "^")
        return: le noeud opérateur
        """
        op_node = self.add_node(label=op)
        self.add_edge(node1, op_node)
        self.add_edge(node2, op_node)
        return op_node
    
    def cla_comp(self, Pi,Gi,c0):
            """
            param: Pi, liste des ids des noeuds représentant le bit de propagation de retenue de chaque addition bit à bit
            param: Gi, liste des ids des noeuds représentant le bit de génération de retenuede chaque addition bit à bit
            param: c0, id du noeud représentant la retenue entrante du bloc cla
            return: retenues, P_groupe, G_groupe, c4
            retenues : Les retenues intermédiaires c0, c1, c2, c3
            P_groupe : le bit (le noeud) de propagation de retenue du bloc cla
            G_groupe : le bit de génération de retenue du bloc cla (utile pour l'adder de 16 bits)
            c4 : la retenue sortante du bloc (utile pour l'adder de 4 bits)
            """
            Gi.reverse()
            Pi.reverse()
            #C4
            # Un bloc cla de 4 bits propage une retenue si les 4 bits propagent
            # Le bloc génère une retenue si le bit de poids fort génère une retenue ou si le second bit génère et le bit de poids fort propage etc
            p3andp2 = self.opbin(Pi[3], Pi[2], "&")
            p1andp0 = self.opbin(Pi[1], Pi[0], "&")
            P_groupe = self.opbin(p3andp2, p1andp0, "&")
            

            p3andg2 = self.opbin(Pi[3], Gi[2], "&")  
            g3orp3andg2 = self.opbin(Gi[3], p3andg2, "|")
            
            p3andp2andG1 = self.opbin(p3andp2, Gi[1], "&")
            g3orp3andg2_or_p3andp2andG1 = self.opbin(g3orp3andg2, p3andp2andG1, "|")
            
            p3andp2andp1 = self.opbin(p3andp2, Pi[1], "&")
            p3andp2andp1andG0 = self.opbin(p3andp2andp1, Gi[0], "&")
            G_groupe = self.opbin(g3orp3andg2_or_p3andp2andG1, p3andp2andp1andG0, "|")

            P_groupeandc0 = self.opbin(P_groupe, c0, "&")
            c4 = self.opbin(G_groupe, P_groupeandc0, "|")

            #C3
            p0andc0 = self.opbin(Pi[0], c0, "&")
            p2andp1 = self.opbin(Pi[2], Pi[1], "&")
            p2andp1andp0andc0 = self.opbin(p2andp1, p0andc0, "&")
            p2andp1andg0 = self.opbin(p2andp1, Gi[0], "&")
            p2andg1 = self.opbin(Pi[2], Gi[1], "&")
            g2orp2andg1 = self.opbin(Gi[2], p2andg1, "|")
            g2orp2andg1_or_p2andp1andg0 = self.opbin(g2orp2andg1, p2andp1andg0, "|")
            c3 = self.opbin(g2orp2andg1_or_p2andp1andg0, p2andp1andp0andc0, "|")

            #C2
            p1andp0andc0 = self.opbin(p1andp0, c0, "&")
            p1andg0 = self.opbin(Pi[1], Gi[0], "&")
            g1orp1andg0 = self.opbin(Gi[1], p1andg0, "|")
            c2 = self.opbin(g1orp1andg0, p1andp0andc0, "|")

            #C1
            c1 = self.opbin(Gi[0], p0andc0, "|")
            
            retenues = [c3, c2, c1,c0]
            Gi.reverse()
            Pi.reverse()
            return retenues, P_groupe, G_groupe, c4
            
    @classmethod
    def cla_somme4(cls, entier1, entier2):
        """
        Somme de deux entiers sur 4 bits via un adder cla de 4 bits
        param: entier1
        param: entier2
        """
        cla = cls.cla_adder4(retenue="0")
        registre1 = cls.registre(entier1, n=4)
        registre2 = cls.registre(entier2, n=4)
        registres= registre1.compo_parallele(registre2)
        circuit = registres.compo_sequentielle(cla)
        return circuit.evaluer()
        
    @classmethod      
    def cla_adder(cls,n):
        """
        Construit un adder de taille 2^n via des blocs de cla de 4 bits
        param n: exposant de la taille de l'adder
        return: adder de taille 2^n
        """
        if(n<2):
            return bool_circ.adder(n)
        elif (n==2):
            return bool_circ.cla_adder4()
        else:
            # Réutilisation du bloc de récursion de l'adder classique pour lier des blocs cla de 4 bits
            adder1 = bool_circ.cla_adder(n-1)
            adder2 = bool_circ.cla_adder(n-1)
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
    def cla_half_adder(cls,n,retenue=0):
        """
        Construit un half-adder de taille 2^n via des blocs de cla de 4 bits
        param n: exposant de la taille de l'adder
        param retenue: valeur de la retenue entrante (0 ou 1) 
        return: half-adder de taille 2^n
        """
        adder = cls.cla_adder(n)
        # on enlève la retenue entrante de l'adder
        inputs = adder.inputs_ids()
        id = inputs.pop()
        adder.set_inputs(inputs)
        adder.get_node_by_id(id).set_label(str(retenue)) # on fixe la retenue entrante à 0 par défaut
        return adder

    @classmethod
    def cla_somme(cls, entier1, entier2):
        """
        Somme de deux entiers sur 8 bits via un half adder composé de deux adders cla de 4 bits
        param: entier1
        param: entier2
        return : somme de entier1 et entier2
        """
        registre1 = bool_circ.registre(entier1)
        registre2 = bool_circ.registre(entier2)
        registres= registre1.compo_parallele(registre2)
        adder3 = bool_circ.cla_half_adder(3)
        circuit = registres.compo_sequentielle(adder3)
        return circuit.evaluer() 
    
    @classmethod 
    def cla_adder16(cls):
        """
        Crée un adder de 16 bits via 4 adders cla de 4 bits en utilisant le Carry Look Ahead pour connaitre les retenues de blocs
        Adder avec une Profondeur constante
        return: adder de 16 bits

        """
        cla4_1 = cls.cla_adder4(superCla=True)
        cla4_2 = cls.cla_adder4(superCla=True)
        cla4_3 = cls.cla_adder4(superCla=True)
        cla4_4 = cls.cla_adder4(superCla=True)
        cla = cla4_1.compo_parallele(cla4_2).compo_parallele(cla4_3).compo_parallele(cla4_4)
        
        # 5 outputs par cla (4 bits de sortie, Pgroupe,Ggroupe)
        Pgi =[cla.outputs_ids()[i] for i in range(4, 24, 6)]
        Ggi = [cla.outputs_ids()[i] for i in range(5, 24, 6)]
        for id in Pgi+Ggi:
            cla.remove_output_id(id)
        
        c0 = cla.inputs_ids()[-1] # La retenue entrante du bloc cla de 4 bits à droite
        retenues,p16,g16,c16 = cla.cla_comp(Pgi,Ggi,c0)
        inputs = cla.inputs_ids()[:-1] #
        outputs = [c16] + cla.outputs_ids()
        cla.set_outputs(outputs)
        retenues_entrantes = [inputs[i] for i in range(8,27,9)]
        for i in range(3):
            cla.add_edge(retenues[i], retenues_entrantes[i])
            cla.remove_input_id(retenues_entrantes[i])
        bitsA = inputs[0:4] + inputs[9:13] + inputs[18:22] + inputs[27:31]
        bitsB = inputs[4:8] + inputs[13:17] + inputs[22:26] + inputs[31:35]
        new_inputs = bitsA + bitsB + [c0]
        cla.set_inputs(new_inputs)
        return cla
     
    @classmethod
    def cla_half_adder16(cls,retenue=0):
        """
        Crée un half-adder de 16 bits en iniitalisant la retenue dans l'adder de 16 bits
        param: retenue valeur de la retenue (0 par défaut)
        return: le half adder
        """
        adder = cls.cla_adder16()
        # on enlève la retenue entrante de l'adder
        inputs = adder.inputs_ids()
        id = inputs.pop()
        adder.set_inputs(inputs)
        adder.get_node_by_id(id).set_label(str(retenue)) # on fixe la retenue entrante à 0 par défaut
        return adder

    @classmethod
    def cla_somme16(cls, entier1, entier2):
        """
        Utilise l'adder cla de 16 bits pour calculer la somme de deux entiers sur 16 bits
        param: entier1
        param: entier2
        return: somme de entier1 et entier2
        """
        registre1 = bool_circ.registre(entier1, n=16)
        registre2 = bool_circ.registre(entier2, n=16)
        registres= registre1.compo_parallele(registre2)
        adder3 = bool_circ.cla_half_adder16()
        circuit = registres.compo_sequentielle(adder3)
        return circuit.evaluer()