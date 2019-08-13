#!/bin/bash
#Subrotina do programa:processaLoteDecoder-1BIM2019 
#Autor:Daniel Consiglieri
#Data:19-jul-2019

#**Inicialiazacao de Variaveis**#
HOME="/home/provas"
#**Fim de variáveis de parametrizacao**#

echo "Inicio da leitura do decoder"
${HOME}/src/decodeqr.py -e Provas/ -t Trabalho/ -s Saida/ -r Refugo
echo "acessando a pasta de Saida..."
cd Saida/
echo "Criando todos os diretorios"
${HOME}/src/criaDirPolos.sh
echo "Distribuindo as provas nos diretorios locais correspondetes"
${HOME}/src/distribuiPorPolos.sh
cd ../
