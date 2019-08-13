#!/bin/bash
#Descricao: Script que gera Dashboard do 2 Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:13-ago-2019

#**Inicialiazacao de Variaveis**#
HOME="/home/provas"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Caminho das provas 2 Bimestre
PATH_PROVAS="SGA/provas_2_bimestre"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_PROVAS="gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="gdrive_rclone/2_bimestre/origem/csv/GabaritoMultiplasEscolhas-2BIM-2019.csv"
SAIDA_CSV="/home/provas/dados/SGA/provas_2_bimestre/Saida"
#**Fim de variÃ¡veis de parametrizacao**#

echo "Iniciando o processamento de CorreÃ§Ã£o 2 Bimestre de 2019"
#Direcionando para a pasta de saida
cd ${PATH_PROVAS}
#Incializa um arquivo de ausentes
>ausentes.csv
#${HOME_NFS}/tmp/srcTMP/remove-csv-txt.sh
echo "Executando o rodaScannerME, aguarde o processamento..."
${HOME}/src/rodaScannerME.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -p ${HOME_NFS}/${PATH_PROVAS}
echo "Executando converte, aguarde o processamento..."
${HOME}/src/converte.py -e ${HOME_NFS}/${PATH_PROVAS} -s ausentes.csv
echo "Executando rodaLeitorPresenca, aguarde o processamento..."
${HOME}/src/rodaLeitorPresenca.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ausentes.csv -p ${HOME_NFS}/${PATH_PROVAS}
#echo "Executando distribuiFolhasAusentes, aguarde o processamento..."
#${HOME}/src/distribuiFolhasAusentes.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ausentes.csv -p ${HOME_NFS}/${PATH_PROVAS}
echo "Organizando as provas de ausentes no servidor..."
${HOME}/src/distribuiPorPolos.sh
echo "Executando corrigeME, aguarde o processamento..."
${HOME}/src/corrigeME-20190717.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -g ${HOME_NFS}/${GABARITO_PROVAS} -a ${HOME_NFS}/${PATH_PROVAS} -s notas.csv
echo "Provas Corrigidas"
echo "Script processaCorreção 2 Bimestre de 2019 finalizado"
