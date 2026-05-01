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
      
    """def test_random_graph(self):
        n = 5
        inputs_count = 2
        outputs_count = 2
    
        g = open_digraph.random(n, 3, inputs=inputs_count, outputs=outputs_count, form='DAG')
        self.assertEqual(len(g.nodes), n + inputs_count + outputs_count)
        self.assertEqual(len(g.inputs), inputs_count)
        self.assertEqual(len(g.outputs), outputs_count)
        self.assertEqual(g.inputs, [5, 6])
        self.assertEqual(g.outputs, [7, 8])"""
        
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
        
        n1 = f_graph.add_node();
        n2 = f_graph.add_node();
        n3 = f_graph.add_node();
        
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
        #tree.display(True)

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

    def test_acyclicToBoolRandom_vide(self):
        g = open_digraph.empty()
        b = bool_circ.acyclicToBoolRandom(g, nbInput=2, nbOutput=3)
        self.assertEqual(len(b.inputs_ids()), 2)
        self.assertEqual(len(b.outputs_ids()), 3)
        b = bool_circ.acyclicToBoolRandom(g)
        self.assertEqual(len(b.inputs_ids()), 0)
        self.assertEqual(b, bool_circ.empty())


    def test_Adder(self):
        #bool_circ.adder0().display()
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
        b3.save_as_dot_file("test_simplifie_naif_before.dot")
        b3.simplifier_naif()
        b3.save_as_dot_file("test_simplifie_naif_after.dot")
  

    def test_Somme(self):
        somme = bool_circ.somme(37,120)
        self.assertEqual(somme, 157)
        

        


if __name__ == '__main__': 
    unittest.main()        

class NodeTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'i', [],[1])
    