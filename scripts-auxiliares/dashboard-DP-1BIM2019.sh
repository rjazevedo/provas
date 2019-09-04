#!/bin/bash
#Descricao: Script que gera Dashboard DP 1 Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:21-ago-2019

#**Inicialiazacao de Variaveis**#
#Isso é invariavel
BASE_STRING="Dashboard Provas UNIVESP"
#Personaliza com informações relativas ao periodo de referencia
SUBSTITUI_STRING=" - DP 1o Bimestre 2019"
#Path para Home
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminho das provas DP 1 Bimestre
PATH_PROVAS="SGA/provas"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="csv/2019dp1/ausentes.csv"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_DASHBOARD="csv/2019dp1/todasProvasJuntas.csv"
#Nome da pasta temporaria de trabalho DP 1 Bimestre
TRABALHO_TMP="d1DPBIM2019"
#Destino de Dashboad DP 1 bimestre
DESTINO_DASHBOARD="SGA/dashboard/dp"
#**Fim de variáveis de parametrizacao**#

cd ${HOME}/tmp
mkdir ${TRABALHO_TMP}
echo "Inicio da geração do DashBoard - DP 1o Bimestre 2019"
~/src/dashboard.py -e ${HOME_NFS}/${PATH_PROVAS} -p ${HOME_NFS}/${ESTRUTURA_DASHBOARD} -s ${HOME}/tmp/${TRABALHO_TMP} -a ${HOME_NFS}/${ESTRUTURA_AUSENTES}
cd ${HOME}/tmp/${TRABALHO_TMP}
#Rotina de personalização de HTML
sed -i "s/${BASE_STRING}/${BASE_STRING}${SUBSTITUI_STRING}/g" *.html
cp -f *.html ${HOME_NFS}/${DESTINO_DASHBOARD}
cd ${HOME}/tmp
rm -rf ${TRABALHO_TMP}
