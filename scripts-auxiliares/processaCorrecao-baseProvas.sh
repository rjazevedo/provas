#!/bin/bash
#Descricao: Script que processa Correcoes
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:16-set-2019

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 1 ]; then
	echo ${0} " Necessita que exatamente um parametro com as configuracoes seja passado por argumento"
else
	source ${1}
#Inicio das rotinas

	echo ${0} " - Inicializado..."
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
	echo ${0} " - finalizado"
fi

