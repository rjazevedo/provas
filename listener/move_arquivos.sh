#!/bin/bash
#Objetivo: Esse script move os arquivos para o local adequado
#Autor: Daniel Consiglieri
#Data Criacao:Set 2019
#Revisao:23-set-2019

PATH_PROVAS_1BIM="/home/provas/dados/SGA/provas"
PATH_PROVAS_2BIM="/home/provas/dados/SGA/2019b2/provas"
PATH_PROVAS_1DP="/home/provas/dados/SGA/2019dp1/provas"
PATH_PROVAS_EXAME_1BIM="/home/provas/dados/SGA/2019e1/provas"
PATH_PROVAS_EXAME_2BIM="/home/provas/dados/SGA/2019e2/provas"
PATH_LIMBO="/home/provas/dados/tmp/Limbo"

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
	if [[ "$3" == "-*f*" ]]; then
		ACTION=${FORCED_ACTION}
	fi
	if [[ "$3" == "-*m*" ]]; then
		ACTION=${MOVE_ACTION}
	fi
	if [[ "$3" == "-*v*" ]]; then
		VERBOSE_MODE="yes"
	fi
	if [[ "$3" == "-*mf*" ]] || [[ "$3" == "-*fm*" ]]; then
		echo "Opcao invalida, você deve escolher copia passiva, copia forçada ou mover arquivos -- usando opcao default: copia somente se não houver arquivo"
		ACTION="cp -n"
	fi	
#Inicio das rotinas
	for lista in $(find ${PATH_ORIGEM} -iname '*png');
	do
		case ${lista} in
			*20190417*|*20190418*|*20190422*|*20190423*|*20190424*|*20190425*|*20190426*|*20190427*|*20190429*|*20190502*|*20190509*)
				
				if [ "$VERBOSE_MODE" == "yes" ]
					echo "Detectei prova do primeiro bimestre - ${ACTION} ${lista} ${PATH_PROVAS_1BIM}/${2}"
				fi				
				${ACTION} ${lista} ${PATH_PROVAS_1BIM}/${2}
				
				;;
			*20190626*|*20190627*|*20190701*|*20190702*|*20190703*|*20190704*|*20190705*|*20190706*|*20190711*|*20190712*)
				if [ "$VERBOSE_MODE" == "yes" ]
					echo "Detectei prova do segundo bimestre - ${ACTION} ${lista} ${PATH_PROVAS_2BIM}/${2}"
				fi
				${ACTION} ${lista} ${PATH_PROVAS_2BIM}/${2}
				;;
			*20190610*|*20190611*|*20190612*|*20190617*|*20190619*)
				if [ "$VERBOSE_MODE" == "yes" ]
					echo "Detectei prova do DP 1 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_1DP}/${2}"
				fi
				${ACTION} ${lista} ${PATH_PROVAS_1DP}/${2}
				;;
			*20190819*|*20190820*|*20190821*|*20190822*|*20190823*|*20190829*)
				if [ "$VERBOSE_MODE" == "yes" ]
					echo "Detectei prova Exame 1 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_1BIM}/${2}"
				fi
				${ACTION} ${lista} ${PATH_PROVAS_EXAME_1BIM}/${2}
				;;
			*20190909*|*20190910*|*20190911*|*20190912*|*20190913*|*20190916*|*20190920*)
				if [ "$VERBOSE_MODE" == "yes" ]
					echo "Detectei prova Exame 2 bimestre - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_2BIM}/${2}"
				fi
				${ACTION} ${lista} ${PATH_PROVAS_EXAME_2BIM}/${2}
				;;
			*)
				#Limbo eh um problema, quando aparece sempre deve ser reportado
				echo "Prova - ${lista} - movida para o Limbo."
				${ACTION} ${lista} ${PATH_LIMBO}
				;;
		esac
	done
fi


