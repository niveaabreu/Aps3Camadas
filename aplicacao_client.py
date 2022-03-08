#!/usr/bin/env python3
#####################################################
# Camada Física da Computação
#Carareto
#11/08/2020
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código! 

from client.enlace import *
import time
import numpy as np
import sys
import random
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
  
class Client:
    def __init__(self,serialname,filepath):
        self.port = serialname
        self.com1 = enlace(self.port)
        self.filepath = filepath
        self.lastPack = 0
        self.datagrams = []
        self.acknowledge = packagetool.Acknowledge().buildAcknowledge("ok")
        self.caso = int(input("""Qual o caso deseja simular?
        1 - Caso de Sucesso de Transmissão ou TIMEOUT
        2 - Caso de erro de pacote
        3 - Caso de erro de tamanho do payload\n """))
        self.com1.enable()

    def nextPack(self):
        self.lastPack+=1

    def buildDatagrams(self):
        datagramsConstructor = packagetool.Packagetool(self.filepath)
        self.datagrams = datagramsConstructor.buildDatagrams()

    def handShake(self):
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
    
    def sentFile(self):
        if self.handShake()==True:
            self.buildDatagrams()
            print(f"Estaremos enviando {len(self.datagrams)} pacotes...")
            time.sleep(2)
            while True:
                try:
                    if self.lastPack==0:
                        print(f"Enviando Pacote n°{self.lastPack+1}...                                 \n")
                        self.com1.sendData(self.datagrams[self.lastPack])
                        time.sleep(.1)
                        self.nextPack()

                    if self.caso==2 and (self.lastPack==27 or self.lastPack==37):
                        acknowledge, sizeAck = self.com1.getData(14)
                        if acknowledge == packagetool.Acknowledge().buildAcknowledge("ok"):
                            print("Acknowledge recebido! Autorizado envio do próximo pacote!                      ")
                            print(f"Enviando Pacote n°{self.lastPack+1}...             \n")
                            self.com1.sendData(self.datagrams[2])
                            time.sleep(.8)
                            self.nextPack()
                            #self.caso=1
                        
                    elif self.caso==3 and self.lastPack==37:
                        acknowledge, sizeAck = self.com1.getData(14)
                        if acknowledge == packagetool.Acknowledge().buildAcknowledge("ok"):
                            print("Acknowledge recebido! Autorizado envio do próximo pacote!                      ")
                            print(f"Enviando Pacote n°{self.lastPack+1}...                               \n")
                            lista = list(self.datagrams[self.lastPack])
                            lista[7]=36
                            lista = bytes(lista)
                            self.com1.sendData(lista)
                            time.sleep(.8)
                            self.nextPack()
                        
                    elif self.lastPack==len(self.datagrams):
                        print("Último pacote enviado\n")
                        print("Encerrando comunicação...")
                        self.com1.disable()
                        break

                    else:
                        acknowledge, sizeAck = self.com1.getData(14)
                        if acknowledge == packagetool.Acknowledge().buildAcknowledge("ok"):
                            print("Acknowledge recebido! Autorizado envio do próximo pacote!                      ")
                            print(f"Enviando Pacote n°{self.lastPack+1}...                               \n")
                            self.com1.sendData(self.datagrams[self.lastPack])
                            time.sleep(.1)
                            self.com1.rx.clearBuffer()
                            self.nextPack()

                        elif acknowledge == packagetool.Acknowledge().buildAcknowledge("erro"):
                            print("-------------------------------------------------------------------------")
                            print(f"Ocorreu algum erro durante a transmissão do pacote nº {self.lastPack}...")
                            print("Reenviando ao server...")
                            print("--------------------------------------------------------------------------\n")
                            self.com1.sendData(self.datagrams[self.lastPack-1])
                            time.sleep(3)
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
    c = Client(serialName,"./image.jpg")
    c.sentFile()
