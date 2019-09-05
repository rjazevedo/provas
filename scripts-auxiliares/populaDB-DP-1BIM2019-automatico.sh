#!/bin/bash
#Objetivo: Esse script gera as saídas necessárias para os arquivos de csv para subir no Banco de dados os corretores-2BIM-2019
#Autor: Daniel Consiglieri
#Data Criacao:Set 2019
#Revisao:04-set-2019

#**Inicialiazacao de Variaveis**#
#Backup de csv anteriores (caminho completo)
BACKUP_CSV="/home/provas/dados/backup/2019dp1"
#Calendario no numero 39 se refere a DP 1 bimestre de 2019
CALENDARIO="39"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
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
#Nome de arquivo de base Correcoes
NOME_BASE_CORRECOES="GabaritoMultiplasEscolhas.csv"
#Caminho das provas
PATH_PROVAS="SGA/2019dp1/provas"
#Caminho da Saida Gerada (Caminho completo)
SAIDA_CSV="/home/provas/dados/SGA/2019dp1/provas/Saida-DP"
#Indicacao do tipo de prova (regular,dp)
TIPO_PROVA="dp"
#Caminho para Logs (Caminho completo)
LOG="/home/provas/dados/log/2019dp1"
#**Fim de variáveis de parametrizacao**#

#**********Modulo de geracao de csv*************#
echo "Inicio de PopulaDB - 2 Bimestre"
${HOME}/src/populaDB.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES} -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV} > ${LOG}/log_populaDB_${DATA}.log
#Correcao de path
sed -i "s#${HOME_NFS}/##g" ${SAIDA_CSV}/*.csv


#*************Modulo de backup ************************#
cat ${SAIDA_CSV}/correcoes.csv > ${BACKUP_CSV}/${DATA}_correcoes.csv
cat ${SAIDA_CSV}/folhas.csv > ${BACKUP_CSV}/${DATA}_folhas.csv
cat ${SAIDA_CSV}/guias.csv > ${BACKUP_CSV}/${DATA}_guias.csv
cat ${SAIDA_CSV}/provas.csv > ${BACKUP_CSV}/${DATA}_provas.csv
cat ${SAIDA_CSV}/questoes.csv > ${BACKUP_CSV}/${DATA}_questoes.csv

#******Modulo de Insercao de Banco de dados*****#
#Incluindo folhas
echo "Iniciando insercao no Banco de Dados"
${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaFolhas_${DATA}.log
echo "Insercao de folhas no Banco de Dados finalizada"

#Inclui corretores
${HOME}/src/sgaCorretores.py -a ${SAIDA_CSV}/correcoes.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaCorretores_${DATA}.log
echo "Insercao de corretores no Banco de Dados finalizada"

#Rotina de atualizacao BaseCorrecoes
cat ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES} ${SAIDA_CSV}/correcoes.csv > ${SAIDA_CSV}/correcoes_tmp.csv
mv ${SAIDA_CSV}/correcoes_tmp.csv ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES}
echo "Fim do populaDB automatizado"