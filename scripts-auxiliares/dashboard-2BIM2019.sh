#!/bin/bash
#Descricao: Script que gera Dashboard do 2 Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:20-ago-2019

#**Inicialiazacao de Variaveis**#
#Isso é invariavel
BASE_STRING="Dashboard Provas UNIVESP"
#Personaliza com informações relativas ao periodo de referencia
SUBSTITUI_STRING=" - 2o Bimestre 2019"
#Path para Home
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/provas_2_bimestre"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="gdrive_rclone/2_bimestre/origem/csv/ausentes.csv"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_DASHBOARD="gdrive_rclone/2_bimestre/origem/csv/dashboard-2BIM-2019.csv"
#Nome da pasta temporaria de trabalho 2 Bimestre
TRABALHO_TMP="d2BIM2019"
#Destino de Dashboad 2 bimestre
DESTINO_DASHBOARD="SGA/dashboard/2bim"
#**Fim de variáveis de parametrizacao**#

cd ${HOME}/tmp
mkdir ${TRABALHO_TMP}
echo "Inicio da geração do DashBoard - 2 Bimestre 2019"
~/src/dashboard.py -e ${HOME_NFS}/${PATH_PROVAS} -p ${HOME_NFS}/${ESTRUTURA_DASHBOARD} -s ${HOME}/tmp/${TRABALHO_TMP} -a ${HOME_NFS}/${ESTRUTURA_AUSENTES}
cd ${HOME}/tmp/${TRABALHO_TMP}

#Rotina de personalização de HTML
sed -i "s/${BASE_STRING}/${BASE_STRING}${SUBSTITUI_STRING}/g" *.html

cp -f *.html ${HOME_NFS}/${DESTINO_DASHBOARD}
cd ${HOME}/tmp
rm -rf ${TRABALHO_TMP}