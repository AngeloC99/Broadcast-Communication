from node import Node
from threading import Thread
import time


n_nodes = 7
start_time = time.time()


def launch_node(id_node):
    Node(id_node, n_nodes, "lazy_rb", start_time)


for n in range(7):
    Thread(target = launch_node, args = [n], daemon = True).start()

input('Press ENTER to quit\n')
