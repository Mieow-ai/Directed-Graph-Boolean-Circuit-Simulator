import sys
import os
root = os.path.normpath(os.path.join(__file__, './../..'))
sys.path.append(root) # allows us to fetch files from the project root
import unittest
from modules.open_digraph import *

class InitTest(unittest.TestCase):
    
    def setUp(self):
        self.n0 = node(0, 'i', {}, {1:1})
        self.n1 = node(1, 'a', {0:1}, {2:2})
        self.n2 = node(2, 'o', {1:2}, {})
        self.g = open_digraph([0], [2], [self.n0, self.n1, self.n2])
    
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
        self.n0 = node(0, 'i', {}, {1:1})
        self.n1 = node(1, 'a', {0:1}, {2:1})
        self.n2 = node(2, 'o', {1:1}, {})
        self.g2 = open_digraph([0], [2], [self.n0, self.n1, self.n2])
        self.assertTrue(self.g2.well_formed())
        self.g.add_edge(0, 2)
        self.assertFalse(self.g.well_formed())
        
        
    # Continuer les tests...
        

if __name__ == '__main__': # the following code is called only when
    unittest.main()        # precisely this file is run

class NodeTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'i', [],[1])
    