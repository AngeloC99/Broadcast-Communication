from channel import Channel
from node import Node
from threading import Thread
import time
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
n_nodes = 7
arrival_rate = 0.2   # lambda
channel_bandwidth = 10   # mu
broadcast_type = "eager_prob"
start_time = time.time()
may_crash = False
# If prob brod
fan_out = 2
n_rounds = 3



def launch_node(id_node):
    Node(id_node, n_nodes, broadcast_type, arrival_rate, start_time, may_crash, fan_out, n_rounds)

def launch_channel(node1, node2):
    Channel(node1, node2, channel_bandwidth)
   

for n in range(n_nodes):
    Thread(target = launch_node, args = [n], daemon = True).start()

for m in range(n_nodes):
    for n in range(m, n_nodes):
        Thread(target = launch_channel, args = [m,n], daemon = True).start()

input('Press ENTER to quit\n')


# Print stats when the run is completed