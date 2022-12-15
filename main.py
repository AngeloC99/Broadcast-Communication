from channel import Channel
from node import Node
from threading import Thread
import time
import udp_support as udp
import random
"""
print(" ___                     _                _          ___  _               _        _")
print("| _ ) _ _  ___  __ _  __| | __  __ _  ___| |_       / __|(_) _ __   _  _ | | __ _ | |_  ___  _ _")
print("| _ \| '_|/ _ \/ _` |/ _` |/ _|/ _` |(_-/|  _|      \__ \| || '  \ | || || |/ _` ||  _|/ _ \| '_|")
print("|___/|_|  \___/\__/_|\__/_|\__|\__/_|/__/ \__|      |___/|_||_|_|_| \_._||_|\__/_| \__|\___/|_|")
print("--------------------------------------------------------------------------------------------------")

# Take inputs for filing variables
n_nodes = int(input("Insert the number of nodes in the distributed system: "))
arrival_rate = float(input("Insert the arrival rate for the broadcast requests: "))   # lambda
channel_bandwidth = float(input("Insert the capacity of the channels in the distributed system: "))   # mu
print("Choose the broadcast protocol to run:")
print("a) Lazy Reliable Broadcast")
print("b) Eager Reliable Broadcast")
print("c) Eager Probabilistic Broadcast")
broadcast_choice = input("Your choice: ").lower()
broadcast_type = None
while broadcast_type == None:
    if broadcast_choice == "a":
        broadcast_type = "lazy_rb"
    elif broadcast_choice == "b":
        broadcast_type = "eager_rb"
    elif broadcast_choice == "c":
        broadcast_type = "eager_prob"
    else:
        print("NOT VALID INPUT! PLEASE TRY AGAIN!")
        broadcast_choice = input("Your choice: ")

start_time = time.time()

print("Nodes in the distributed system can crash?")
print("y) Yes")
print("n) No")
may_crash = None
crash_choice = input("Your choice: ").lower()
while may_crash== None:
    if crash_choice == "y":
        may_crash = True
    elif crash_choice == "n":
        may_crash = False
    else:
        print("NOT VALID INPUT! PLEASE TRY AGAIN!")
        crash_choice = input("Your choice: ")

fan_out = None
n_rounds = None
if broadcast_type == "eager_prob":
    fan_out = int(input("Fan-out for the gossip (number of processes to which forward the message in each round): "))
    n_rounds = int(input("Number of rounds to perform: "))

"""
run_id = random.randint(0, 1000000)

n_nodes = 7
arrival_rate = 0.2   # lambda
channel_bandwidth = 10   # mu
broadcast_type = "lazy_rb"
start_time = time.time()
may_crash = True
# If prob brod
fan_out = 2
n_rounds = 3

nodes_list = []

# Global dictionary to connect a pair of nodes to the right channel linking them
nodes_to_channel = {}
current_port = 9000 + n_nodes

def launch_node(id_node, nodes_to_channel):
    n = Node(id_node, n_nodes, broadcast_type, arrival_rate, start_time, may_crash, fan_out, n_rounds, nodes_to_channel)
    nodes_list.append(n)
    n.start_node()

def launch_channel(node1, node2):
    global current_port
    nodes_pair = (node1, node2)
    nodes_to_channel[nodes_pair] = current_port
    current_port += 1
    channel = Channel(nodes_to_channel[nodes_pair], node1, node2, channel_bandwidth)
    udp.start_udp_server(channel)

for m in range(n_nodes):
    for n in range(m, n_nodes):
        Thread(target = launch_channel, args = [m,n], daemon = True).start()

for n in range(n_nodes):
    Thread(target = launch_node, args = [n, nodes_to_channel], daemon = True).start()

input('Press ENTER to quit\n')

with open(f"stats_file_{run_id}.txt","a") as stats_file:
    stats_file.write(f"Statistics of run {run_id}:\n")

    for node in nodes_list:
        stats_file.write("----------------------------\n")
        stats_file.write(f"Process {node.id}\n")
        stats_file.write(f"Received messages in total: {node.received_messages_total}\n")
        stats_file.write(f"Delivered unique messages: {node.unique_messages}\n")
        stats_file.write(f"Broadcast requests processed: {node.broadcast_requests}\n")
        stats_file.write("----------------------------\n")

print("END OF THE RUN! Here you can find some interesting stats about it.")


# Print stats when the run is completed