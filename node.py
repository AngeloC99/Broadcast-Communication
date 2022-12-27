import random
from collections import deque
from threading import Thread
import time
import udp_support as udp
import numpy as np

class Node:
    def __init__(self, id, n_nodes, broadcast_type, arrival_rate, service_rate, start_time, may_crash, prob_k, n_rounds, nodes_to_channel):
        self.port = 9000 + id
        self.id = int(id)
        self.start_time = start_time
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        # Lazy RB
        self.correct = set(range(n_nodes))
        self.message_from = None
        # Eager RB and Eager PB
        self.delivered = None
        self.fan_out = None
        self.n_rounds = None
        self.nodes_to_channel = nodes_to_channel

        self.type = broadcast_type
        self.deliver = None
        if broadcast_type == "lazy_rb":
            self.deliver = self.lazy_rb_deliver
            self.message_from = deque(maxlen = 200)
        elif broadcast_type == "eager_rb":
            self.deliver = self.eager_rb_deliver
            self.delivered = deque(maxlen = 200)
        elif broadcast_type == "eager_prob":
            self.deliver = self.eager_probabilistic_deliver
            self.delivered = deque(maxlen = 200)
            self.fan_out = prob_k
            self.n_rounds = n_rounds
        
        self.receive_thread = Thread(target = udp.start_udp_server, daemon = True, args = [self])
        self.receive_thread.start()
        
        self.alive = True
        self.may_crash = may_crash
        if self.may_crash:
            self.crash_thread = Thread(target = self.crash, daemon = True)
            self.crash_thread.start()

        # Statistics about the node
        self.received_messages_total = 0
        self.unique_messages = 0
        self.broadcast_requests = 0
        self.avg_response_time = 0
        self.throughput = 0    # Number of messages sent in 1 second
        self.utilization = 0

    def broadcast(self, message):
        message_list = message.strip().split("_")
        sender_id = message_list[0]
        tag = message_list[1]

        if tag == "broadcast":
            content = message_list[2]
            print(f"[{round(time.time() - self.start_time,3)}][{tag.upper()}] Process {self.id} broadcasts message {content} with sender {sender_id}")

        for node in self.correct:
            if self.id <= node:
                channel_port = self.nodes_to_channel[(self.id, node)]
            else:
                channel_port = self.nodes_to_channel[(node, self.id)]
            
            udp.udp_send(channel_port, message)

        self.broadcast_requests += 1  # Update Stats


    def pick_targets(self):
        targets = []
        candidates = list(self.correct)
        candidates.remove(self.id)
        while len(targets) < self.fan_out:
            candidate = int(random.choice(candidates))
            if candidate not in targets:
                targets.append(candidate)
        return targets

    def gossip(self, message):
        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        tag = message_list[1]
        content = message_list[2]
        time_sent = message_list[3]
        current_round = int(message_list[4])

        targets = self.pick_targets()
        for n in targets:
            if self.id <= n:
                channel_port = self.nodes_to_channel[(self.id, n)]
            else:
                channel_port = self.nodes_to_channel[(n, self.id)]
            udp.udp_send(channel_port, message)
            print(f"[{round(time.time() - self.start_time,3)}][GOSSIP] Process {self.id} sends to process {n} message {content} with sender {sender_id} and round {current_round}")

    def prob_broadcast(self, message):
        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        tag = message_list[1]
        content = message_list[2]
        time_sent = message_list[3]
        current_round = int(message_list[4])

        if tag == "broadcast":
            content = message_list[2]
            print(f"[{round(time.time() - self.start_time,3)}][{tag.upper()}] Process {self.id} broadcasts message {content} with sender {sender_id}")

        self.delivered.append(message)
        print(f"[{round(time.time() - self.start_time,3)}][PROB_DELIVERY] Process {self.id} delivers message {content} with sender {sender_id}")  # Deliver to the application    
        self.eager_probabilistic_deliver(message)
        self.gossip(message)
        self.broadcast_requests += 1  # Update Stats

    def lazy_rb_deliver(self, message):
        self.process_data()

        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        tag = message_list[1]
        content = message_list[2]
        time_sent = float(message_list[3])
        time_to_deliver = time.time() - time_sent

        if self.avg_response_time == 0:
            self.avg_response_time = time_to_deliver
        else:
            self.avg_response_time = (self.avg_response_time + time_to_deliver) / 2

        if message not in self.message_from:
            print(f"[{round(time.time() - self.start_time,3)}][LRB_DELIVERY] Process {self.id} delivers message {content} with sender {sender_id}")  # Deliver to the application
            self.message_from.append(message)
            self.unique_messages += 1  # Update Stats

            if sender_id not in self.correct:
                self.broadcast(message)
        else:
            print(f"[{round(time.time() - self.start_time,3)}][NO DELIVERY] Process {self.id} already delivered message {content} with sender {sender_id}")

        # Update Stats
        self.received_messages_total += 1

    def eager_rb_deliver(self, message):
        self.process_data()

        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        content = message_list[2]
        time_sent = float(message_list[3])
        time_to_deliver = time.time() - time_sent

        if self.avg_response_time == 0:
            self.avg_response_time = time_to_deliver
        else:
            self.avg_response_time = (self.avg_response_time + time_to_deliver) / 2

        if message not in self.delivered:
            self.delivered.append(message)
            print(f"[{round(time.time() - self.start_time,3)}][ERB_DELIVERY] Process {self.id} delivers message {content} with sender {sender_id}")  # Deliver to the application    
            self.broadcast(message)

            self.unique_messages += 1  # Update Stats
        else:
            print(f"[{round(time.time() - self.start_time,3)}][NO DELIVERY] Process {self.id} already delivered message {content} with sender {sender_id}")
        
        # Update Stats
        self.received_messages_total += 1


    def eager_probabilistic_deliver(self, message):
        self.process_data()

        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        tag = message_list[1]
        content = message_list[2]
        time_sent = float(message_list[3])
        current_round = int(message_list[4])

        time_to_deliver = time.time() - time_sent

        if self.avg_response_time == 0:
            self.avg_response_time = time_to_deliver
        else:
            self.avg_response_time = (self.avg_response_time + time_to_deliver) / 2
        
        if message not in self.delivered:
            self.delivered.append(message)
            print(f"[{round(time.time() - self.start_time,3)}][PROB_DELIVERY] Process {self.id} delivers message {content} with sender {sender_id}")  # Deliver to the application    
            
            self.unique_messages += 1  # Update Stats

        if current_round > 1:
            current_round -= 1
            new_message = f"{sender_id}_{tag}_{content}_{time_sent}_{current_round}\n"
            self.gossip(new_message)

        # Update Stats
        self.received_messages_total += 1

    # Method corresponding to the Crash event in our algorithms.
    def receive_crash(self, id):
        if self.type == "lazy_rb":
            self.correct.remove(int(id))
            print(f"[{round(time.time() - self.start_time,3)}][CRASH] Process {self.id} detects crash of process {id}")
            for message in self.message_from:
                message_list = message.strip().split("_")
                sender_id = message_list[0]
                tag = message_list[1]
                content = message_list[2]
                if sender_id == id and tag != "crash":
                    self.broadcast(message)
    
    # Method to simulate a the crash of a process. The perfect failure detector is not directly implemented but simulated by the sending
    # of a crash message from the process that is crashing.
    def crash(self):
        if random.choice([True, False]):
            crash_time = np.random.exponential(30)                   # MTTF = 30 s
            print(f"Process {self.id} will crash in {crash_time} seconds...")
            time.sleep(crash_time)
            self.alive = False
            self.broadcast(f"{self.id}_crash_process_{time.time()}\n")
    
    def start_node(self):
        scale_beta = 1/self.arrival_rate
        time_instants = np.random.exponential(scale_beta, 100)

        for t in time_instants:
            time.sleep(t)
            if not self.alive:
                return
            # Message format: senderID_tag_content_time\n
            message = f"{self.id}_broadcast_{random.randint(1, 100)}_{time.time()}\n"

            if self.type == "eager_prob":
                rounds = self.n_rounds
                # Insert in the message the information about the number of rounds to perform
                message = f"{self.id}_broadcast_{random.randint(1, 100)}_{time.time()}_{rounds}\n"
                self.prob_broadcast(message)
            else:
                self.broadcast(message)

    # Method to simulate the processing of a single message accordin to an exponential distribution
    def process_data(self):
        scale_beta = 1/self.service_rate
        
        # It returns a sequence of values which can be assumed by a random variable following an exponential distribution.
        # The first parameter is the scale beta (the inverse of the rate lambda) and the second the size of the array of values to return.
        processing_time = np.random.exponential(scale_beta)
        time.sleep(processing_time)