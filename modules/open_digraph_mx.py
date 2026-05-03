import os
# MARK: - Matrix
class MatrixMixin:
    @staticmethod
    def random_int_list(n, bound):
        """
        Crée une liste d'entiers aléatoires
        param n: taille de la liste
        param bound: borne supérieure
        return: liste d'entiers aléatoires
        """
        import random
        return [random.randrange(0, bound) for e in range(n)]

    @staticmethod
    def random_int_matrix(n, bound, null_diag=True):
        """
        Crée une matrice d'entiers aléatoires
        param n: taille de la matrice
        param bound: borne supérieure
        param null_diag: si True, la diagonale est nulle
        return: matrice d'entiers aléatoires
        """
        res = [MatrixMixin.random_int_list(n, bound) for e in range(n)]
        if null_diag:
            for i in range(n):
                    res[i][i] = 0
        return res

    @staticmethod
    def random_symetric_int_matrix(n, bound, null_diag=True):
        """
        Crée une matrice symétrique d'entiers aléatoires
        param n: taille de la matrice
        param bound: borne supérieure
        param null_diag: si True, la diagonale est nulle
        return: matrice symétrique d'entiers aléatoires
        """
        res = MatrixMixin.random_int_matrix(n, bound, null_diag)
        for i in range(n):
            for j in range(i+1, n):
                res[i][j] = res[j][i]
        return res

    @staticmethod
    def random_oriented_int_matrix(n, bound, null_diag=True):
        """
        Crée une matrice orientée d'entiers aléatoires
        param n: taille de la matrice
        param bound: borne supérieure
        param null_diag: si True, la diagonale est nulle
        return: matrice orientée d'entiers aléatoires
        """
        res = MatrixMixin.random_int_matrix(n, bound, null_diag)
        for i in range(n):
            for j in range(i+1, n):
                if res[i][j] != 0:
                    res[j][i] = 0
        return res

    @staticmethod
    def random_triangular_int_matrix(n, bound, null_diag=True):
        """
        Crée une matrice triangulaire d'entiers aléatoires
        param n: taille de la matrice
        param bound: borne supérieure
        param null_diag: si True, la diagonale est nulle
        return: matrice triangulaire d'entiers aléatoires
        """
        res = MatrixMixin.random_int_matrix(n, bound, null_diag)
        for i in range(n):
            for j in range(i+1, n):
                res[i][j] = 0
        return res

    def graph_from_adjacency_matrix(self, matrix):
        """
        Construit et renvoie un graphe à partir d'une matrice
        inputs et outputs restent vides
        """
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
        Construit et renvoie un graphe à partir d'une matrice
        inputs et outputs restent vides
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
    
    def adjacency_matrix(self):
        """
        Renvoie la matrice d'adjacence du graphe
        """
        n = len(self.nodes)
        matrix = [[0 for j in range(n)] for i in range(n)]
        id_to_index = self.graph_to_dict()
        for node_id, node in self.nodes.items():
            for child_id, m in node.get_children().items():
                matrix[id_to_index[node_id]][id_to_index[child_id]] = m
        return matrix
    
    @classmethod
    def random(cls, n, bound, inputs=0, outputs=0, form="free"):
        """
        Génère un graphe aléatoire
        param n: nombre de noeuds
        param bound: borne supérieure
        param inputs: nombre d'entrées
        param outputs: nombre de sorties
        param form: forme du graphe
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

# MARK: - Display
class DisplayMixin:
    def save_as_dot_file(self, path, verbose=False):
        """
        Sauvegarde le graphe au format .dot
        param path: chemin du fichier
        param verbose: si True, ajoute les ID
        """
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
    def from_dot_file(cls, path):
        """
        Lit un fichier .dot et renvoie un graphe
        param path: chemin du fichier
        return: graphe
        """
        with open(path, 'r') as f:
            g = cls.empty()
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
    
    def display(self, verbose=False):
        """
        Affiche le graphe sous forme de fichier PDF
        param verbose: si True, ajoute les ID
        """
        import webbrowser
        self.save_as_dot_file("temp.dot",verbose)
        commande = "dot -Tpdf temp.dot -o temp.pdf"
        print("Fichier .dot généré : temp.dot")
        print(f"Exécution de la commande : {commande}")
        os.system(commande)
        chemin_pdf = "file://" + os.path.abspath("temp.pdf")
        print(f"Ouverture du fichier : {chemin_pdf}")
        print("--------------------")
        webbrowser.open(chemin_pdf)

    def save_as_pdf(self, path, verbose=False):
        """
        Sauvegarde le graphe sous forme de fichier PDF
        param path: chemin du fichier
        param verbose: si True, ajoute les ID
        """
        self.save_as_dot_file("temp.dot", verbose)
        commande = f"dot -Tpdf temp.dot -o {path}"
        print("Fichier .dot généré : temp.dot")
        print(f"Exécution de la commande : {commande}")
        print("--------------------")
        os.system(commande)
        os.remove("temp.dot")

# MARK: - Composition
class CompositionMixin:

    def shift_indices(self, n):
        """
        Crée un graphe dont les IDs sont décalés de n
        param n: décalage
        return: graphe décalé
        """
        if n is None:
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
        return self.__class__(new_inputs, new_outputs, new_nodes.values())
    
    def merge_nodes(self, id1, id2):
        """
        Fusionne deux noeuds en un seul
        param id1: id du premier noeud
        param id2: id du second noeud
        return: graphe fusionné
        """
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

    def compo_parallele(self, other):
        """
        Composition parallèle de deux graphes
        param other: autre graphe
        return: graphe composé
        """
        f = self.copy()
        shift = (f.max_id() + 1) if f.max_id() is not None else 0
        g = other.shift_indices(shift)
        inputs = f.inputs_ids() + g.inputs_ids()
        outputs = f.outputs_ids() + g.outputs_ids()
        nodes = f.get_nodes() + g.get_nodes()
        return self.__class__(inputs, outputs, nodes)
    
    def compo_sequentielle(self, other):
        """
        Composition séquentielle de deux graphes
        param other: autre graphe
        return: graphe composé
        """
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
        combined = self.__class__(inputs, outputs, nodes_list)
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
        return combined
    
    def connected_components(self):
        """
        Calcule les composantes connexes du graphe
        return: dictionnaire des composantes connexes
        """
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
        """
        Calcule les composantes connexes du graphe et renvoie un graphe pour chaque composante
        return: dictionnaire des graphes des composantes connexes, liste des inputs globaux, liste des outputs globaux
        """
        (inputs_globaux, outputs_globaux) = (self.inputs_ids().copy(), self.outputs_ids().copy())
        num_comps, comp_dict = self.connected_components()
        graphs = [self.empty() for _ in range(num_comps)]
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

# MARK: - Algo
class AlgoMixin:
    # Ancienne fonction pour calculer les longueurs, dysfonctionne dans certains cas
    def longueurs_dfs(self, src, direction = 1) :
        """
        Calcule les longueurs des chemins depuis un noeud source avec DFS
        param src: noeud source
        param direction: direction du parcours
        return: dictionnaire des longueurs
        """
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
        """
        Calcul de la distance minimale depuis un noeud source   
        param src: noeud source
        param prev: dictionnaire des predecesseurs
        param dist: dictionnaire des distances
        param current_dist: distance actuelle
        param parent: parent du noeud actuel
        return: dictionnaire des distances
        """
        childs = self.get_node_by_id(src).get_children()
        if src not in dist or dist[src] > current_dist:
            dist[src] = current_dist
            prev[src] = parent
            for child in childs.keys():
                self.longueurs_aux(child, prev, dist, current_dist + 1, src)
                
    def longueurs_aux2(self, src, prev,dist, current_dist, enfant):
        """
        Pareil que longueurs_aux mais pour les parents (direction -1)
        """
        parents = self.get_node_by_id(src).get_parents()
        if src not in dist or dist[src] > current_dist:
            dist[src] = current_dist
            prev[src] = enfant
            for parent in parents.keys():
                self.longueurs_aux2(parent, prev, dist, current_dist + 1, src)         

    # Fonction valide des calculs de longueurs
    def longueurs_bfs(self, src, direction=1, tgt = None):
        """
        Calcule les longueurs des chemins depuis un noeud source avec BFS
        param src: noeud source
        param direction: direction du parcours
        param tgt: optionnel : noeud cible (l'algorithme s'arrête des que la distance minimale vers tgt est connue)
        return: dictionnaire des longueurs
        """
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
        """
        Calcule le plus court chemin entre un noeud source et un noeud cible avec BFS
        param src: noeud source
        param tgt: noeud cible
        param direction: direction du parcours
        return: distance et chemin
        """
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
        """
        Calcule les ancêtres communs entre deux noeuds
        param id1: id du premier noeud
        param id2: id du second noeud
        return: dictionnaire des ancêtres communs avec distances respectives vers id1 et id2
        """
        dist1, _ = self.longueurs_bfs(id1, direction=-1)
        dist2, _ = self.longueurs_bfs(id2, direction=-1)
        resultat = {}
        for id in dist1.keys():
            if id in dist2:
                resultat[id] = (dist1[id], dist2[id])
        return resultat

	# Tri topologique "compréssé vers le haut"                            
    # On réutilise une partie du code de is_cyclic
    def tri_topologique(self):
        """
        Tri topologique du graphe
        return: liste des noeuds triés
        """
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
    
    def profondeur_noeud(self, id_noeud, tri=None):
        """
        Calcule la profondeur d'un noeud
        param id_noeud: id du noeud
        param tri: tri topologique du graphe
        return: profondeur du noeud
        """
        if tri is None: # Le paramètre optionnel permet d'optimiser certaines fonctions comme longest_path
            tri = self.tri_topologique()
        for i in range(len(tri)):
            if id_noeud in tri[i]:
                return i+1
        raise ValueError("l'id n'est pas dans le graphe")
    
    def profondeur(self):
        """
        Calcule la profondeur du graphe
        return: profondeur du graphe
        """
        tri = self.tri_topologique()
        return len(tri)
    
    def longest_path(self,u,v):
        """
        Calcule le plus long chemin entre un noeud source et un noeud cible avec DFS
        param u: noeud source
        param v: noeud cible
        return: distance et chemin
        """
        tri_topo = self.tri_topologique() # Vérifie en même temps que le graphe est acyclique
        prof_u = self.profondeur_noeud(u, tri_topo) # On évite de rappeler le tri topologique 
        prof_v = self.profondeur_noeud(v, tri_topo)
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
    
    def is_cyclic(self):
        """
        Vérifie si le graphe est cyclique
        return: True si le graphe est cyclique, False sinon
        """
        noeud_deg = {id_noeud: noeud.outdegree() for id_noeud, noeud in self.nodes.items()} # Dictionnaire  noeud : degré sortant
        queue = [id_noeud for id_noeud, outdegree in noeud_deg.items() if outdegree == 0] # Feuilles avec degré sortant nul
        cpt = 0
        while queue:
            courant = queue.pop(0) # On supprime la feuille de la queue et virtuellement du graphe
            cpt += 1
            for parent_id, multi in self.nodes[courant].get_parents().items():
                noeud_deg[parent_id] -= multi # Le degré sortant des parents diminue
                if noeud_deg[parent_id] == 0: # Si il est à 0 on l'ajoute à la queue
                    queue.append(parent_id)
        # Sortie de la boucle lorsqu'il n'y a plus de cofeuilles
        # Si il y a des noeuds restants, il y a un cycle
        return cpt != len(self.nodes) 
    
