import random
from collections import deque
from threading import Thread
import time
import udp_support as udp
import numpy as np

class Node:
    def __init__(self, id, n_nodes, broadcast_type, start_time):
        self.port = 9000 + id
        self.id = id
        self.type = broadcast_type
        self.start_time = start_time
        # In case of eager_rb
        self.delivered = deque(maxlen = 200)
        self.alive = True
        self.deliver = None
        if broadcast_type == "beb":
            self.deliver = self.beb_deliver
        elif broadcast_type == "lazy_rb":
            self.deliver = self.lazy_rb_deliver
        elif broadcast_type == "eager_rb":
            self.deliver = self.lazy_rb_deliver
        elif broadcast_type == "eager_prob":
            self.deliver = self.eager_probabilistic_deliver
        self.correct = set(range(n_nodes))
        self.message_from = deque(maxlen = 200)
        self.receive_thread = Thread(target = udp.start_udp_server, daemon = True, args = [self])
        self.receive_thread.start()
        self.crash_thread = Thread(target = self.crash, daemon = True)
        self.crash_thread.start()
        self.start_node()

    def broadcast(self, message):
        message_list = message.strip().split("_")
        sender_id = message_list[0]
        tag = message_list[1]

        if tag == "broadcast":
            content = message_list[2]
            print(f"[{time.time() - self.start_time}][{tag.upper()}] Process {self.id} broadcasts message {content} with sender {sender_id}")
        
        for node in self.correct:
            list_nodes = list()
            list_nodes.append(self.id)
            list_nodes.append(node)
            list_nodes.sort()
            if self.id <= node:
                channel_port = 9050 + int(f"{self.id}" + f"{node}")
            else:
                channel_port = 9050 + int(f"{node}" + f"{self.id}")
            
            udp.udp_send(channel_port, message)

    def beb_deliver(self, message):
        print(f"[BEB_DELIVERY] Process{self.id} delivers from process{message}")

    def lazy_rb_deliver(self, message):
        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        tag = message_list[1]
        content = message_list[2]
        time_sent = message_list[3]

        if message not in self.message_from:
            print(f"[{time.time() - self.start_time}][LRB_DELIVERY] Process {self.id} delivers message {content} with sender {sender_id}")  # Deliver to the application
            self.message_from.append(message)
            if sender_id not in self.correct:
                self.broadcast(message)
        else:
            print(f"[{time.time() - self.start_time}][NO DELIVERY] Process {self.id} already delivered message {content} with sender {sender_id}")

    def eager_rb_deliver(self, message):
        pass

    def eager_probabilistic_deliver(self, message):
        pass
    
    # Method corresponding to the Crash event in our algorithms.
    def receive_crash(self, id):
        self.correct.remove(int(id))
        print(f"[{time.time() - self.start_time}][CRASH] Process {self.id} detects crash of process {id}")
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
            crash_time = np.random.normal(5,2)
            print(f"Process {self.id} will crash in {crash_time} seconds...")
            time.sleep(crash_time)
            self.alive = False
            
            self.broadcast(f"{self.id}_crash\n")
    
    def start_node(self):
        scale_beta = 5
        time_instants = np.random.exponential(scale_beta, 20)

        for t in time_instants:
            time.sleep(t)
            if not self.alive:
                return
            # Message format: senderID_tag_content_time\n
            message = f"{self.id}_broadcast_{random.randint(1, 100)}_{time.time()}\n"
            self.broadcast(message)


