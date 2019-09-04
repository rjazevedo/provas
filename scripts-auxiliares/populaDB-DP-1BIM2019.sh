#!/bin/bash
#Objetivo: Esse script gera as saídas necessárias para os arquivos de csv para subir no Banco de dados os corretores-DP-1BIM2019
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:29-ago-2019

#**Inicialiazacao de Variaveis**#
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_BASE_CORRECOES="csv/2019dp1/baseCorrecoes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="csv/2019dp1/corretores.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="SGA/2019dp1/guias"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="csv/2019dp1/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="csv/2019dp1/GabaritoMultiplasEscolhas.csv"
#Diretorio de HOME
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminho das provas
PATH_PROVAS="SGA/provas"
#Caminho da Saida Gerada
SAIDA_CSV="/home/provas/dados/SGA/provas/Saida-DP"
#Backup de csv anteriores
BACKUP_CSV="/home/provas/dados/backup/2019dp1"
#**Fim de variáveis de parametrizacao**#


echo "Inicio da geracao do PopulaDB - DP-1BIM2019"
${HOME}/src/populaDB.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES} -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV} > ${SAIDA_CSV}/log.txt
echo "Tratando dos arquivos csv gerados"
sed -i "s#${HOME_NFS}/##g" ${SAIDA_CSV}/*.csv