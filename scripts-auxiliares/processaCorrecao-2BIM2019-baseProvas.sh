#!/bin/bash
#Descricao: Script que processa Correcoes do 2 Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:13-ago-2019

#**Inicialiazacao de Variaveis**#
#Backup de csv anteriores
BACKUP_CSV="/home/provas/dados/backup/2019b2"
#Calendario no numero 38 se refere ao segundo bimestre de 2019
CALENDARIO="38"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Caminho do arquivo de estrutura Provas
ESTRUTURA_CSV="gdrive_rclone/2_bimestre/origem/csv/"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="gdrive_rclone/2_bimestre/origem/csv/GabaritoMultiplasEscolhas-2BIM-2019.csv"
#Diretorio de Home
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminnho para Logs
LOG="/home/provas/dados/log/2019b2"
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/provas_2_bimestre"
#Path Completo de Saida
SAIDA_CSV="/home/provas/dados/SGA/provas_2_bimestre/Saida"



#**Fim de variáveis de parametrizacao**#

echo "Iniciando o processamento de Correção 2 Bimestre de 2019"
#Incializa um arquivo de ausentes
> ${SAIDA_CSV}/ausentes_${DATA}.csv
echo "Executando o rodaScannerME, aguarde o processamento..."
${HOME}/src/rodaScannerME.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -p ${HOME_NFS}/${PATH_PROVAS}
echo "Executando converte, aguarde o processamento..."
${HOME}/src/converte.py -e ${HOME_NFS}/${PATH_PROVAS} -s ${SAIDA_CSV}/ausentes_${DATA}.csv
echo "Executando rodaLeitorPresenca, aguarde o processamento..."
${HOME}/src/rodaLeitorPresenca.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ${SAIDA_CSV}/ausentes_${DATA}.csv -p ${HOME_NFS}/${PATH_PROVAS}
#echo "Executando distribuiFolhasAusentes, aguarde o processamento..." #distribuiFolhasAusentes não será mais utilizado, foi guardado nos comentarios por histórico
#${HOME}/src/distribuiFolhasAusentes.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ${SAIDA_CSV}/ausentes_${DATA}.csv -p ${HOME_NFS}/${PATH_PROVAS} 
echo "Organizando as provas de ausentes no servidor..."
${HOME}/src/distribuiPorPolos.sh
echo "Executando corrigeME, aguarde o processamento..."
${HOME}/src/corrigeME-20190717.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -g ${HOME_NFS}/${GABARITO_PROVAS} -a ${HOME_NFS}/${PATH_PROVAS} -s ${SAIDA_CSV}/notas.csv
echo "Filtrando arquivo de saida de correcao"
#Esse passo é necessário para não sobrescrever correcoes manuais
awk '!/em branco/' ${SAIDA_CSV}/notas.csv > ${SAIDA_CSV}/nota_filtrada.csv
cat ${SAIDA_CSV}/ausentes_${DATA}.csv > ${SAIDA_CSV}/ausentes.csv
echo "Provas Corrigidas"
echo "Script processaCorre��o 2 Bimestre de 2019 finalizado"
