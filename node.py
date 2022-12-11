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
        self.deliver = None
        self.start_time = start_time
        self.alive = True
        if broadcast_type == "beb":
            self.deliver = self.beb_deliver
        elif broadcast_type == "lazy_rb":
            self.deliver = self.lazy_rb_deliver
        elif broadcast_type == "eager_rb":
            self.deliver = self.lazy_rb_deliver
        elif broadcast_type == "eager_prob":
            self.deliver = self.eager_probabilistic_deliver
        self.correct = set(range(n_nodes))
        self.message_from = [deque(maxlen = 100)]
        self.receive_thread = Thread(target = udp.start_udp_server, daemon = True, args = [self])
        self.receive_thread.start()
        #self.crash_thread = Thread(target = self.crash, daemon = True)
        #self.crash_thread.start()
        self.start_node()

    def broadcast(self, message):
        message_list = message.strip().split("_")
        sender_id = message_list[0]
        tag = message_list[1]
        content = message_list[2]
        print(f"[{time.time() - self.start_time}][{tag.upper()}] Process {sender_id} broadcasts message {content}")
        for node in self.correct:
            udp.udp_send(9050 + self.id + node, message)

    def beb_deliver(self, message):
        print(f"[BEB_DELIVERY] Process{self.id} delivers from process{message}")

    def lazy_rb_deliver(self, message):
        message_list = message.strip().split("_")
        sender_id = message_list[0]
        tag = message_list[1]
        content = message_list[2]

        if message not in self.message_from:
            print(f"[{time.time() - self.start_time}][LRB_DELIVERY] Process {self.id} delivers message {content} from process {sender_id}")  # Deliver to the application
            self.message_from.append(message)
            if sender_id not in self.correct:
                self.broadcast(message)
        else:
            print(f"[{time.time() - self.start_time}][NO DELIVERY] Process {self.id} already delivered message {content} from process {sender_id}")

    """
    def receive_crash(self, id):
        self.correct.remove(id)
        print(f"Process {self.id} detects crash of: {id}")
        for message in self.message_from:
            message_list = message.strip().split("_")
            sender_id = message_list[0]
            tag = message_list[1]
            content = message_list[2]
            if sender_id == id:
                self.broadcast(message)
    """


    def eager_rb_deliver(self, message):
        pass

    def eager_probabilistic_deliver(self, message):
        pass
    
    def start_node(self):
        scale_beta = 5
        time_instants = np.random.exponential(scale_beta, 20)

        for t in time_instants:
            time.sleep(t)
            if not self.alive:
                return
            # Message format: senderID_tag_content\n
            message = f"{self.id}_broadcast_{random.randint(1, 100)}\n"
            self.broadcast(message)
            
    """
    def crash(self):
        if random.choice([True, False]):
            crash_time = np.random.normal(50,20)    
            t = random.randint(2, 60)
            print(f"Node {self.id} will crash in {crash_time} seconds...")
            time.sleep(crash_time)
            self.alive = False
            
            self.broadcast(f"{self.id}_crash\n")
    """


