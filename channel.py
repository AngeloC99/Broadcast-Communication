from collections import deque
import udp_support as udp
from threading import Thread
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
        

    def forward(self, message):
        message_list = message.strip().split("_")
        sender_id = int(message_list[0])
        
        if sender_id == self.node1:
            #time.sleep(tableDelay[sender_id][self.node2])
            udp.udp_send(self.port2, message)
        else:
            #time.sleep(tableDelay[sender_id][self.node1])
            udp.udp_send(self.port1, message)

    def receive(self, message):
        #print(f"channel {self.port} receives {message}")
        self.messages_in.append(message)
        self.process_data()
        self.forward(message)

    # Method to simulate the processing of a single message accordin to an exponential distribution
    def process_data(self):
        scale_beta = 5
        
        # It returns a sequence of values which can be assumed by a random variable following an exponential distribution.
        # The first parameter is the scale beta (the inverse of the rate lambda) and the second the size of the array of values to return.
        processing_time = np.random.exponential(scale_beta)
        time.sleep(processing_time)
