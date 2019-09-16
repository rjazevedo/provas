#!/bin/bash
#Descricao: Script que realiza o resumo do segundo Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:04-set-2019

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 1 ]; then
	echo ${0} " Necessita que exatamente um parametro com as configuracoes seja passado por argumento"
else
	source ${1}
#Inicio das rotinas
	${HOME}/src/resumo.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ${HOME_NFS}/${ESTRUTURA_AUSENTES} -p ${HOME_NFS}/${PATH_PROVAS}
fi
