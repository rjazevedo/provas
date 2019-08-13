#!/bin/bash
#Objetivo: Esse script gera as saídas necessárias para os arquivos de csv para subir no Banco de dados os corretores-2BIM-2019
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:13-ago-2019

#**Inicialiazacao de Variaveis**#
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_BASE_CORRECOES="gdrive_rclone/2_bimestre/origem/csv/baseCorrecoes-2BIM-2019.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="gdrive_rclone/2_bimestre/origem/csv/corretores-2BIM-2019.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="${ESTRUTURA_GUIAS}"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="gdrive_rclone/2_bimestre/origem/csv/GabaritoMultiplasEscolhas-2BIM-2019.csv"
#Diretorio de HOME
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/provas_2_bimestre"
#Caminho da Saida Gerada
SAIDA_CSV="/home/provas/dados/SGA/provas_2_bimestre/Saida"
#**Fim de variáveis de parametrizacao**#


echo "Inicio da geração do PopulaDB - 2 Bimestre"
${HOME}/src/populaDB.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES} -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV}