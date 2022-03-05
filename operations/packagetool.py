from operations.datagram import Datagram
class Packagetool:
    def __init__(self,filepath):
        self.filepath = filepath
        self.bytearray = b''
        self.totalSize = 0
        self.numberOfPayloads = 0
        self.lastPayloadsize = 0
        self.datagram = Datagram()
        self.payloads = []
        self.datagrams = []

    def buildPayloads(self):
        """Constroi lista fracionada do arquivo a ser enviado pelos pacotes de acordo
        com o tamanho máximo de cada payload"""
        with open(self.filepath,"rb") as bytearray:
            bytearray = bytearray.read()
            self.bytearray = bytearray
        self.totalSize = len(self.bytearray)

        if self.totalSize%114 ==0:
            self.numberOfPayloads = int(self.totalSize/114)
        else:
            self.numberOfPayloads = int(self.totalSize/114)+1
            self.lastPayloadsize = self.totalSize - int(self.totalSize/114)*114

        self.fracionatePayloads()

    def fracionatePayloads(self):
        """Função auxiliar para fracionar os bytes de um arquivo na quantidade de pacotes
        desejados ao envio"""
        for i in range(0,self.numberOfPayloads):
            self.payloads.append(self.bytearray[114*i:114*(i+1)])
    
    def buildDatagrams(self):
        """Função que monta os envios de datagramas em vários pacotes do arquivo enviado"""
        self.buildPayloads()
        for i in range(0,self.numberOfPayloads):
            self.datagram.payload(self.payloads[i])
            self.datagram.head(2,0,1,self.totalSize,self.numberOfPayloads)
            pack = self.datagram.datagram()
            self.datagrams.append(pack)
            self.datagram.nextPackage()
        return self.datagrams

class Acknowledge:
    def __init__(self):
        self.datagram = Datagram()

    def buildAcknowledge(self,condition):
        "Constroi o acknowledge para envio"
        if condition=="ok":
            self.datagram.bytesNotIntegrity()
            self.datagram.head(3,1,0)
        elif condition=="erro":
            self.datagram.bytesNotIntegrity(True)
            self.datagram.head(3,1,0)
        return self.datagram.datagram()

# image = "operations/image.png"
# x = Packagetool(image)
# print(list(x.buildDatagrams()))





        

        
        



