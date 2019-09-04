#!/bin/bash
#Objetivo: Esse é um script para corrigir a anomalia de PopulaDB que uma vez gerado folhas não gera mais folhas, rodar poucas vezes para não gerar um gasto de processamento desnecessário de processamento
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:14-ago-2019

#**Inicialiazacao de Variaveis**#
#Backup de csv anteriores
BACKUP_CSV="/home/provas/dados/backup/2019b2"
#Calendario no numero 38 se refere ao segundo bimestre de 2019
CALENDARIO="38"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Caminho do arquivo de estrutura Corretores ###No full-insertion o preenchimento desta variavel ESTRUTURA_BASE_CORRECOES não importa
ESTRUTURA_BASE_CORRECOES="gdrive_rclone/2_bimestre/origem/csv/baseCorrecoes-2BIM-2019.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="gdrive_rclone/2_bimestre/origem/csv/corretores-2BIM-2019.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="SGA/guias_2_bimestre_2019"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="gdrive_rclone/2_bimestre/origem/csv/GabaritoMultiplasEscolhas-2BIM-2019.csv"
#Diretorio de HOME
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Nome de arquivo de base Correcoes
NOME_BASE_CORRECOES="GabaritoMultiplasEscolhas-2BIM-2019.csv"
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/provas_2_bimestre"
#Caminho da Saida Gerada
SAIDA_CSV="/home/provas/dados/SGA/provas_2_bimestre/Saida"
#Caminnho para Logs
LOG="/home/provas/dados/log/2019b2"
#**Fim de variáveis de parametrizacao**#

#Adaptação full-insertion
>${SAIDA_CSV}/base_zero.csv


#**********Modulo de geracao de csv*************# #Modifica como base de correcoes para a base zero
echo "Inicio de PopulaDB - 2 Bimestre"
${HOME}/src/populaDB.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${SAIDA_CSV}/base_zero.csv -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV} > ${LOG}/log_full-insertion_populaDB_${DATA}.log
#Correcao de path
awk -f ${HOME}/src/filtra.awk ${SAIDA_CSV}/folhas.csv > ${SAIDA_CSV}/folha_filtrada.csv
mv ${SAIDA_CSV}/folha_filtrada.csv ${SAIDA_CSV}/folhas.csv


#*************Modulo de backup ************************#
cat ${SAIDA_CSV}/correcoes.csv > ${BACKUP_CSV}/${DATA}-full-insertion_correcoes.csv
cat ${SAIDA_CSV}/folhas.csv > ${BACKUP_CSV}/${DATA}-full-insertion_folhas.csv
cat ${SAIDA_CSV}/guias.csv > ${BACKUP_CSV}/${DATA}-full-insertion_guias.csv
cat ${SAIDA_CSV}/provas.csv > ${BACKUP_CSV}/${DATA}-full-insertion_provas.csv
cat ${SAIDA_CSV}/questoes.csv > ${BACKUP_CSV}/${DATA}-full-insertion_questoes.csv

#******Modulo de Insercao de Banco de dados*****#
#Incluindo folhas
echo "Iniciando insercao no Banco de Dados"
${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas.csv -c ${CALENDARIO} > ${LOG}/log_full-insertion_sgaFolhas_${DATA}.log
echo "Insercao de folhas no Banco de Dados finalizada"


echo "Fim do populaDB automatizado"