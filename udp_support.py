import socketserver
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

def start_udp_server(component):
    with socketserver.UDPServer(('localhost', component.port), UdpReceiver) as server:
        try:
            server.component = component
            server.serve_forever()
        except:
            server.shutdown()


class UdpReceiver(socketserver.DatagramRequestHandler):
    def handle(self):
        raw_message = self.rfile.readline().strip().decode('utf-8')
        
        message_list = raw_message.split("_")
        sender_id = message_list[0]
        tag = message_list[1]
        content = message_list[2]

        #if not self.server.node.alive:
        #    self.server.shutdown()
        #    return

        if tag == "crash":
            self.server.component.receive_crash(sender_id)
            return
        else:
            self.server.component.deliver(raw_message)


def udp_send(receiver_id, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_list = message.split("_")
    sender_id = int(message_list[0])
    tag = message_list[1]
    content = message_list[2]

    time.sleep(tableDelay[sender_id][receiver_id])
    sock.sendto(message.encode('utf-8'), ('localhost', 9000 + receiver_id))
    sock.close()