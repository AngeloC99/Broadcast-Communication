import random
from collections import deque
import socketserver
from threading import Thread
import socket
import time
import numpy as np

tableDelay = {
    0: {0: 0, 1: 2, 2: 3, 3: 2, 4: 3, 5: 4, 6: 4},
    1: {0: 2, 1: 0, 2: 2, 3: 1, 4: 2, 5: 5, 6: 1},
    2: {0: 1, 1: 3, 2: 0, 3: 3, 4: 2, 5: 5, 6: 6},
    3: {0: 2, 1: 1, 2: 4, 3: 0, 4: 2, 5: 5, 6: 5},
    4: {0: 1, 1: 3, 2: 4, 3: 3, 4: 0, 5: 5, 6: 5},
    5: {0: 2, 1: 1, 2: 2, 3: 3, 4: 2, 5: 0, 6: 6},
    6: {0: 1, 1: 2, 2: 4, 3: 3, 4: 5, 5: 7, 6: 0}
}


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
        elif broadcast_type == "eager_probabilistic":
            self.deliver = self.eager_probabilistic_deliver
        self.correct = set(range(n_nodes))
        self.message_from = [deque(maxlen = 100)]
        self.receive_thread = Thread(target = start_udp_server, daemon = True, args = [self])
        self.receive_thread.start()
        #self.crash_thread = Thread(target = self.crash, daemon = True)
        #self.crash_thread.start()
        self.start_node()


    def broadcast(self, message):
        print(f"[{time.time() - self.start_time}][BROADCAST] Process{message.strip()}")
        for node in self.correct:
            udp_send(node, message)
        


    def beb_deliver(self, message):
        print(f"[BEB_DELIVERY] Process{self.id} delivers from process{message}")


    def lazy_rb_deliver(self, message):
        self.process_data()

        sender = int(message.split('_', 2)[0])
        #content = message.split(':', 2)[1]
        #if content not in self.message_from[sender]:
        if message not in self.message_from:
            print(f"[{time.time() - self.start_time}][LRB_DELIVERY] Process{self.id} delivers from process{message}")  # Deliver to the application
            #self.message_from[sender].append(message)
            self.message_from.append(message)
            #if sender not in self.correct:
            #    self.broadcast(message)
        else:
            print(f"[{time.time() - self.start_time}][NO DELIVERY] Process {self.id} already delivered from process{message}")

    def eager_probabilistic_deliver(self, message):
        pass

    # Method to simulate the processing of a single message accordin to an exponential distribution
    def process_data(self):
        scale_beta = 5
        
        # It returns a sequence of values which can be assumed by a random variable following an exponential distribution.
        # The first parameter is the scale beta (the inverse of the rate lambda) and the second the size of the array of values to return.
        processing_time = np.random.exponential(scale_beta)
        time.sleep(processing_time) 

    """
    def receive_crash(self, id):
        self.correct.remove(id)
        print(f"Process {self.id} detects crash of: {id}")
        for message in self.message_from[id]:
            self.broadcast(message)

    def crash(self):
        if random.choice([True, False]):
            t = random.randint(2, 60)
            print(f"Node {self.id} will crash in {t} seconds...")
            time.sleep(t)
            self.alive = False
            self.broadcast(f"{self.id}_crash:crash\n")
    """
    
    def start_node(self):
        scale_beta = 5
        time_instants = np.random.exponential(scale_beta, 20)

        for t in time_instants:
            time.sleep(t)
            if not self.alive:
                return
            message = f"{self.id}_message:{random.randint(1, 100)}\n"
            self.broadcast(message)
            


def start_udp_server(node: Node):
    with socketserver.UDPServer(('localhost', node.port), UdpReceiver) as server:
        try:
            server.node = node
            server.serve_forever()
        except:
            server.shutdown()


class UdpReceiver(socketserver.DatagramRequestHandler):
    def handle(self):
        raw_message = self.rfile.readline().strip().decode('utf-8')
        sender = int(raw_message.split('_', 2)[0])
        content = raw_message.split(':', 2)[1]
        tag = raw_message.split('_', 2)[1].split(':')[0]

        if not self.server.node.alive:
            self.server.shutdown()
            return

        if tag == "crash":
            self.server.node.receive_crash(sender)
            return
        else:
            self.server.node.deliver(raw_message)


def udp_send(receiver_id, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_id = int(message.split('_', 2)[0])
    time.sleep(tableDelay[sender_id][receiver_id])
    sock.sendto(message.encode('utf-8'), ('localhost', 9000 + receiver_id))
    sock.close()
