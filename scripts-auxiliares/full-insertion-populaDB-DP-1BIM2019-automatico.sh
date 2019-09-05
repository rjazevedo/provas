#!/bin/bash
#Objetivo: Esse é um script para corrigir a anomalia de PopulaDB que uma vez gerado folhas não gera mais folhas, rodar poucas vezes para não gerar um gasto de processamento desnecessário de processamento
#Autor: Daniel Consiglieri
#Data Criacao:Set 2019
#Revisao:04-set-2019

#**Inicialiazacao de Variaveis**#
#Backup de csv anteriores
BACKUP_CSV="/home/provas/dados/backup/2019dp1"
#Calendario no numero 39 se refere a DP bimestre de 2019
CALENDARIO="39"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Caminho do arquivo de estrutura Corretores ###No full-insertion o preenchimento desta variavel ESTRUTURA_BASE_CORRECOES não importa
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
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/2019dp1/provas"
#Caminho da Saida Gerada (caminho completo)
SAIDA_CSV="/home/provas/dados/SGA/2019dp1/provas/Saida-DP"
#Indicacao do tipo de prova (regular,dp)
TIPO_PROVA="dp"
#Caminho para Logs
LOG="/home/provas/dados/log/2019dp1"
#**Fim de variáveis de parametrizacao**#

#Adaptação full-insertion
>${SAIDA_CSV}/base_zero.csv


#**********Modulo de geracao de csv*************# #Modifica como base de correcoes para a base zero
echo "Inicio de PopulaDB - 2 Bimestre"
${HOME}/src/populaDB.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${SAIDA_CSV}/base_zero.csv -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV} > ${LOG}/log_full-insertion_populaDB_${DATA}.log
#Correcao de path
sed -i "s#${HOME_NFS}/##g" ${SAIDA_CSV}/*.csv

#*************Modulo de backup ************************#
cat ${SAIDA_CSV}/correcoes.csv > ${BACKUP_CSV}/${DATA}-full-insertion_correcoes.csv
cat ${SAIDA_CSV}/folhas.csv > ${BACKUP_CSV}/${DATA}-full-insertion_folhas.csv
cat ${SAIDA_CSV}/guias.csv > ${BACKUP_CSV}/${DATA}-full-insertion_guias.csv
cat ${SAIDA_CSV}/provas.csv > ${BACKUP_CSV}/${DATA}-full-insertion_provas.csv
cat ${SAIDA_CSV}/questoes.csv > ${BACKUP_CSV}/${DATA}-full-insertion_questoes.csv

#******Modulo de Insercao de Banco de dados*****#
#Incluindo folhas
echo "Iniciando insercao no Banco de Dados"
${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_full-insertion_sgaFolhas_${DATA}.log
echo "Insercao de folhas no Banco de Dados finalizada"


echo "Fim do populaDB automatizado"