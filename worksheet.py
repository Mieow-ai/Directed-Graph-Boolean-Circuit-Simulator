from modules.open_digraph import *

n0 = node(0, 'i', {}, {1:1})
n1 = node(1, 'a', {0:1}, {2:2})
n2 = node(2, 'o', {1:2}, {})
g = open_digraph([0], [2], [n0, n1, n2])
print(g)
print([n0, n1, n2])