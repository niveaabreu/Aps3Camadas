class Datagram:
    def __init__(self):
        self.HEAD  = b''
        self.PAYLOAD = b''
        self.EOP = 0X10120327.to_bytes(4,byteorder="big") #digitos iniciais do numero de ouro
        self.currentPack = 0
        self.dataSize  =  0
        self.integrity = 1
        self.overhead = 0X01.to_bytes(1,byteorder="big")
        self.remainingSize = 0X00.to_bytes(1,byteorder="big")

    def head(self,tipo,origem,destino,totalSize=0,numberOfPackages=0):
        """
        Recebe inteiro, devolve em byte
        header:
        0-tipo [0:Handshake,1:Resposta Handshake,2:Envio de comandos,3:Acknowledge],
        1-origem [0:Client, 1:Server],
        2-destino [0:Server, 1:Client],
        3-tamanho total do arquivo [quantidade de bytes que serão fracionados em n pacotes],
        4-tamanho total do arquivo [quantidade de bytes que serão fracionados em n pacotes],
        5-pacotes a serem enviados [número n],
        6-numero do pacote atual [entre 0 e n-1, dado n pacotes],
        7-quantidade de bytes no payload atual [entre 0 e 114],
        8-integridade do pacote [1:OK,0:solicita reenvio]
        9-porcentagem de bytes que faltam para a imagem (complementar do tamanho total)
        """
        self.tipo  = tipo.to_bytes(1,byteorder="big")
        self.origem =  origem.to_bytes(1,byteorder="big")
        self.destino = destino .to_bytes(1,byteorder="big")
        self.totalSize = totalSize.to_bytes(2,byteorder="big")
        self.numberOfPackages = numberOfPackages.to_bytes(1,byteorder="big")
        currentPack = self.currentPack.to_bytes(1,byteorder="big")
        datasize = self.dataSize.to_bytes(1,byteorder="big")
        integrity = self.integrity.to_bytes(1,byteorder="big")
        if totalSize!=0:
            self.remainingSize = int((100*(totalSize -  self.dataSize*self.currentPack)/totalSize)).to_bytes(1,byteorder="big")

        self.HEAD = self.tipo+self.origem+self.destino+self.totalSize+self.numberOfPackages+currentPack+datasize+integrity+self.remainingSize

    def payload(self, payload):
        """Método de definição do payload em um pacote"""
        self.PAYLOAD = payload
        self.dataSize = len(payload)

    def nextPackage(self):
        """Método de incrementação no pacote atual a ser enviado"""
        self.currentPack+=1

    def bytesAreIntegrity(self,bool=True):
        """Método de verificação da integridade dos dados"""
        if not bool:
            self.integrity=0
        else:
            self.integrity=1    

    def datagram(self):
        """Método de criação do datagrama conforme especificado"""
        finalDatagram = self.HEAD+self.PAYLOAD+self.EOP
        try:
            assert len(finalDatagram)<=128
            return finalDatagram
        except:
            print("Tamanho acima do esperado")
            return b''
         
    
