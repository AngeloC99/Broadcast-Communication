from node import Node
from threading import Thread


n_nodes = 7


def launch_node(id_node):
    Node(id_node, n_nodes, "lazy_rb")


for n in range(7):
    Thread(target = launch_node, args = [n], daemon = True).start()

input('Press ENTER to quit')
