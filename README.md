# Projeto 3 de Camada Física da Computação 
## Fragmentação, hand-shake e datagrama

### Autores:
* [Matheus Oliveira](https://github.com/matheus-1618)
* [Nívea Abreu](https://github.com/niveaabreu)

### Descrição:
Implementação de um simulação client-server com envio e recebimento de ações que obedecem uma ordenação temporal real.


Foi construído um código em Python para transmissão de um determinada quantidade de comandos(client) e recepção e reenvio do tamanho recebido (server) para assim certificar a comunicação serial.


Foram simulados três tipos de casos:
- SUCESSO DE TRANSMISSÃO: Envio de uma quantidade aleatória (entre 10 e 30) e sorteada de comandos de bytes a cada requisição do client, na qual o server deve receber e diferenciar os comandos enviando uma resposta em menos de 10 segundos do tamanho recebido, para que o client confirme que o tamanho de envio e de recebimento seja adequado.

- ERRO DE TRANSMISSÃO: Situação em que após o server realizar o recebimento dos comandos, enviar uma quantidade errada de comandos para o client, gerando um erro de retransmissão de dados.

- CASO DE TIMEOUT: Situação na qual, após o client enviar os comandos, ele não recebe nenhuma resposta de volta do server em 10s, encerrando a comunicação.

Para montagem, use dois Arduinos uno e 5 jumpers, para ligar os terminais TX e RX cruzado de cada Arduino, e depois conecte cada arduino a um computador (ou ao mesmo se for caso, mas em portas diferentes).
<center><img src="arduinos.jpeg"  style="float: center; margin: 0px 0px 10px 10px"></center>

Para realizar a simulação, abra um terminal na pasta server e execute o comando abaixo, e selecione o caso a ser simulado:

```console
 borg@borg:~ python aplicacao_server.py
```
Simultaneamente, abra outro terminal, em outro computador conectado ao arduino, ou em relação a outra porta no mesmo computador e execute, dentro da pasta client. o comando baixo, dando inicio a transmissão e recebimento dos dados:
```console
 borg@borg:~ python aplicacao_client.py
```

Assim, poderão ser simulados os casos de transmissão e recepção entre computadores ou portas diferentes, garantindo comunicação ou simulando casos de erro.

 <center><img src="groot.gif"  style="float: center; margin: 0px 0px 10px 10px"></center>

 ©Insper, 4° Semestre Engenharia da Computação, Camada Física da Computação.