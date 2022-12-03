import random
from collections import deque
import socketserver
from threading import Thread
import socket
import time


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
    def __init__(self, id, n_nodes, broadcast_type):
        self.port = 9000 + id
        self.id = id
        self.type = broadcast_type
        self.deliver = None
        self.alive = True
        if broadcast_type == "beb":
            self.deliver = self.beb_deliver
        elif broadcast_type == "lazy_rb":
            self.deliver = self.lazy_rb_deliver
        elif broadcast_type == "eager_probabilistic":
            self.deliver = self.eager_probabilistic_deliver
        self.correct = set(range(n_nodes))
        self.message_from = [deque(maxlen = 4) for _ in range(n_nodes)]  # riceve al massimo 4 messaggi e sostituisce i piÃ¹ vecchi quando piena
        self.receive_thread = Thread(target = start_udp_server, daemon = True, args = [self])
        self.receive_thread.start()
        self.crash_thread = Thread(target = self.crash, daemon = True)
        self.crash_thread.start()
        self.start_node()


    def broadcast(self, message):
        correct_copy = set(self.correct)
        for node in correct_copy:
            udp_send(node, message)
            print(f"Process {self.id} sends in broadcast {message}")


    def beb_deliver(self, message):
        print(f"Deliver message: {message}")


    def lazy_rb_deliver(self, message):
        sender = int(message.split('_', 2)[0])
        content = message.split(':', 2)[1]
        if content not in self.message_from[sender]:
            print(f"Process {self.id} delivers message: {message}")  # Deliver to the application
            self.message_from[sender].append(message)
            if sender not in self.correct:
                self.broadcast(message)


    def eager_probabilistic_deliver(self, message):
        pass


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


    def start_node(self):
        inter_arrival_t = random.randint(5, 10)
        while True:
            if not self.alive:
                return
            message = f"{self.id}_message:{random.randint(1, 50)}\n"
            self.broadcast(message)
            time.sleep(inter_arrival_t)


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
