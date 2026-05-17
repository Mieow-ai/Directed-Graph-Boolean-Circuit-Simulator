import sys
import os
root = os.path.normpath(os.path.join(__file__, './../..'))
sys.path.append(root) # allows us to fetch files from the project root
import unittest
from modules.open_digraph import *
from modules.bool_circ import *

class InitTest(unittest.TestCase):
    
    def setUp(self):
        self.n0 = node(0, 'i', {}, {1:1})
        self.n1 = node(1, 'a', {0:1}, {2:2})
        self.n2 = node(2, 'o', {1:2}, {})
        self.g = open_digraph([0], [2], [self.n0, self.n1, self.n2])
        
        self.n0_2 = node(0, 'i', {}, {1:1})
        self.n1_2 = node(1, 'a', {0:1}, {2:1})
        self.n2_2 = node(2, 'o', {1:1}, {})
        self.g2 = open_digraph([0], [2], [self.n0_2, self.n1_2, self.n2_2])
    
    def test_init_node(self):
        self.assertEqual(self.n0.id, 0)
        self.assertEqual(self.n0.label, 'i')
        self.assertEqual(self.n0.parents, {})
        self.assertEqual(self.n0.children, {1:1})
        self.assertIsInstance(self.n0, node)
        self.assertIsNot(self.n0.copy(), self.n0)
        
    def test_add_node(self):
        self.g.add_node('b', {0:1}, {2:1})
        self.assertEqual(self.g.nodes[3].get_id(), 3)
        self.assertEqual(self.g.nodes[3].get_label(), 'b')
        self.assertEqual(self.g.nodes[3].get_parents(), {0:1})
        self.assertEqual(self.g.nodes[3].get_children(), {2:1})
        self.g.add_node('c')
        self.assertEqual(self.g.nodes[4].get_id(), 4)
        self.assertEqual(self.g.nodes[4].get_label(), 'c')
        self.assertEqual(self.g.nodes[4].get_parents(), {})
        self.assertEqual(self.g.nodes[4].get_children(), {})
    
    def test_init_open_digraph(self):
        self.assertEqual(self.g.inputs, [0])
        self.assertEqual(self.g.outputs, [2])
        self.assertEqual(self.g.nodes, {0:self.n0, 1:self.n1, 2:self.n2})
        self.assertIsInstance(self.g, open_digraph)
        
    def test_copy_open_digraph(self):
        self.assertIsNot(self.g.copy(), self.g)
    
    def test_new_id_and_add_edge(self):
        new_id = self.g.new_id()
        self.assertEqual(new_id, 3)
        self.g.add_edge(0, 2)
        self.assertEqual(self.n0.get_children()[2], 1)
        self.assertEqual(self.n2.get_parents()[0], 1)
        self.g.add_edges([(0, 1), (1, 2)])
        self.assertEqual(self.n0.get_children()[1], 2)
        self.assertEqual(self.n1.get_parents()[0], 2)
        self.assertEqual(self.n1.get_children()[2], 3)
        self.assertEqual(self.n2.get_parents()[1], 3)
        
    def test_remove_childrens_parents_once(self):
        self.n1.remove_child_once(2)
        self.assertEqual(self.n1.get_children(), {2:1})
        self.n1.remove_parent_once(0)
        self.assertEqual(self.n1.get_parents(), {})
        
    def test_remove_childrens_parents_id(self):
        self.n1.remove_child_id(2)
        self.assertEqual(self.n1.get_children(), {})
        self.n1.remove_parent_id(0)
        self.assertEqual(self.n1.get_parents(), {})
        
    def test_remove_edge(self):
        self.g.remove_edge(1, 2)
        self.assertEqual(self.n1.get_children(), {2:1})
        self.assertEqual(self.n2.get_parents(), {1:1})
    
    def test_remove_parallel_edges(self):
        self.g.add_edge(1, 2)
        self.g.add_edge(1, 2)
        self.assertEqual(self.n1.get_children(), {2:4})
        self.assertEqual(self.n2.get_parents(), {1:4})
        self.g.remove_parallel_edges(1, 2)
        self.assertEqual(self.n1.get_children(), {})
        self.assertEqual(self.n2.get_parents(), {})
        
    def test_well_formed(self):
        self.assertTrue(self.g2.well_formed())
        self.g2.add_edge(0, 2)
        self.assertFalse(self.g2.well_formed())
        
    def test_add_input_node(self):
        self.g2.add_input_node(1)
        self.assertTrue(self.g2.well_formed())
    
    def test_add_output_node(self):
        self.g2.add_output_node(1)
        self.assertTrue(self.g2.well_formed())
      
    def test_random_int_list(self):
        lst = open_digraph.random_int_list(5, 10)
        self.assertEqual(len(lst), 5)
        for x in lst:
            self.assertTrue(0 <= x < 10)
    
    def test_random_int_matrix(self):
        matrix = open_digraph.random_int_matrix(3, 5)
        self.assertEqual(len(matrix), 3)
        for row in matrix:
            self.assertEqual(len(row), 3)
            for x in row:
                self.assertTrue(0 <= x < 5)
            
    def test_random_symetric_int_matrix(self):
        matrix = open_digraph.random_symetric_int_matrix(3, 5)
        self.assertEqual(len(matrix), 3)
        for row in matrix:
            self.assertEqual(len(row), 3)
            for x in row:
                self.assertTrue(0 <= x < 5)
        for i in range(3):
            for j in range(i+1, 3):
                self.assertEqual(matrix[i][j], matrix[j][i])
    
    def test_random_oriented_int_matrix(self):
        matrix = open_digraph.random_oriented_int_matrix(3, 5)
        self.assertEqual(len(matrix), 3)
        for row in matrix:
            self.assertEqual(len(row), 3)
            for x in row:
                self.assertTrue(0 <= x < 5)
        for i in range(3):
            for j in range(i+1, 3):
                self.assertTrue(matrix[i][j] == 0 or matrix[j][i] == 0)
                         
    def test_random_triangular_int_matrix(self):
        matrix = open_digraph.random_triangular_int_matrix(3, 5)
        self.assertEqual(len(matrix), 3)
        for row in matrix:
            self.assertEqual(len(row), 3)
            for x in row:
                self.assertTrue(0 <= x < 5)
        for i in range(3):
            self.assertEqual(matrix[i][i], 0)
            for j in range(i+1, 3):
                self.assertEqual(matrix[i][j], 0)
                
    def test_graph_from_adjacency_matrix(self):
        matrix = [[0, 1, 0], [0, 0, 2], [0, 0, 0]]
        g = open_digraph.empty()
        g.graph_from_adjacency_matrix(matrix)
        self.assertEqual(g.nodes[0].get_children(), {1:1})
        self.assertEqual(g.nodes[1].get_parents(), {0:1})
        self.assertEqual(g.nodes[1].get_children(), {2:2})
        self.assertEqual(g.nodes[2].get_parents(), {1:2})
      
    def test_random_graph(self):
        n = 5
        inputs_count = 2
        outputs_count = 2
    
        g = open_digraph.random(n, 3, inputs=inputs_count, outputs=outputs_count, form='DAG')
        self.assertTrue(len(g.nodes) >= n)
        self.assertTrue(len(g.inputs) <= inputs_count)
        self.assertTrue(len(g.outputs) <= outputs_count)
        self.assertFalse(g.is_cyclic())
        
    def test_graph_to_dict(self):
        d = self.g.graph_to_dict()
        for i, new_index in enumerate(d.items()):
            self.assertEqual(new_index[0], i)
    
        
    def test_dot_file(self):
        self.g.save_as_dot_file('test.dot')
        g2 = open_digraph.from_dot_file('test.dot')
        # self.g.display(True)
        self.assertEqual(self.g, g2)
        os.remove('test.dot')
        #self.g.save_as_pdf('Graphe_g.pdf') 
        #self.g.save_as_pdf('Graphe_g_verbose.pdf', verbose=True) 

    
    def test_compo_parallele(self):
        # Composition de deux graphes vides est un graphe vide
        g_vide = open_digraph.empty()
        b_vide = bool_circ(g_vide)
        res_vide = b_vide.compo_parallele(b_vide)
        self.assertEqual(len(res_vide.get_nodes()), 0)
        self.assertEqual(len(res_vide.inputs_ids()), 0)
        self.assertEqual(len(res_vide.outputs_ids()), 0)
        
        # Composition à gauche et à droite d’un graphe f avec l’élément neutre et vérification que f n’est pas modifié
        g1 = open_digraph.empty()
        n1 = g1.add_node()
        g1.add_input_id(n1)
        b1 = bool_circ(g1)
        
        res_gauche = b_vide.compo_parallele(b1)
        self.assertEqual(res_gauche, b1)
        
        res_droite = b1.compo_parallele(b_vide)
        self.assertEqual(res_droite, b1)
        
        # Composition de deux graphes f et g, vérification que le nombre total de noeuds, d’entrée et de sortie est identique à la somme des nombres correspondants pour f et g.
        g2 = open_digraph.empty()
        n2 = g2.add_node()
        n3 = g2.add_node()
        n4 = g2.add_node()
        g2.add_input_id(n3)
        g2.add_output_id(n2)
        b2 = bool_circ(g2)
        
        res_parallele = b1.compo_parallele(b2)
        self.assertEqual(len(res_parallele.get_nodes()), len(b1.get_nodes()) + len(b2.get_nodes()))
        self.assertEqual(len(res_parallele.inputs_ids()), len(b1.inputs_ids()) + len(b2.inputs_ids()))
        self.assertEqual(len(res_parallele.outputs_ids()), len(b1.outputs_ids()) + len(b2.outputs_ids()))

    def test_compo_sequentielle(self):
        g_vide = open_digraph.empty()
        b_vide = bool_circ(g_vide)
        
        g1 = open_digraph.empty()
        n1 = g1.add_node()
        g1.add_output_id(n1)
        b1 = bool_circ(g1)
        
        g2 = open_digraph.empty()
        g2.add_input_id(g2.add_node())
        g2.add_input_id(g2.add_node())
        b2 = bool_circ(g2)

        # Composition de graphes incompatibles, vérification que l’erreur est bien renvoyée
        with self.assertRaises(ValueError):
            b1.compo_sequentielle(b2) 

        # Composition d’un graphe non vide et du graphe vide (incompatible)
        with self.assertRaises(ValueError):
            # b1 a 1 sortie, b_vide a 0 entrée -> incompatible
            b1.compo_sequentielle(b_vide) 

        # Composition de deux graphes vides
        res_vide = b_vide.compo_sequentielle(b_vide)
        self.assertEqual(len(res_vide.get_nodes()), 0)
        self.assertEqual(len(res_vide.inputs_ids()), 0)
        self.assertEqual(len(res_vide.outputs_ids()), 0)

        # Composition f et g compatibles et vérification que le nombre total de noeud est égale à la somme du nombre de noeuds de f et de g moins le nombre d’entrées de g et de sorties de f, vérification que le nombre d’entrées du graphe résultat est le nombre d’entrées de f et que son nombre de sorties est celui de g.
        f = open_digraph.empty()
        n0 = f.add_node()
        n1 = f.add_node()
        f.add_edge(n0, n1)
        f.add_input_node(n0)
        f.add_output_node(n1)
        b_f = bool_circ(f)
        
        g = open_digraph.empty()
        g.add_input_node(g.add_node())
        b_g = bool_circ(g)
        
        res = b_f.compo_sequentielle(b_g)
        expected_nodes = len(b_f.get_nodes()) + len(b_g.get_nodes()) - len(b_g.inputs_ids()) - len(b_f.outputs_ids())
        self.assertEqual(len(res.get_nodes()), expected_nodes)
        self.assertEqual(len(res.inputs_ids()), len(b_f.inputs_ids()))
        self.assertEqual(len(res.outputs_ids()), len(b_g.outputs_ids()))

        
    def test_ancetres_communs_dist(self):
        g = open_digraph.empty()
        for i in range(10):
            g.add_node(id=i, label=str(i))
        edges = [(0, 3), (1, 4), (1, 5), (1, 8),(2, 4),(3, 5), 
        (3, 6), (3, 7),(4, 6),(5, 7),(6, 8), (6, 9)]
        g.add_edges(edges)
        b = bool_circ(g)
        res = b.ancetres_communs_dist(5, 8)
        self.assertEqual(res, {0: (2, 3), 3: (1, 2), 1: (1, 1)})

    def test_longueurs_bfs(self):
        g = open_digraph.empty()
        for i in range(10):
            g.add_node(id=i)
        edges = [(0, 3), (1, 4), (1, 5), (1, 8),(2, 4),(3, 5), 
        (3, 6), (3, 7),(4, 6),(5, 7),(6, 8), (6, 9)]
        g.add_edges(edges)
        b = bool_circ(g)
        
        dist, prev = b.longueurs_bfs(3, direction=1)
        self.assertEqual(dist, {3: 0, 5: 1, 6: 1, 7: 1, 8: 2, 9: 2})
        self.assertEqual(prev, {5: 3, 6: 3, 7: 3, 8: 6, 9: 6})
        
        dist2, prev2 = b.longueurs_bfs(8, direction=-1)
        self.assertEqual(dist2, {8: 0, 1: 1, 6: 1, 3: 2, 4: 2, 0: 3, 2: 3})
        self.assertEqual(prev2[3], 6)
        self.assertEqual(prev2[4], 6)
        self.assertEqual(prev2[0], 3)
        self.assertEqual(prev2[2], 4)
        dist3,prev3 = b.longueurs_bfs(7,direction=-1)
        #b.save_as_pdf("exec_soutenance.pdf", verbose=True)
        print("\nDistances depuis le noeud 3 vers les enfants")
        print(dist)
        print("\nDistances depuis le noeud 7 vers les parents")
        print(dist3)
        print("\nDistances depuis le noeud 7, direction None")
        dist4,prev4 = b.longueurs_bfs(7,direction=None)
        print(dist4)

    def test_shortest_path(self):
        g = open_digraph.empty()
        for i in range(10):
            g.add_node(id=i, label=str(i))
        edges = [(0, 3), (1, 4), (1, 5), (1, 8),(2, 4),(3, 5), 
        (3, 6), (3, 7),(4, 6),(5, 7),(6, 8), (6, 9)]
        g.add_edges(edges)
        b = bool_circ(g)
        
        dist, path = b.shortest_path(3, 8)
        self.assertEqual(dist, 2)
        self.assertEqual(path, [3, 6, 8])
        
        dist2, path2 = b.shortest_path(1, 9)
        self.assertEqual(dist2, 3)
        self.assertTrue(path2 == [1, 3, 6, 9] or path2 == [1, 4, 6, 9])
        
        # Test de chemin impossible
        dist3, path3 = b.shortest_path(7, 0) #Implicitement direction = 1
        self.assertIsNone(dist3)
        self.assertEqual(path3, [])

    def test_tri_topologique(self):
        g = open_digraph.empty()
        for i in range(10):
            g.add_node(id=i)
        edges = [(0, 3), (1, 4), (1, 5), (1, 8),(2, 4),(3, 5), 
        (3, 6), (3, 7),(4, 6),(5, 7),(6, 8), (6, 9)]
        g.add_edges(edges)
        b = bool_circ(g)
        
        tri = b.tri_topologique()
        attendu = [{0, 1, 2}, {3, 4}, {5, 6}, {7, 8, 9}]
        self.assertEqual(tri, attendu)


    def test_longest_path(self):
        g = open_digraph.empty()
        for i in range(10):
            g.add_node(id=i)
        edges = [(0, 3), (1, 4), (1, 5), (1, 8),(2, 4),(3, 5), 
        (3, 6), (3, 7),(4, 6),(5, 7),(6, 8), (6, 9)]
        g.add_edges(edges)
        b = bool_circ(g)
        
        # 1 à 5
        dist, path = b.longest_path(1, 5)
        self.assertEqual(dist, 1) # Pas 2 car (1,3) n'existe 
        
        # 1 à 3 (impossible)
        res = b.longest_path(1, 3)
        self.assertIsNone(res)
        
        # 1 à 8 
        dist2, path2 = b.longest_path(1, 8)
        self.assertEqual(dist2, 3) # Pas 1

    def test_identity(self):
        g_id = open_digraph.identity(3)
        self.assertTrue(g_id.well_formed())
        self.assertEqual(len(g_id.get_nodes()), 6)
        self.assertEqual(len(g_id.inputs_ids()), 3)
        self.assertEqual(len(g_id.outputs_ids()), 3)
        
        # Composition séquentielle avec l'élément neutre
        # Graphe quelconque f avec 2 entrées et 3 sorties
        f_graph = open_digraph.empty()
        in1 = f_graph.add_node()
        in2 = f_graph.add_node()
        out1 = f_graph.add_node()
        out2 = f_graph.add_node()
        out3 = f_graph.add_node()
        f_graph.add_input_node(in1)
        f_graph.add_input_node(in2)
        f_graph.add_output_node(out1)
        f_graph.add_output_node(out2)
        f_graph.add_output_node(out3)
        
        n1 = f_graph.add_node()
        n2 = f_graph.add_node()
        n3 = f_graph.add_node()
        
        f_graph.add_edge(in1, n1)
        f_graph.add_edge(in2, n2)
        f_graph.add_edge(n1, n3)
        f_graph.add_edge(n1, out1)
        f_graph.add_edge(n2, out2)
        f_graph.add_edge(n3, out3)
        
        b = bool_circ(f_graph)
        b_id_droite = bool_circ(open_digraph.identity(3)) # f à 3 sorties
        b_id_gauche = bool_circ(open_digraph.identity(2)) # f à 2 entrées
        
        compo_droite = b.compo_sequentielle(b_id_droite)
        compo_gauche = b_id_gauche.compo_sequentielle(b)
        
        self.assertEqual(len(compo_droite.get_nodes()), len(b.get_nodes()))
        self.assertEqual(len(compo_droite.inputs_ids()), len(b.inputs_ids()))
        self.assertEqual(len(compo_droite.outputs_ids()), len(b.outputs_ids()))
        
        self.assertEqual(len(compo_gauche.get_nodes()), len(b.get_nodes()))
        self.assertEqual(len(compo_gauche.inputs_ids()), len(b.inputs_ids()))
        self.assertEqual(len(compo_gauche.outputs_ids()), len(b.outputs_ids()))


    def test_formula_to_tree(self):
        # Test de la formule "a AND b"
        formula = "((x0)&((x1)&(x2)))|((x1)&(~(x2)))"
        tree,ids = bool_circ.formula_to_tree(formula)
        self.assertEqual(ids, ["x0", "x1", "x2"])
        #tree.display()

    def test_formula_to_treeExtend(self):
        # Test de la formule "a AND b"
        tree,ids = bool_circ.formula_to_treeExtend("((x0)&((x1)&(x2)))|((x1)&(~(x2)))", "((x0)&(~(x1)))|(x2)")
        self.assertEqual(ids, ["x0", "x1", "x2"])
        #tree.display(True)
    
    def test_acyclicToBoolRandom(self):
        g = open_digraph.empty()
        for i in range(10):
            g.add_node()
        edges = [(0, 3), (1, 4), (1, 5), (1, 8),(2, 4),(3, 5), 
        (3, 6), (3, 7),(4, 6),(5, 7),(6, 8), (6, 9)]
        g.add_edges(edges)
        #g.save_as_dot_file("test_acyclicToBoolRandomBefore.dot")
        b = bool_circ.acyclicToBoolRandom(g,nbInput=4)
        #b.save_as_dot_file("test_acyclicToBoolRandomAfter.dot")
        print(len(b.outputs_ids()))
        #b.display()
       
    def test_acyclicToBoolRandom_depuis_vide(self):
        g = open_digraph.empty()
        b = bool_circ.acyclicToBoolRandom(g, nbInput=2, nbOutput=3)
        self.assertEqual(len(b.inputs_ids()), 2)
        self.assertEqual(len(b.outputs_ids()), 3)
        #b.display()
        b = bool_circ.acyclicToBoolRandom(g)
        self.assertEqual(len(b.inputs_ids()), 0)
        self.assertEqual(b, bool_circ.empty())
        
        
    def test_Adder(self):
        #bool_circ.adder0().display()
        #bool_circ.adder0().save_as_pdf("adder0.pdf")
        #bool_circ.half_adder(0).save_as_pdf("halfadder0.pdf")
        #bool_circ.adder(1).display()
        return
    
    def test_Registre(self):
        b = bool_circ.registre(11)
        #b.display()
        
    def test_simplifie_copie(self):
        b = bool_circ.registre(11)
        g = open_digraph.empty()
        for i in range(10):
            g.add_node()
        edges = [(0, 3), (1, 4), (1, 5), (1, 8),(2, 4),(3, 5), 
        (3, 6), (3, 7),(4, 6),(5, 7),(6, 8), (6, 9)]
        g.add_edges(edges)
        b2 = bool_circ.acyclicToBoolRandom(g,nbInput=8)
        b3 = b.compo_sequentielle(b2)
        #b3.save_as_dot_file("test_simplifie_naif_before.dot")
        b3.simplifier_naif()
        #b3.save_as_dot_file("test_simplifie_naif_after.dot")
  
    def test_eq_and_copy(self):
        g_copy = self.g.copy()
        self.assertEqual(self.g, g_copy)
        self.assertIsNot(self.g, g_copy)
        g_copy.add_node()
        self.assertNotEqual(self.g, g_copy)

    def test_min_max_id(self):
        self.assertEqual(self.g.min_id(), 0)
        self.assertEqual(self.g.max_id(), 2)
        g_empty = open_digraph.empty()
        self.assertIsNone(g_empty.min_id())
        self.assertIsNone(g_empty.max_id())

    def test_adjacency_matrix(self):
        matrix = [[0, 1, 0], [0, 0, 2], [0, 0, 0]]
        g = open_digraph.from_adjacency_matrix(matrix)
        self.assertEqual(g.adjacency_matrix(), matrix)

    def test_is_cyclic(self):
        g = open_digraph.empty()
        g.add_node(id=0)
        g.add_node(id=1)
        g.add_node(id=2)
        g.add_edges([(0, 1), (1, 2), (2, 0)])
        self.assertTrue(g.is_cyclic())
        self.assertFalse(self.g.is_cyclic())

    def test_connected_components(self):
        g = open_digraph.empty()
        g.add_node(id=0)
        g.add_node(id=1)
        g.add_node(id=2)
        g.add_node(id=3)
        g.add_edge(0, 1)
        g.add_edge(2, 3)
        num_comps, comp_dict = g.connected_components()
        self.assertEqual(num_comps, 2)
        self.assertEqual(comp_dict[0], comp_dict[1])
        self.assertEqual(comp_dict[2], comp_dict[3])
        self.assertNotEqual(comp_dict[0], comp_dict[2])

        graphs, io = g.connected_components_graphs()
        self.assertEqual(len(graphs), 2)
        self.assertTrue(0 in graphs[comp_dict[0]].nodes and 1 in graphs[comp_dict[0]].nodes)
        self.assertTrue(2 in graphs[comp_dict[2]].nodes and 3 in graphs[comp_dict[2]].nodes)

    def test_remove_node(self):
        g = self.g.copy()
        g.remove_node_by_id(1)
        self.assertNotIn(1, g.nodes)
        self.assertEqual(g.nodes[0].get_children(), {})
        self.assertEqual(g.nodes[2].get_parents(), {})

    def test_profondeur(self):
        g = open_digraph.empty()
        for i in range(4):
            g.add_node(id=i)
        g.add_edges([(0, 1), (1, 2), (2, 3)])
        self.assertEqual(g.profondeur(), 4)
        self.assertEqual(g.profondeur_noeud(0), 1)
        self.assertEqual(g.profondeur_noeud(3), 4)

    def test_random_graph_form(self):
        g = open_digraph.random(5, 3, form="DAG")
        self.assertEqual(len(g.nodes), 5)
        self.assertFalse(g.is_cyclic())

    def test_Somme(self):
        somme = bool_circ.somme(37,120)
        self.assertEqual(somme, 157)
    
    def test_Somme_cla_4_bits(self):
        somme = bool_circ.cla_somme4(6, 12)
        self.assertEqual(somme, 18)
    
    def test_cla_adder4(self):
        cla = bool_circ.cla_adder4()
        #cla.save_as_pdf("test_cla_adder4bits.pdf")

    def test_cla_addern(self):
        cla = bool_circ.cla_adder(3)
        #cla.save_as_pdf("test_cla_adder_2x4.pdf")
        somme = bool_circ.cla_somme(37,120)
        self.assertEqual(somme, 157)
        
    def test_cla_adder16(self):
        cla= bool_circ.cla_adder16()
        #cla.save_as_pdf("test_cla_adder16bits.pdf")
        somme = bool_circ.cla_somme16(28240,12345)
        self.assertEqual(somme, 28240+12345)

class NodeTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'i', {1: 1}, {2: 2})
        
    def test_getters_setters(self):
        self.assertEqual(self.n0.get_id(), 0)
        self.assertEqual(self.n0.get_label(), 'i')
        self.assertEqual(self.n0.get_parents(), {1: 1})
        self.assertEqual(self.n0.get_children(), {2: 2})
        self.n0.set_id(5)
        self.assertEqual(self.n0.get_id(), 5)
        
    def test_add_remove_child_parent(self):
        self.n0.add_child_id(3, 1)
        self.assertEqual(self.n0.get_children(), {2: 2, 3: 1})
        self.n0.remove_child_once(2)
        self.assertEqual(self.n0.get_children(), {2: 1, 3: 1})
        self.n0.remove_child_id(2)
        self.assertEqual(self.n0.get_children(), {3: 1})

    def test_degree(self):
        self.assertEqual(self.n0.indegree(), 1)
        self.assertEqual(self.n0.outdegree(), 2)
        self.assertEqual(self.n0.degree(), 3)

    def test_encodeur(self):
        encodeur = bool_circ.encodeur()
        #encodeur.save_as_pdf("test_encodeur.pdf")
    
    def test_decodeur(self):
        decodeur = bool_circ.decodeur()
        #decodeur.save_as_pdf("test_decodeur.pdf")

    def test_point_2(self):
        print("\n" + "="*50)
        print("POINT 2 : Évaluation d'un half-adder sur 1 bit")
        print("="*50)
        registre1 = bool_circ.registre(1, n=1)
        registre2 = bool_circ.registre(1, n=1)
        registres = registre1.compo_parallele(registre2)
        half_adder = bool_circ.half_adder(0)
        circuit_complet = registres.compo_sequentielle(half_adder)
        print(f"Entrées du circuit : {circuit_complet.inputs_ids()}")
        print(f"Sorties du circuit : {circuit_complet.outputs_ids()}")
        tri_topo = circuit_complet.tri_topologique()
        print("\nÉtapes intermédiares :")
        for i, niveau in enumerate(tri_topo):
            labels = []
            for noeud_id in niveau:
                noeud = circuit_complet.get_node_by_id(noeud_id)
                label = noeud.get_label() if noeud.get_label() != "" else "copie/sortie"
                labels.append(f"ID : {noeud_id} | label : {label}")
            print(f"niveau {i} : {', '.join(labels)}")
        resultat = circuit_complet.evaluer()
        print(f"\n Résultat final de l'évaluation (1 + 1) : {resultat}")
        #circuit_complet.save_as_pdf("point2_evaluation_trace.pdf", verbose=True)

    def test_point_3(self):
        print("\n" + "="*50)
        print("POINT 3 : Complexité du Half-Adder classique")
        print("="*50)
        
        print(f"{'n (taille = 2^n)':<20} | {'Profondeur':<12} | {'Nb Noeuds/Portes':<18} | {'Plus court chemin'}")
        print("-" * 75)

        for n in range(5):
            half_adder = bool_circ.half_adder(n)
            pr = half_adder.profondeur()
            nb_noeuds =len(half_adder.get_nodes())

            min_path = float('inf')
            for in_id in half_adder.inputs_ids():
                for out_id in half_adder.outputs_ids():
                    dist, path = half_adder.shortest_path(in_id, out_id)
                    if dist is not None and dist < min_path:
                        min_path = dist
            print(f"n={n} ({2**n} bits){'':<8} | {pr:<12} | {nb_noeuds:<18} | {min_path}")
        
        print("\n" + "-"*75)
        print("Bonus CLA :")
        print(f"{'n (taille = 2^n)':<25} | {'Profondeur':<12} | {'Nombre de noeuds/Portes':<18} | {'Plus court chemin'}")
        print("-"*75)

        for n in range(2, 4):
            cla = bool_circ.cla_half_adder(n)
            pr = cla.profondeur()
            nb_noeuds = len(cla.get_nodes())
            min_path = float('inf')
            for in_id in cla.inputs_ids():
                for out_id in cla.outputs_ids():
                    dist, path = cla.shortest_path(in_id, out_id)
                    if dist is not None and dist < min_path:
                        min_path = dist       
            print(f"n={n} ({2**n} bits) CLA {'':<8} | {pr:<12} | {nb_noeuds:<23} | {min_path}")

    def test_point_4(self):
        print("\n" + "="*50)
        print("POINT 4 : Étapes de simplification (comme sur le diagramme)")
        print("="*50)

        print(f"\n--- Test: Associativité de XOR ---")
        g1 = open_digraph.empty()
        e1_1, e1_2, e1_3 = g1.add_node(label=""), g1.add_node(label=""), g1.add_node(label="")
        xor_p, xor_e = g1.add_node(label="^"), g1.add_node(label="^")
        s1 = g1.add_node(label="")
        for i in [e1_1, e1_2, e1_3]: g1.add_input_id(i)
        g1.add_output_id(s1)
        g1.add_edge(e1_1, xor_p); g1.add_edge(e1_2, xor_p)
        g1.add_edge(e1_3, xor_e); g1.add_edge(xor_p, xor_e)
        g1.add_edge(xor_e, s1)
        c1 = bool_circ(g1)
        #c1.save_as_pdf("projet-info/Point-4-Rapport/img1_associativite_xor_AVANT.pdf", verbose=False)
        c1.simplifier_xor_associativite()
        #c1.save_as_pdf("projet-info/Point-4-Rapport/img1_associativite_xor_APRES.pdf", verbose=False)

        print(f"\n--- Test: Associativité de la copie ---")
        g2 = open_digraph.empty()
        e2 = g2.add_node(label="")
        copie_p, copie_e = g2.add_node(label=""), g2.add_node(label="")
        s2_1, s2_2, s2_3 = g2.add_node(label=""), g2.add_node(label=""), g2.add_node(label="")
        g2.add_input_id(e2)
        for o in [s2_1, s2_2, s2_3]: g2.add_output_id(o)
        g2.add_edge(e2, copie_p)
        g2.add_edge(copie_p, copie_e)
        g2.add_edge(copie_p, s2_1)
        g2.add_edge(copie_e, s2_2)
        g2.add_edge(copie_e, s2_3)
        c2 = bool_circ(g2)
        #c2.save_as_pdf("projet-info/Point-4-Rapport/img2_associativite_copie_AVANT.pdf", verbose=False)
        c2.simplifier_copie_associativite()
        #c2.save_as_pdf("projet-info/Point-4-Rapport/img2_associativite_copie_APRES.pdf", verbose=False)

        print(f"\n--- Test: Involution de XOR ---")
        g3 = open_digraph.empty()
        e3_1, e3_2 = g3.add_node(label=""), g3.add_node(label="")
        xor3 = g3.add_node(label="^")
        s3_xor, s3_other = g3.add_node(label=""), g3.add_node(label="")
        g3.add_input_id(e3_1); g3.add_input_id(e3_2)
        g3.add_output_id(s3_xor); g3.add_output_id(s3_other)
        g3.add_edge(e3_1, xor3); g3.add_edge(e3_1, xor3)
        g3.add_edge(e3_1, s3_other) 
        g3.add_edge(e3_2, xor3)
        g3.add_edge(xor3, s3_xor)
        c3 = bool_circ(g3)
        #c3.save_as_pdf("projet-info/Point-4-Rapport/img3_involution_xor_AVANT.pdf", verbose=False)
        c3.simplifier_xor_involution()
        #c3.save_as_pdf("projet-info/Point-4-Rapport/img3_involution_xor_APRES.pdf", verbose=False)

        print(f"\n--- Test: Effacement (nettoyer_noeuds_morts) ---")
        g4 = open_digraph.empty()
        e4 = g4.add_node(label="")
        op4 = g4.add_node(label="op")
        g4.add_input_id(e4)
        g4.add_edge(e4, op4)
        c4 = bool_circ(g4)
        #c4.save_as_pdf("projet-info/Point-4-Rapport/img4_effacement_AVANT.pdf", verbose=False)
        c4.nettoyer_noeuds_morts()
        #c4.save_as_pdf("projet-info/Point-4-Rapport/img4_effacement_APRES.pdf", verbose=False)

        print(f"\n--- Test: NON à travers XOR ---")
        g5 = open_digraph.empty()
        e5_1, e5_2 = g5.add_node(label=""), g5.add_node(label="")
        not5 = g5.add_node(label="~")
        xor5 = g5.add_node(label="^")
        s5 = g5.add_node(label="")
        g5.add_input_id(e5_1); g5.add_input_id(e5_2)
        g5.add_output_id(s5)
        g5.add_edge(e5_1, not5)
        g5.add_edge(not5, xor5)
        g5.add_edge(e5_2, xor5)
        g5.add_edge(xor5, s5)
        c5 = bool_circ(g5)
        #c5.save_as_pdf("projet-info/Point-4-Rapport/img5_non_travers_xor_AVANT.pdf", verbose=False)
        c5.simplifier_non_travers_xor()
        #c5.save_as_pdf("projet-info/Point-4-Rapport/img5_non_travers_xor_APRES.pdf", verbose=False)

        print(f"\n--- Test: NON à travers la copie ---")
        g6 = open_digraph.empty()
        e6 = g6.add_node(label="")
        not6 = g6.add_node(label="~")
        copie6 = g6.add_node(label="")
        s6_1, s6_2 = g6.add_node(label=""), g6.add_node(label="")
        g6.add_input_id(e6)
        g6.add_output_id(s6_1); g6.add_output_id(s6_2)
        g6.add_edge(e6, not6)
        g6.add_edge(not6, copie6)
        g6.add_edge(copie6, s6_1)
        g6.add_edge(copie6, s6_2)
        c6 = bool_circ(g6)
        #c6.save_as_pdf("projet-info/Point-4-Rapport/img6_non_travers_copie_AVANT.pdf", verbose=False)
        c6.simplifier_non_travers_copie()
        #c6.save_as_pdf("projet-info/Point-4-Rapport/img6_non_travers_copie_APRES.pdf", verbose=False)

        print(f"\n--- Test: Involution de NON ---")
        g7 = open_digraph.empty()
        e7 = g7.add_node(label="")
        not7_1, not7_2 = g7.add_node(label="~"), g7.add_node(label="~")
        s7 = g7.add_node(label="")
        g7.add_input_id(e7)
        g7.add_output_id(s7)
        g7.add_edge(e7, not7_1)
        g7.add_edge(not7_1, not7_2)
        g7.add_edge(not7_2, s7)
        c7 = bool_circ(g7)
        #c7.save_as_pdf("projet-info/Point-4-Rapport/img7_involution_non_AVANT.pdf", verbose=False)
        c7.simplifier_non_involution()
        #c7.save_as_pdf("projet-info/Point-4-Rapport/img7_involution_non_APRES.pdf", verbose=False)

        print("\nTous les tests de schémas sont terminés et les PDF sont générés !")


if __name__ == '__main__': 
    unittest.main()
    