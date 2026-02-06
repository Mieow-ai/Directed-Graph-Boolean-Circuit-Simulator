import sys
import os
root = os.path.normpath(os.path.join(__file__, './../..'))
sys.path.append(root) # allows us to fetch files from the project root
import unittest
from modules.open_digraph import *

class InitTest(unittest.TestCase):

    def test_init_node(self):
        n0 = node(0, 'i', {}, {1:1})
        self.assertEqual(n0.id, 0)
        self.assertEqual(n0.label, 'i')
        self.assertEqual(n0.parents, {})
        self.assertEqual(n0.children, {1:1})
        self.assertIsInstance(n0, node)
        self.assertIsNot(n0.copy(), n0)
    
    def test_init_open_digraph(self):
        n0 = node(0, 'i', {}, {1:1})
        n1 = node(1, 'a', {0:1}, {2:2})
        n2 = node(2, 'o', {1:2}, {})
        g = open_digraph([0], [2], [n0, n1, n2])
        self.assertEqual(g.inputs, [0])
        self.assertEqual(g.outputs, [2])
        self.assertEqual(g.nodes, {0:n0, 1:n1, 2:n2})
        self.assertIsInstance(g, open_digraph)
        self.assertIsNot(g.copy(), g)
        new_id = g.new_id()
        self.assertEqual(new_id, 3)
        g.add_edge(0, 2)
        self.assertEqual(n0.get_children()[2], 1)
        self.assertEqual(n2.get_parents()[0], 1)
        

if __name__ == '__main__': # the following code is called only when
    unittest.main()        # precisely this file is run

class NodeTest(unittest.TestCase):
    def setUp(self):
        self.n0 = node(0, 'i', [],[1])
    