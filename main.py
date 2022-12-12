from channel import Channel
from node import Node
from threading import Thread
import time

n_nodes = 7
channel_bandwidth = 10
start_time = time.time()

def launch_node(id_node):
    Node(id_node, n_nodes, "lazy_rb", start_time)

def launch_channel(node1, node2):
    Channel(node1, node2, channel_bandwidth)
   

for n in range(4):
    Thread(target = launch_node, args = [n], daemon = True).start()

for m in range(4):
    for n in range(m,4):
        Thread(target = launch_channel, args = [m,n], daemon = True).start()

input('Press ENTER to quit\n')