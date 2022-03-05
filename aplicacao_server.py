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


class Server:
    def __init__(self,serialname):
        self.port = serialname
        self.com1 = enlace(self.port)
        self.lastPack = 0
        self.datagrams = []
        self.bytes = b''
        self.com1.enable()
        

    def nextPack(self):
        self.lastPack+=1

    def handShake(self):
        while True:
            try:
                print("Esperando 1 byte de sacrifício...\n")        
                rxBuffer, nRx = self.com1.getData(1)
                self.com1.rx.clearBuffer()
                print("Recebido...")
                time.sleep(.1)

                self.handshake = handshake.Handshake("server").buildHandshake()
                print("Esperando Handshake do Client...")
                clientHandshake, nRx = self.com1.getData(14) #tamanho fixo do handshake
                if clientHandshake == handshake.Handshake("client").buildHandshake():
                    print("\nHandshake recebido...")
                    self.com1.sendData(self.handshake)
                    print("\nIniciando Transmissão")
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

    def receiveFile(self):
        if self.handShake()==True:
            while True:
                try:
                    print(f"Recebendo pacote n°{self.lastPack+1}...")
                    head, sizeHead = self.com1.getData(10)
                    if head[6]==self.lastPack:
                        payload,sizepayload = self.com1.getData(head[7])
                        if sizepayload==head[7]:
                            eop,sizeeop = self.com1.getData(4)
                            if head[5]==self.lastPack+1:
                                print("Último Pacote recebido com sucesso\n")
                                self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("ok"))
                                self.bytes+=payload
                                print("Encerrando Comunicação...\n")
                                self.mountFile()
                                self.com1.disable()
                                break
                            elif eop == datagram.Datagram().EOP:
                                print("Pacote recebido com sucesso, mande o próximo...\n")
                                self.nextPack()
                                self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("ok"))
                                time.sleep(0.5)
                                self.bytes+=payload
                                
        
                            else:
                                print("Recebi algo estranho...")
                                print("Por favor reenvie")
                                self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("erro"))
                                continue
                        else:
                            print("Recebi arquivo com tamanho diferente...")
                            print(f"Tamanho esperado: {head[7]} bytes")
                            print(f"Tamanho recebido: {sizepayload} bytes")
                            print("Por favor reenvie...")
                            self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("erro"))
                            time.sleep(.5)
                            continue
                    else:
                        print("Recebi um pacote diferente...")
                        print(f"Pacote recebido: {head[6]}")
                        print(f"Pacote esperado: {self.lastPack}")
                        print("Por favor reenvie\n")
                        self.com1.sendData(packagetool.Acknowledge().buildAcknowledge("erro"))
                        continue
                                
                        
                except KeyboardInterrupt:
                    print("Interrupção Forçada")
                    self.com1.disable()
                    break
                except Exception as erro:
                    print(erro)
                    self.com1.disable()
                    break
                
    def mountFile(self):
        print("Salvando dados no arquivo")
        f = open("recebida.png",'wb')
        f.write(self.bytes)
        f.close()


    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    s = Server(serialName)
    s.receiveFile()
