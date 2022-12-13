from channel import Channel
from node import Node
from threading import Thread
import time

### PRINT TITLE OF THE FRAMEWORK
### Take inputs for filing variables

n_nodes = 4
arrival_rate = 0.2   # lambda
channel_bandwidth = 10   # mu
broadcast_type = "eager_prob"
start_time = time.time()
may_crash = False
# If prob brod
fan_out = 2

def launch_node(id_node):
    Node(id_node, n_nodes, broadcast_type, arrival_rate, start_time, may_crash, fan_out)

def launch_channel(node1, node2):
    Channel(node1, node2, channel_bandwidth)
   

for n in range(n_nodes):
    Thread(target = launch_node, args = [n], daemon = True).start()

for m in range(n_nodes):
    for n in range(m, n_nodes):
        Thread(target = launch_channel, args = [m,n], daemon = True).start()

input('Press ENTER to quit\n')