from channel import Channel
from node import Node
from threading import Thread
import time
import udp_support as udp
import random

print(" ___                     _                _          ___  _               _        _")
print("| _ ) _ _  ___  __ _  __| | __  __ _  ___| |_       / __|(_) _ __   _  _ | | __ _ | |_  ___  _ _")
print("| _ \| '_|/ _ \/ _` |/ _` |/ _|/ _` |(_-/|  _|      \__ \| || '  \ | || || |/ _` ||  _|/ _ \| '_|")
print("|___/|_|  \___/\__/_|\__/_|\__|\__/_|/__/ \__|      |___/|_||_|_|_| \_._||_|\__/_| \__|\___/|_|")
print("--------------------------------------------------------------------------------------------------")

# Take inputs for filing variables
n_nodes = int(input("Insert the number of nodes in the distributed system: "))
arrival_rate = float(input("Insert the arrival rate for the broadcast requests: "))   # lambda
service_rate = float(input("Insert the service rate of the nodes: "))   # node mu
channel_bandwidth = float(input("Insert the capacity of the channels in the distributed system: "))   # channel mu
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


run_id = random.randint(0, 1000000)

nodes_list = []
channel_list = []
n_crash = 0

# Global dictionary to connect a pair of nodes to the right channel linking them
nodes_to_channel = {}
current_port = 9000 + n_nodes

def launch_node(id_node, nodes_to_channel):
    n = Node(id_node, n_nodes, broadcast_type, arrival_rate, service_rate, start_time, may_crash, fan_out, n_rounds, nodes_to_channel)
    nodes_list.append(n)
    n.start_node()

def launch_channel(node1, node2):
    global current_port
    nodes_pair = (node1, node2)
    nodes_to_channel[nodes_pair] = current_port
    current_port += 1
    channel = Channel(nodes_to_channel[nodes_pair], node1, node2, channel_bandwidth)
    channel_list.append(channel)
    udp.start_udp_server(channel)

for m in range(n_nodes):
    for n in range(m, n_nodes):
        Thread(target = launch_channel, args = [m,n], daemon = True).start()

for n in range(n_nodes):
    Thread(target = launch_node, args = [n, nodes_to_channel], daemon = True).start()

input('Press ENTER to quit\n')
finish_time = time.time()
run_duration = finish_time - start_time


with open(f"stats_file_{run_id}_{broadcast_type}_crash_{may_crash}.txt","a") as stats_file:
    stats_file.write(f"Statistics of run {run_id}\n")
    stats_file.write("Broadcast Type: ")
    if broadcast_type == "lazy_rb":
        stats_file.write("Lazy Reliable Broadcast\n")
    elif broadcast_type == "eager_rb":
        stats_file.write("Eager Reliable Broadcast\n")
    elif broadcast_type == "eager_prob":
        stats_file.write("Eager Probabilistic Broadcast\n")

    stats_file.write(f"Number of nodes in the system: {n_nodes}\n")
    stats_file.write(f"Arrival rate of the bradcast requests: {arrival_rate} requests/s\n")
    stats_file.write(f"Service rate of the node: {service_rate} msgs/s\n")
    stats_file.write(f"Channel bandwidth: {channel_bandwidth} msgs/s\n")
    if may_crash == False:
        stats_file.write("No failures\n")
    else:
        stats_file.write("Processes can fail by crash\n")

    if broadcast_type == "eager_prob":
        stats_file.write(f"Fan-out for the gossip: {fan_out}\n")
        stats_file.write(f"Number of rounds to perform: {n_rounds}\n")
    
    stats_file.write(f"Duration of the run : {run_duration} s\n")
    if arrival_rate <= channel_bandwidth:
        stats_file.write(f"The system is stable\n")
    else:
        stats_file.write(f"The system is NOT stable\n")
    stats_file.write("--------------------------------------------------- NODES --------------------------------------------------------------\n")

    nodes_avg_response_time = 0
    nodes_throughput = 0
    nodes_utilization = 0
    for node in nodes_list:
        if node.alive == False:
            n_crash += 1
        node.throughput = node.broadcast_requests / run_duration
        node.utilization = (1/service_rate) * node.throughput                       # Utilization in terms of messages sent by a node in 1 second
        if nodes_avg_response_time == 0:                                                      # First node considered
            nodes_avg_response_time = node.avg_response_time
            nodes_throughput = node.throughput
            nodes_utilization = node.utilization
        else:
            nodes_avg_response_time = (nodes_avg_response_time + node.avg_response_time) / 2
            nodes_throughput = (nodes_throughput + node.throughput) / 2
            nodes_utilization = (nodes_utilization + node.utilization) / 2
        
        stats_file.write(f"------------------------------------------------- PROCESS {node.id} ------------------------------------------------------------\n")
        stats_file.write(f"Received messages in total: {node.received_messages_total} msgs\n")
        stats_file.write(f"Delivered unique messages: {node.unique_messages} msgs\n")
        stats_file.write(f"Broadcast requests processed: {node.broadcast_requests} requests\n")
        stats_file.write(f"Average Response Time (expected time to deliver a message): {node.avg_response_time} s\n")
        stats_file.write(f"Average Throughput (broadcast requests processed in 1 second): {node.throughput} processed requests/s\n")
        stats_file.write(f"Average Throughput (messages sent in 1 second): {node.throughput * n_nodes} msgs/s\n")
        stats_file.write(f"Average Utilization: {node.utilization * 100} %\n")

    stats_file.write("-------------------------------------------------- CHANNELS ------------------------------------------------------------\n")
    channels_avg_response_time = 0
    channels_throughput = 0
    channels_utilization = 0
    for channel in channel_list:
        channel.throughput = channel.received_messages / run_duration
        channel.utilization = (1/channel_bandwidth) * channel.throughput
        if channels_avg_response_time == 0:                                 # First channel considered
            channels_avg_response_time = channel.avg_response_time
            channels_throughput = channel.throughput
            channels_utilization = channel.utilization
        else:
            channels_avg_response_time = (channels_avg_response_time + channel.avg_response_time) / 2
            channels_throughput = (channels_throughput + channel.throughput) / 2
            channels_utilization = (channels_utilization + channel.utilization) / 2

        stats_file.write(f"------------------------------------------------ CHANNEL ({channel.node1},{channel.node2}) ---------------------------------------------------------\n")
        stats_file.write(f"Average Response Time: {channel.avg_response_time} msgs/s\n")
        stats_file.write(f"Average Throughput (messages sent in 1 second): {channel.throughput} msgs/s\n")
        stats_file.write(f"Average Utilization: {channel.utilization * 100} %\n")
    
    stats_file.write("--------------------------------------------- AGGREGATE STATISTICS -----------------------------------------------------\n")

    if may_crash == True:
        stats_file.write(f"Number of crash happened: {n_crash}\n")

    stats_file.write(f"Average Total Response Time for a request (considering a generic channel followed by a generic node) is: {nodes_avg_response_time} s\n")
    stats_file.write(f"Average Throughput for a node: {nodes_throughput} processed requests/s\n")
    stats_file.write(f"Average Throughput for a node: {nodes_throughput * n_nodes} msgs/s\n")
    stats_file.write(f"Average Utilization for a node: {nodes_utilization * 100} %\n")
    stats_file.write(f"Average Throughput for a channel: {channels_throughput} msgs/s\n")
    stats_file.write(f"Average Utilization for a channel: {channels_utilization * 100} %\n")


print(f"END OF THE RUN! The stats of the run are available at stats_file_{run_id}.txt.")


