#!/usr/bin/env python3
#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################

import json
from sys import argv


from client.enlace import *
import time
import numpy as np
import operations.datagram as datagram
import operations.handshake as handshake
import operations.packagetool as packagetool

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python3 -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/tty0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)

jsonfile = "./files/notes.json"
pngfile = "./files/image.png"

file = pngfile
  
class Client:
    def __init__(self,serialname,filepath):
        self.port = serialname
        self.com1 = enlace(self.port)
        self.filepath = filepath
        self.currentPack = 0
        self.datagrams = []
        self.acknowledge = packagetool.Acknowledge().buildAcknowledge("ok")
        self.caso = int(input("""Qual o caso deseja simular?
        1 - Caso de Sucesso de Transmissão ou TIMEOUT
        2 - Caso de erro de pacote
        3 - Caso de erro de tamanho do payload\n """))
        self.com1.enable()

    def nextPack(self):
        """Método de incrementação do pack a ser enviado"""
        self.currentPack+=1

    def buildDatagrams(self):
        """Método de construção dos datagramas ao receber o caminho do arquivo a ser 
        transmitido"""
        datagramsConstructor = packagetool.Packagetool(self.filepath)
        self.datagrams = datagramsConstructor.buildDatagrams()

    def handShake(self):
        """Método de asserção do handshake, garantindo previamente a comunicação
        entre client e server"""
        while True:
            try:
                time.sleep(.2)
                print("Enviando byte de sacríficio...")
                self.com1.sendData(b'00')
                time.sleep(1) 

                self.handshake = handshake.Handshake("client").buildHandshake()
                print("\nEnviando Handshake para Server...")
                self.com1.sendData(self.handshake)
                time.sleep(.1)
                serverHandshake, nRx = self.com1.getData(14) #tamanho fixo do handshake
                if serverHandshake == handshake.Handshake("server").buildHandshake():
                    print("\nHandshake recebido...")
                    print("\n--------------------------")
                    print("Iniciando Transmissão")
                    print("--------------------------")
                    return True
                elif serverHandshake==[-1]:
                    answer = input("\nServidor inativo. Tentar novamente? S/N ")
                    if answer.lower()=="s":
                        continue
                    else:
                        print("Encerrando comunicação...")
                        self.com1.disable()
                        break
                else:
                    print("Recebi algo estranho...")
                    break

            except KeyboardInterrupt:
                    print("Interrupção Forçada")
                    self.com1.disable()
                    break
            except Exception as erro:
                print(erro)
                self.com1.disable()
                break
        
    def casoErroPacote(self):
        """Método que implementa o caso de envio errado de um número de pacote no head
        ao esperado pelo server (em termos de sucessividade)"""
        acknowledge, sizeAck = self.com1.getData(14)
        if acknowledge == packagetool.Acknowledge().buildAcknowledge("ok"):
            print("Acknowledge recebido! Autorizado envio do próximo pacote!                      ")
            print(f"Enviando Pacote n°{self.currentPack+1}...             \n")
            self.com1.sendData(self.datagrams[self.currentPack+2])
            time.sleep(.8)
            self.nextPack()

    def casoErroPayload(self):
        """Método que implementa o caso de envio incorreto do tamanho do payload
        informado no head em relação ao trnasmitido no pacote"""
        acknowledge, sizeAck = self.com1.getData(14)
        if acknowledge == packagetool.Acknowledge().buildAcknowledge("ok"):
            print("Acknowledge recebido! Autorizado envio do próximo pacote!                      ")
            print(f"Enviando Pacote n°{self.currentPack+1}...                               \n")
            lista = list(self.datagrams[self.currentPack])
            lista[7]=36
            lista = bytes(lista)
            self.com1.sendData(lista)
            time.sleep(.8)
            self.nextPack()
    
    def sendCurrentpack(self):
        """Método de envio do pacote atual"""
        print("Acknowledge recebido! Autorizado envio do próximo pacote!                      ")
        print(f"Enviando Pacote n°{self.currentPack+1}...                               \n")
        self.com1.sendData(self.datagrams[self.currentPack])
        time.sleep(.1)
        #self.com1.rx.clearBuffer()
        self.nextPack()

    def sendPackaagain(self):
        """Método de reenvio do pacote alertado como enviado incorretamente ao
        servidor"""
        print("-------------------------------------------------------------------------")
        print(f"Ocorreu algum erro durante a transmissão do pacote nº {self.currentPack}...")
        print("Reenviando ao server...")
        print("--------------------------------------------------------------------------\n")
        self.com1.sendData(self.datagrams[self.currentPack-1])
        time.sleep(3)

    def sendFile(self):
        """Método main. Utiliza todos os métodos acima de maneira a cumprir o propósito do
        projeto"""
        if self.handShake()==True:
            self.buildDatagrams()
            print(f"Estaremos enviando {len(self.datagrams)} pacotes...")
            time.sleep(2)
            while True:
                try:
                    if self.currentPack==0:
                        self.sendCurrentpack()
                    elif self.caso==2 and (self.currentPack==3 or self.currentPack==7):
                        self.casoErroPacote()
                        
                    elif self.caso==3 and self.currentPack==4:
                        self.casoErroPayload()
                        
                    elif self.currentPack==len(self.datagrams):
                        print("Último pacote enviado\n")
                        print("Encerrando comunicação...")
                        self.com1.disable()
                        break

                    else:
                        acknowledge, sizeAck = self.com1.getData(14)
                        if acknowledge == packagetool.Acknowledge().buildAcknowledge("ok"):
                            self.sendCurrentpack()
                        elif acknowledge == packagetool.Acknowledge().buildAcknowledge("erro"):
                            self.sendPackaagain()
                        else:
                            print("Ocorreu um erro bastante estranho...")
                            print("Encerrando comunicação")
                            self.com1.disable()
                            break
                except KeyboardInterrupt:
                    print("Interrupção Forçada")
                    self.com1.disable()
                    break
                except Exception as erro:
                    print(erro)
                    self.com1.disable()
                    break

        
    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    c = Client(serialName,file)
    c.sendFile()
