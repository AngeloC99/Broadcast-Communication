import socketserver
import socket
import time

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

        if tag == "crash":                    # MODIFY IF CRASH HANDLED DIFFERENTLYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
            self.server.component.receive_crash(sender_id)
            return
        else:
            self.server.component.deliver(raw_message)


def udp_send(receiver_port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message_list = message.split("_")
    sender_id = int(message_list[0])
    tag = message_list[1]
    content = message_list[2]

    #time.sleep(tableDelay[sender_id][receiver_id])
    sock.sendto(message.encode('utf-8'), ('localhost', receiver_port))
    sock.close()