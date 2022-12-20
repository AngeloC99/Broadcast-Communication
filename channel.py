from collections import deque
import udp_support as udp
from threading import Thread
import time
import numpy as np

class Channel:
    def __init__(self, port, node1, node2, bandwidth):
        self.port = port
        self.node1 = int(node1)
        self.node2 = int(node2)
        self.port1 = 9000 + self.node1
        self.port2 = 9000 + self.node2
        self.bandwidth = bandwidth
        self.deliver = self.receive
        self.messages_in = deque(maxlen = 200)
        
        # Statistics about the node
        self.avg_response_time = 0
        self.throughput = 0    # Number of messages sent in 1 second
        self.utilization = 0

    def forward(self, message):
        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        
        start_t = time.time()
        if sender_id == self.node1:
            udp.udp_send(self.port2, message)
        else:
            udp.udp_send(self.port1, message)
        sending_time = time.time() - start_t
        if self.throughput == 0:
            self.throughput = 1 / sending_time
            self.utilization = (1/self.bandwidth)*(self.throughput)
        else:
            self.throughput = (self.throughput + (1 / sending_time)) / 2
            self.utilization = (self.utilization + (1/self.bandwidth)*(self.throughput)) / 2

    def receive(self, message):
        self.process_data()
        self.messages_in.append(message)

        message_list = message.strip().split("_")
        time_sent = float(message_list[3])
        time_to_deliver = time.time() - time_sent
        if self.avg_response_time == 0:
            self.avg_response_time = time_to_deliver
        else:
            self.avg_response_time = (self.avg_response_time + time_to_deliver) / 2
        
        self.forward(message)

    # Method to simulate the processing of a single message accordin to an exponential distribution
    def process_data(self):
        scale_beta = 1/self.bandwidth
        
        # It returns a sequence of values which can be assumed by a random variable following an exponential distribution.
        # The first parameter is the scale beta (the inverse of the rate lambda) and the second the size of the array of values to return.
        processing_time = np.random.exponential(scale_beta)
        time.sleep(processing_time)
