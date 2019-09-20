#!/bin/bash
#Objetivo: Esse script move os arquivos para o local adequado
#Autor: Daniel Consiglieri
#Data Criacao:Set 2019
#Revisao:20-set-2019

PATH_PROVAS_1BIM="/home/provas/dados/SGA/provas"
PATH_PROVAS_2BIM="/home/provas/dados/SGA/2019b2/provas"
PATH_PROVAS_1DP="/home/provas/dados/SGA/2019dp1/provas"
PATH_PROVAS_EXAME_1BIM="/home/provas/dados/SGA/2019e1/provas"
PATH_PROVAS_EXAME_2BIM="/home/provas/dados/SGA/2019e2/provas"
PATH_LIMBO="/home/provas/dados/tmp/Limbo"

#Opcoes de comando
ACTION="cp -n"


#Deve ser passado por parametro o arquivo de configuracao
if [ "$#" -ne 2 ]; then
	echo ${0} " Necessita de dois parametros para funcionar"
else
	PATH_ORIGEM="$1"
#Inicio das rotinas
	for lista in $(find ${PATH_ORIGEM} -iname '*png');
	do
		case ${lista} in
			*20190417*|*20190418*|*20190422*|*20190423*|*20190424*|*20190425*|*20190426*|*20190427*|*20190429*|*20190502*|*20190509*)
				echo "Detectei prova do primeiro bimestre - ${ACTION} ${lista} ${PATH_PROVAS_1BIM}/${2}"
				${ACTION} ${lista} ${PATH_PROVAS_1BIM}/${2}
				
				;;
			*20190626*|*20190627*|*20190701*|*20190702*|*20190703*|*20190704*|*20190705*|*20190706*|*20190711*|*20190712*)
				echo "Detectei prova do segundo bimestre - ${ACTION} ${lista} ${PATH_PROVAS_2BIM}/${2}"
				${ACTION} ${lista} ${PATH_PROVAS_2BIM}/${2}
				;;
			*20190610*|*20190611*|*20190612*|*20190617*|*20190619*)
				echo "Detectei prova do DP 1 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_1DP}/${2}"
				${ACTION} ${lista} ${PATH_PROVAS_1DP}/${2}
				;;
			*20190819*|*20190820*|*20190821*|*20190822*|*20190823*|*20190829*)
				echo "Detectei prova Exame 1 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_1BIM}/${2}"
				${ACTION} ${lista} ${PATH_PROVAS_EXAME_1BIM}/${2}
				;;
			*20190909*|*20190910*|*20190911*|*20190912*|*20190913*|*20190916*|*20190920*)
				echo "Detectei prova Exame 2 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_2BIM}/${2}"
				${ACTION} ${lista} ${PATH_PROVAS_EXAME_2BIM}/${2}
				;;
			*)
				echo "Prova - ${lista} - movida para o Limbo."
				${ACTION} ${lista} ${PATH_LIMBO}
				;;
		esac
	done
fi


