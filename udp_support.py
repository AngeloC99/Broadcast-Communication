import socketserver
import socket

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

        # To understand if the component is a Node or a Channel
        if hasattr(self.server.component,"id"):
            if not self.server.component.alive:
                self.server.shutdown()
                return

            if tag == "crash":
                self.server.component.receive_crash(sender_id)
                return
            else:
                self.server.component.deliver(raw_message)
        else:
            self.server.component.deliver(raw_message)

def udp_send(receiver_port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(message.encode('utf-8'), ('localhost', receiver_port))
    sock.close()