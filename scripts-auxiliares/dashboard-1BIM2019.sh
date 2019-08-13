#!/bin/bash
#Descricao: Script que gera Dashboard do 1 Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Maio 2019
#Revisao:

#**Inicialiazacao de Variaveis**#
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminho das provas 1 Bimestre
PATH_PROVAS="SGA/provas"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="SGA/provas/ausentes.csv"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_DASHBOARD="SGA/db/todasProvasJuntas.csv"
#Nome da pasta temporaria de trabalho 1 Bimestre
TRABALHO_TMP="d1BIM2019"
#Destino de Dashboad 1 bimestre
DESTINO_DASHBOARD="SGA/dashboard/"
#**Fim de variáveis de parametrizacao**#

cd ${HOME}/tmp
mkdir ${TRABALHO_TMP}
echo "Inicio da geração do DashBoard - 1 Bimestre 2019"
~/src/dashboard.py -e ${HOME_NFS}/${PATH_PROVAS} -p ${HOME_NFS}/${ESTRUTURA_DASHBOARD} -s ${HOME}/tmp/${TRABALHO_TMP} -a ${HOME_NFS}/${ESTRUTURA_AUSENTES}
cd ${HOME}/tmp/${TRABALHO_TMP}
cp -f *.html ${HOME_NFS}/${DESTINO_DASHBOARD}
cd ${HOME}/tmp
rm -rf ${TRABALHO_TMP}
