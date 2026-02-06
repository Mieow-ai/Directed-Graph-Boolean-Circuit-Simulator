from modules.open_digraph import *
import inspect

n0 = node(0, 'i', {}, {1:1})
n1 = node(1, 'a', {0:1}, {2:2})
n2 = node(2, 'o', {1:2}, {})
g = open_digraph([0], [2], [n0, n1, n2])
print(g)
print([n0, n1, n2])

print("######################################")
print("Les méthodes de node sont :")
print(dir(node))
print("Les méthodes de open_digraph sont :")
print(dir(open_digraph))
print("######################################")

path = inspect.getfile(node)
doc = inspect.getdoc(node.__init__)
code = inspect.getsource(node.__init__)
print(f"La fichier dans lequel se trouve node est : {path} \nLe docstring de node.__init__ est : {doc} \nLe code de node.__init__ est : \n {code}")
print("######################################")
