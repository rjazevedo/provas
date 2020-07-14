#!/bin/bash
#Objetivo: Processamento de provas Anistia, incluindo a correção para todas as particularidades e ocorrencias
#Data Criacao:06-jul-2020
#Autor: Daniel Consiglieri
#Data Ultima alteracao: 06-jul-2020

source /home/provas/src/scripts-auxiliares/config/2019anistia-conf.sh

#Correcao de caderno respostas nao correspondente a guia
for i in $( find ${HOME_NFS}/${PATH_PROVAS} -iname '*-P0*.png' );
do
	echo -e "mv ${i} ${i/-P0/-A0}" >> ${LOG}/log_arquivosRenomeados_${DATA}.log
	mv ${i} ${i/-P0/-A0}
done

for i in $( find ${HOME_NFS}/${PATH_PROVAS} -iname '*-E00*.png' );
do
	echo -e "mv ${i} ${i/-E0/-A0}" >> ${LOG}/log_arquivosRenomeados_${DATA}.log
	mv ${i} ${i/-E0/-A0}
done

#Chama as rotinas de processamento de provas
/home/provas/src/scripts-auxiliares/processamentoProvas-geral.sh /home/provas/src/scripts-auxiliares/config/2019anistia-conf.sh