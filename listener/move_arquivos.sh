#!/bin/bash
#Objetivo: Esse script move os arquivos para o local adequado, ainda existem melhorias a serem implementadas
#Autor: Daniel Consiglieri
#Data Criacao:Set 2019
#Revisao:14-nov-2019

PATH_PROVAS_1BIM="/home/provas/dados/SGA/provas"
PATH_PROVAS_2BIM="/home/provas/dados/SGA/2019b2/provas"
PATH_PROVAS_3BIM="/home/provas/dados/SGA/2019b3/provas"
PATH_PROVAS_1DP="/home/provas/dados/SGA/2019dp1/provas"
PATH_PROVAS_EXAME_1BIM="/home/provas/dados/SGA/2019e1/provas"
PATH_PROVAS_EXAME_2BIM="/home/provas/dados/SGA/2019e2/provas"
PATH_LIMBO="/home/provas/dados/gdrive_rclone/Nucleo-Processamento-Provas/Verifica-Thales"

#Opcoes de comando
ACTION="cp -n"
FORCED_ACTION="cp -f"
MOVE_ACTION="mv"
#yes or empty - preenchido automaticamente com base nos argumentos passados
VERBOSE_MODE=""

#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -lt 2 ]; then
	echo ${0} " Necessita de dois ou três parametros para funcionar"
else
	PATH_ORIGEM="$1"
	if [[ "$3" == "-f" ]]; then
		ACTION=${FORCED_ACTION}
	fi
	if [[ "$3" == "-m" ]]; then
		ACTION=${MOVE_ACTION}
	fi
	#echo "Opcao parametro: "${3}	
#Inicio das rotinas
	for lista in $( find ${PATH_ORIGEM} -iname '*png' );
	do
		case "${lista}" in
			*XXXXXXX*|*YYYYYYY*|*ZZZZZZZ*)
				#Limbo eh um problema, quando aparece sempre deve ser reportado
				echo "Prova - ${lista} - movida para o Limbo."
				${ACTION} "${lista}" ${PATH_LIMBO}
				;;
			*20190417*|*20190418*|*20190422*|*20190423*|*20190424*|*20190425*|*20190426*|*20190427*|*20190429*|*20190502*|*20190509*)
				
				#if [ "$VERBOSE_MODE" == "yes" ]; then
					echo "Detectei prova do primeiro bimestre - ${ACTION} ${lista} ${PATH_PROVAS_1BIM}/${2}"
				#fi				
				${ACTION} "${lista}" ${PATH_PROVAS_1BIM}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_1BIM}/${2}/${temp}.csv 2> /dev/null
					rm ${PATH_PROVAS_1BIM}/${2}/result/${temp}.txt 2> /dev/null
				fi
				
				;;
			*20190626*|*20190627*|*20190701*|*20190702*|*20190703*|*20190704*|*20190705*|*20190706*|*20190711*|*20190712*)
				#if [ "$VERBOSE_MODE" == "yes" ]; then
					echo "Detectei prova do segundo bimestre - ${ACTION} ${lista} ${PATH_PROVAS_2BIM}/${2}"
				#fi
				${ACTION} "${lista}" ${PATH_PROVAS_2BIM}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_2BIM}/${2}/${temp}.csv 2> /dev/null
					rm ${PATH_PROVAS_2BIM}/${2}/result/${temp}.txt 2> /dev/null
				fi
				
				;;
			*20190610*|*20190611*|*20190612*|*20190617*|*20190619*)
				#if [ "$VERBOSE_MODE" == "yes" ]; then
					echo "Detectei prova do DP 1 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_1DP}/${2}"
				#fi
				${ACTION} "${lista}" ${PATH_PROVAS_1DP}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_1DP}/${2}/${temp}.csv 2> /dev/null
					rm ${PATH_PROVAS_1DP}/${2}/result/${temp}.txt 2> /dev/null
				fi	
				
				;;
			*20190819*|*20190820*|*20190821*|*20190822*|*20190823*|*20190829*)
				#if [ "$VERBOSE_MODE" == "yes" ]; then
					echo "Detectei prova Exame 1 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_1BIM}/${2}"
				#fi
				${ACTION} "${lista}" ${PATH_PROVAS_EXAME_1BIM}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_EXAME_1BIM}/${2}/${temp}.csv 2> /dev/null
					rm ${PATH_PROVAS_EXAME_1BIM}/${2}/result/${temp}.txt 2> /dev/null
				fi		
				
				;;
			*20190909*|*20190910*|*20190911*|*20190912*|*20190913*|*20190916*|*20190920*)
				#if [ "$VERBOSE_MODE" == "yes" ]; then
					echo "Detectei prova Exame 2 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_2BIM}/${2}"
				#fi
				${ACTION} "${lista}" ${PATH_PROVAS_EXAME_2BIM}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_EXAME_2BIM}/${2}/${temp}.csv 2> /dev/null
					rm ${PATH_PROVAS_EXAME_2BIM}/${2}/result/${temp}.txt 2> /dev/null
				fi				
				
				;;
			*20191002*|*20191003*|*20191007*|*20191008*|*20191009*|*20191010*|*20191011*|*20191016*|*20191017*|*20191018*|*20191021*|*20191022*)
				#if [ "$VERBOSE_MODE" == "yes" ]; then
					echo "Detectei prova do terceiro bimestre - ${ACTION} ${lista} ${PATH_PROVAS_3BIM}/${2}"
				#fi
				${ACTION} "${lista}" ${PATH_PROVAS_3BIM}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_3BIM}/${2}/${temp}.csv 2> /dev/null
					rm ${PATH_PROVAS_3BIM}/${2}/result/${temp}.txt 2> /dev/null
				fi
				
				;;
			*)
				#Limbo eh um problema, quando aparece sempre deve ser reportado
				echo "Prova - ${lista} - movida para o Limbo."
				${ACTION} "${lista}" ${PATH_LIMBO}
				;;
		esac
	done
fi
