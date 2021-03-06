#!/bin/bash
#Objetivo: Esse script gera as sa�das necess�rias para os arquivos de csv para subir no Banco de dados os corretores-2BIM-2019
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:13-ago-2019

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 1 ]; then
	echo ${0} " Necessita que exatamente um parametro com as configuracoes seja passado por argumento"
else
	source ${1}
#Inicio das rotinas

	echo ${MSG_POPULADB_INICIO}
	${HOME}/src/populaDB-embaralhado.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES} -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV} > ${SAIDA_CSV}/log.txt
	echo "Tratando dos arquivos csv gerados"
	sed -i "s#${HOME_NFS}/##g" ${SAIDA_CSV}/*.csv
	
	#Remove duplicados
	cat ${SAIDA_CSV}/guias.csv | sort | uniq > ${SAIDA_CSV}/guias_tmp.csv
	cat ${SAIDA_CSV}/questoes.csv | sort | uniq > ${SAIDA_CSV}/questoes_tmp.csv
	mv ${SAIDA_CSV}/questoes_tmp.csv ${SAIDA_CSV}/questoes.csv
	mv ${SAIDA_CSV}/guias_tmp.csv ${SAIDA_CSV}/guias.csv
	
fi
