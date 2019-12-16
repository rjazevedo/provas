#!/bin/bash
#Descricao: Script que processa Correcoes do 2 Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:26-ago-2019

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 1 ]; then
	echo ${0} " Necessita que exatamente um parametro com as configuracoes seja passado por argumento"
else
	source ${1}
#Inicio das rotinas

	echo ${MSG_CORRECAO_AUTOMATICO_INICIO}
	#Incializa um arquivo de ausentes
	> ${SAIDA_CSV}/ausentes.csv
	echo "Executando o rodaScannerME, aguarde o processamento..."
	${HOME}/src/rodaScannerME.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -p ${HOME_NFS}/${PATH_PROVAS} > ${LOG}/log_rodaScannerME_${DATA}.log
	echo "Executando converte, aguarde o processamento..."
	${HOME}/src/converte.py -e ${HOME_NFS}/${PATH_PROVAS} -s ${SAIDA_CSV}/ausentes.csv > ${LOG}/log_converte_${DATA}.log
	echo "Executando rodaLeitorPresenca, aguarde o processamento..."
	${HOME}/src/rodaLeitorPresenca.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ${SAIDA_CSV}/ausentes.csv -p ${HOME_NFS}/${PATH_PROVAS} > ${LOG}/log_rodaLeitorPresenca_${DATA}.log
	#echo "Executando distribuiFolhasAusentes, aguarde o processamento..." #distribuiFolhasAusentes não será mais utilizado, foi guardado nos comentarios por histórico
	#${HOME}/src/distribuiFolhasAusentes.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ${SAIDA_CSV}/ausentes_${DATA}.csv -p ${HOME_NFS}/${PATH_PROVAS} 
	#${HOME}/src/distribuiPorPolos.sh #distribuiPorPolos não será mais utilizado, pois era para arrumar o que o distribuiFolhasAusentes deixava espalhado
	echo "Executando corrigeME, aguarde o processamento..."
	${HOME}/src/corrigeME-20190717.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -g ${HOME_NFS}/${GABARITO_PROVAS} -a ${HOME_NFS}/${PATH_PROVAS} -s ${SAIDA_CSV}/notas.csv > ${LOG}/log_corrigeME-20190717_${DATA}.log
	echo "Filtrando arquivo de saida de correcao"
	#Esse passo é necessário para não sobrescrever correcoes de Notas manuais
	awk '!/em branco/' ${SAIDA_CSV}/notas.csv > ${SAIDA_CSV}/nota_filtrada.csv


	#*************Modulo de backup ************************#
	cat ${SAIDA_CSV}/nota_filtrada.csv > ${BACKUP_CSV}/${DATA}_nota_filtrada.csv
	cat ${SAIDA_CSV}/notas.csv > ${BACKUP_CSV}/${DATA}_nota_raw.csv

	#Concatena o ausentes manual e automatico
	cat ${SAIDA_CSV}/ausentes.csv ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual.csv | sort | uniq > ${SAIDA_CSV}/ausentes_tmp.csv
	#comm -23 <(sort ausentes_anterior.csv) <(sort ausentes_manual.csv) > saida_presentes.csv
	#${HOME}/src/sgaPresentes.py -a ${SAIDA_CSV}/ausentes.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaPresentes_${DATA}.log
	#depois copia o ausentes_manual para o ausentes_anterior

	cat ${SAIDA_CSV}/ausentes_tmp.csv > ${SAIDA_CSV}/ausentes.csv
	cat ${SAIDA_CSV}/ausentes.csv > ${BACKUP_CSV}/${DATA}_ausentes.csv
	
	cat ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual.csv | sort | uniq > ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual_tmp.csv
	mv ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual_tmp.csv ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual.csv

	#******Modulo de Insercao de Banco de dados*****#
	#Incluindo notas
	echo "Iniciando insercao no Banco de Dados"
	${HOME}/src/sgaNotas.py -a ${SAIDA_CSV}/nota_filtrada.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaNotas_${DATA}.log
	echo "Insercao de Notas no Banco de Dados finalizada"

	#Inclui ausentes
	${HOME}/src/sgaAusentes.py -a ${SAIDA_CSV}/ausentes.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaAusentes_${DATA}.log
	echo "Insercao de ausentes no Banco de Dados finalizada"

	#Rotina de atualizacao Ausentes
	mv ${SAIDA_CSV}/ausentes_tmp.csv ${HOME_NFS}/${ESTRUTURA_AUSENTES}

	echo "Provas Corrigidas"
	echo ${MSG_CORRECAO_AUTOMATICO_FIM}
fi
