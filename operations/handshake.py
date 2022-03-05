from operations.datagram import Datagram

class Handshake:
    def __init__(self, origem):
        self.origem = origem
        self.datagram = Datagram()

    def buildHandshake(self):
        "Constroi o handshake para envio"
        if self.origem=="client":
            self.datagram.head(0,0,1)
        elif self.origem=="server":
            self.datagram.head(1,1,0)
        return self.datagram.datagram()

# m=Handshake("client").buildHandshake()
# print(m)