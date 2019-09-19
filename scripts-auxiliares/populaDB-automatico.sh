#!/bin/bash
#Objetivo: Esse script gera as saídas necessárias para os arquivos de csv para subir no Banco de dados os corretores e folhas
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:16-set-2019

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 1 ]; then
	echo ${0} " Necessita que exatamente um parametro com as configuracoes seja passado por argumento"
else
	source ${1}
#Inicio das rotinas

	#**********Modulo de geracao de csv*************#
	echo ${MSG_POPULADB_AUTOMATICO_INICIO}
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
	
	#Essa rotina é exclusiva do populaDB, nao deve ser usada em fullInsertion
	if [ "${BIMESTRE_CONSOLIDADO}" == "sim" ]; then
		cat ${SAIDA_CSV}/correcoes.csv > ${SAIDA_CSV}/lista_referencia_liberacao.csv
		sed -i -e 's/^/X,X,/' ${SAIDA_CSV}/lista_referencia_liberacao.csv
		${HOME}/src/sgaPresentes.py -a ${SAIDA_CSV}/lista_referencia_liberacao.csv -c ${CALENDARIO} -t ${TIPO_PROVA} -e > ${LOG}/log_sgaPresentes_liberados_${DATA}.log
		#rm ${SAIDA_CSV}/lista_referencia_liberacao.csv
	fi
	
	echo ${MSG_POPULADB_AUTOMATICO_FIM}
fi
