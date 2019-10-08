#!/bin/bash
#Objetivo: Esse � um script para corrigir a anomalia de PopulaDB que uma vez gerado folhas n�o gera mais folhas, rodar poucas vezes para n�o gerar um gasto de processamento desnecess�rio de processamento
# Altera o PopulaDB para diversas provas
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:16-set-2019

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 1 ]; then
	echo ${0} " Necessita que exatamente um parametro com as configuracoes seja passado por argumento"
else
	source ${1}
#Inicio das rotinas

	#Adapta��o full-insertion
	>${SAIDA_CSV}/base_zero.csv


	#**********Modulo de geracao de csv*************# #Modifica como base de correcoes para a base zero
	echo ${MSG_FULLINSERTION_INICIO}
	${HOME}/src/populaDB-embaralhado.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${SAIDA_CSV}/base_zero.csv -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV} > ${LOG}/log_full-insertion_populaDB_${DATA}.log
	#Correcao de path
	sed -i "s#${HOME_NFS}/##g" ${SAIDA_CSV}/*.csv

	#*************Modulo de backup ************************#
	cat ${SAIDA_CSV}/correcoes.csv > ${BACKUP_CSV}/${DATA}-full-insertion_correcoes.csv
	cat ${SAIDA_CSV}/folhas.csv > ${BACKUP_CSV}/${DATA}-full-insertion_folhas.csv
	cat ${SAIDA_CSV}/guias.csv > ${BACKUP_CSV}/${DATA}-full-insertion_guias.csv
	cat ${SAIDA_CSV}/provas.csv > ${BACKUP_CSV}/${DATA}-full-insertion_provas.csv
	cat ${SAIDA_CSV}/questoes.csv > ${BACKUP_CSV}/${DATA}-full-insertion_questoes.csv

	${HOME}/src/sgaTestesGuias.py -a ${SAIDA_CSV}/guias.csv
	${HOME}/src/sgaQuestoes -a ${SAIDA_CSV}/questoes.csv

	#******Modulo de Insercao de Banco de dados*****#
	#Incluindo folhas
	echo "Iniciando insercao no Banco de Dados"
	${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_full-insertion_sgaFolhas_${DATA}.log
	echo "Insercao de folhas no Banco de Dados finalizada"
	echo ${MSG_FULLINSERTION_FIM}
fi
