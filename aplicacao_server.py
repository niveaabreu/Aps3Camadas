#!/usr/bin/env python3
#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################

#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 


from server.enlace import *
import time
import numpy as np
import sys
import operations.datagram as datagram
import operations.handshake as handshake
import operations.packagetool as packagetool

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python3 -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/tty"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM5"                  # Windows(variacao de)

jsonfile = "./files/recebido.json"
pngfile = "./files/recebido.png"

file = pngfile
class Server:
    def __init__(self,serialname):
        self.port = serialname
        self.com1 = enlace(self.port)
        self.currentPack = 0
        self.datagrams = []
        self.bytes = b''
        self.head = b''
        self.sizeHead = 0
        self.com1.enable()
        

    def nextPack(self):
        """Método de incrementação do pack a ser enviado"""
        self.currentPack+=1

    def readHead(self):
        """Método que realiza leitura do head do pacote recebido"""
        self.head,self.sizeHead = self.com1.getData(10)

    def readPayload(self):
        """Método que realiza leitura do payload do pacote recebido"""
        self.payload,self.sizepayload = self.com1.getData(self.head[7])

    def readEOP(self):
        """Método que realiza leitura do EOP do pacote recebido"""
        self.eop,sizeeop = self.com1.getData(4)

    def handShake(self):
        """Método de asserção do handshake, garantindo previamente a comunicação
        entre client e server"""
        while True:
            try:
                print("Esperando 1 byte de sacrifício...\n")        
                rxBuffer, nRx = self.com1.getData(1)
                self.com1.rx.clearBuffer()
                print("Recebido...")

                self.handshake = handshake.Handshake("server").buildHandshake()
                print("\nEsperando Handshake do Client...")
                clientHandshake, nRx = self.com1.getData(14) #tamanho fixo do handshake
                if clientHandshake == handshake.Handshake("client").buildHandshake():
                    print("\nHandshake recebido...")
                    self.com1.sendData(self.handshake)
                    time.sleep(0.1)
                    print("\n--------------------------")
                    print("Iniciando Transmissão")
                    print("--------------------------")
                    return True
                    
                else:
                    print("Recebi algo estranho...")
                    self.com1.disable()
                    return False   

            except KeyboardInterrupt:
                    print("Interrupção Forçada")
                    self.com1.disable()
                    break

            except Exception as erro:
                print(erro)
                self.com1.disable()
                break   

    def sendAcknowledge(self,status):
        """Método de envio da mensagem de Acknowledge, confirmando se o pacote foi bem recebido
        ou solicitando um possível reenvio"""
        if status=="sucesso":
            print("Pacote recebido com sucesso, mande o próximo...\n")
            self.nextPack()
            self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("ok"))
            time.sleep(0.1)
        elif status=="ultimo":
            print("Último Pacote recebido com sucesso\n")
            self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("ok"))
            time.sleep(0.8)
        elif status=="sizeError":
            print("\n------------------------------------------------------------")
            print("Recebi arquivo com tamanho diferente...")
            print(f"Recebi algo maior que os {self.sizepayload} bytes esperados...")
            print("Por favor reenvie...")
            print("------------------------------------------------------------\n")
            self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("erro"))
            self.com1.rx.clearBuffer()
            time.sleep(3)
        elif status=="packError":
            print("\n---------------------------------------")
            print("Recebi um pacote diferente...")
            print(f"Pacote recebido: {self.head[6]}")
            print(f"Pacote esperado: {self.currentPack+1}")
            print("Por favor reenvie")
            print("---------------------------------------\n")
            self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("erro"))
            self.com1.rx.clearBuffer()
            time.sleep(3)

    def check_current_Pack_is_Right(self):
        """Método verificação se o pacote informado no head corresponde ao esperado"""
        if self.head[6]==self.currentPack:
            return True
        return False

    def check_EOP_in_right_place(self):
        """Método de verificação da posição do EOP"""
        if self.eop == datagram.Datagram().EOP:
            return True
        return False

    def check_if_is_the_last_pack(self):
        """Método de verificação se é o último pacote a ser receber"""
        if self.head[5]==self.currentPack+1:
            return True
        return False

    def mountFile(self):
        """Método de montagem dos bytes para formação do arquivo"""
        print("Salvando dados no arquivo")
        f = open(file,'wb')
        f.write(self.bytes)
        f.close()

    def receiveFile(self):
        """Método main. Utiliza todos os métodos acima de maneira a cumprir o propósito do
        projeto"""
        if self.handShake()==True:
            while True:
                try:
                    print(f"Recebendo pacote n°{self.currentPack+1}...")
                    self.readHead()
                    if self.check_current_Pack_is_Right():
                        self.readPayload()
                        self.readEOP()
                        if self.check_if_is_the_last_pack():
                            if self.check_EOP_in_right_place():
                                self.sendAcknowledge("ultimo")
                                self.bytes+=self.payload
                                print("Encerrando Comunicação...\n")
                                self.mountFile()
                                self.com1.disable()
                                break
                        elif self.check_EOP_in_right_place():
                            self.sendAcknowledge("sucesso")
                            self.bytes+=self.payload
                        else:
                            self.sendAcknowledge("sizeError")
                            continue
                    else:
                        self.sendAcknowledge("packError")
                        continue
                                
                except KeyboardInterrupt:
                    print("Interrupção Forçada")
                    self.com1.disable()
                    break
                except Exception as erro:
                    print(erro)
                    self.com1.disable()
                    break
                
#So roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    s = Server(serialName)
    s.receiveFile()
