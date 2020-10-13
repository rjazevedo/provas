#!/bin/bash
#Descricao: Script que gera Dashboard
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:28-jan-2020

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 1 ]; then
	echo ${0} "Necessita que exatamente um parametro com as configuracoes seja passado por argumento"
else
	source ${1}
#Inicio das rotinas

	cd ${HOME}/tmp
	mkdir ${TRABALHO_TMP}
	echo ${MSG_DASH_INICIO}
	${HOME}/src/dashboard.py -e ${HOME_NFS}/${PATH_PROVAS} -p ${HOME_NFS}/${ESTRUTURA_DASHBOARD} -s ${HOME}/tmp/${TRABALHO_TMP} -a ${HOME_NFS}/${ESTRUTURA_AUSENTES}
	
	if [ "$REGULAR_E_DP" == "sim" ]; then	
		if [ "$TIPO_PROVA_DP" == "dpexam" ];then
			${HOME}/src/dashboard_correcao.py -c "${CALENDARIO},${CALENDARIO_DP}" -t "${TIPO_PROVA},dp" -s ${HOME}/tmp/${TRABALHO_TMP}
		else
			${HOME}/src/dashboard_correcao.py -c "${CALENDARIO},${CALENDARIO_DP}" -t "${TIPO_PROVA},${TIPO_PROVA_DP}" -s ${HOME}/tmp/${TRABALHO_TMP}
		fi
	else
		${HOME}/src/dashboard_correcao.py -c ${CALENDARIO} -t ${TIPO_PROVA} -s ${HOME}/tmp/${TRABALHO_TMP}
	fi
	cd ${HOME}/tmp/${TRABALHO_TMP}
	#Rotina de personalização de HTML
	sed -i "s/${BASE_STRING}/${BASE_STRING}${SUBSTITUI_STRING}/g" *.html

	cp -f *.html ${HOME_NFS}/${DESTINO_DASHBOARD}
	cp -f *.csv ${HOME_NFS}/${DESTINO_DASHBOARD}
	cd ${HOME}/tmp
	rm -rf ${TRABALHO_TMP}
fi
