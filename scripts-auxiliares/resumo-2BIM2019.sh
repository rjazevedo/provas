#!/bin/bash
#Descricao: Script que realiza o resumo do segundo Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:04-set-2019

#**Inicialiazacao de Variaveis**#
#Caminho do arquivo de estrutura ausentes
ESTRUTURA_AUSENTES="gdrive_rclone/2_bimestre/origem/csv/ausentes.csv"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv"
#Diretorio de Home
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/provas_2_bimestre"
#**Fim de variáveis de parametrizacao**#


${HOME}/src/resumo.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ${HOME_NFS}/${ESTRUTURA_AUSENTES} -p ${HOME_NFS}/${PATH_PROVAS}

