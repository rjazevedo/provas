#!/bin/bash
#Objetivo: Esse script move os arquivos para o local adequado, ainda existem melhorias a serem implementadas
#Autor: Daniel Consiglieri
#Data Criacao:Set 2019
#Revisao:06-fev-2020

<<DATAS_CORINGAS
Regulares:
1BIM2019 - 20190512
2BIM2019 - 20190714
3BIM2019 - 20191024
4BIM2019 - 20191222
Exames:
E1BIM2019 - 20190901
E2BIM2019 - 20190922
DP:
DP1Semestre2019 - 20190623 

DATAS_CORINGAS

PATH_PROVAS_1BIM2019="/home/provas/dados/SGA/provas"
PATH_PROVAS_2BIM2019="/home/provas/dados/SGA/2019b2/provas"
PATH_PROVAS_3BIM2019="/home/provas/dados/SGA/2019b3/provas"
PATH_PROVAS_4BIM2019="/home/provas/dados/SGA/2019b4/provas"
PATH_PROVAS_1DP2019="/home/provas/dados/SGA/2019dp1/provas"
PATH_PROVAS_1DP2020="/home/provas/dados/SGA/2020dp1/provas"
PATH_PROVAS_EXAME_1BIM2019="/home/provas/dados/SGA/2019e1/provas"
PATH_PROVAS_EXAME_2BIM2019="/home/provas/dados/SGA/2019e2/provas"
PATH_PROVAS_EXAME_3BIM2019="/home/provas/dados/SGA/2019e3/provas"
PATH_PROVAS_EXAME_4BIM2019="/home/provas/dados/SGA/2019e4/provas"
PATH_LIMBO="/home/provas/dados/gdrive_rclone/Nucleo-Processamento-Provas/Verifica-Thales"
WORKING_FOLDER="/home/provas/tmp"

#Opcoes de comando
ACTION="cp -n"
FORCED_ACTION="cp -f"
MOVE_ACTION="mv"
#yes or empty - preenchido automaticamente com base nos argumentos passados - Não implementado
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
#Inicio das rotinas
	for lista in $( find ${PATH_ORIGEM} -iname '*png' );
	do
		case "${lista}" in
			*XXXXXXX*|*YYYYYYY*|*ZZZZZZZ*)
				#Limbo eh um problema, quando aparece sempre deve ser reportado
				echo "Prova - ${lista} - movida para o Limbo."
				${ACTION} "${lista}" ${PATH_LIMBO}
				;;
			*20190417*|*20190418*|*20190422*|*20190423*|*20190424*|*20190425*|*20190426*|*20190427*|*20190429*|*20190502*|*20190509*|*20190512*)

				echo "Detectei prova do 1o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_1BIM2019}/${2}"
				
				${ACTION} "${lista}" ${PATH_PROVAS_1BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_1BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_1BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 37 -e
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
				
				;;
			*20190626*|*20190627*|*20190701*|*20190702*|*20190703*|*20190704*|*20190705*|*20190706*|*20190711*|*20190712*|*20190714*)

				echo "Detectei prova do 2o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_2BIM2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_2BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_2BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_2BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 38 -e
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
				
				;;
			*20190610*|*20190611*|*20190612*|*20190617*|*20190619*|*20190623*)

				echo "Detectei prova do DP 1 Semestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_1DP2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_1DP2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_1DP2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_1DP2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 39 -t dp -e
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
				
				;;
			*20190819*|*20190820*|*20190821*|*20190822*|*20190823*|*20190829*|*20190901*)

				echo "Detectei prova Exame 1o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_1BIM2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_EXAME_1BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_EXAME_1BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_EXAME_1BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 37 -t exam -e
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
				
				;;
			*20190909*|*20190910*|*20190911*|*20190912*|*20190913*|*20190916*|*20190920*|*20190922*)

				echo "Detectei prova Exame 2o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_2BIM2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_EXAME_2BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_EXAME_2BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_EXAME_2BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 38 -t exam -e
						rm ${WORKING_FOLDER}/reverte_status.csv	
					fi
				fi
				
				;;
			*20191002*|*20191003*|*20191007*|*20191008*|*20191009*|*20191010*|*20191011*|*20191014*|*20191016*|*20191017*|*20191018*|*20191021*|*20191022*|*20191024*)

				echo "Detectei prova do 3o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_3BIM2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_3BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_3BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_3BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4}-${temp:9:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						#como regular e DP estão misturadas é necessário chutar qual é o registro correto
						#echo "Atencao! Como os registros de DP e regular do 3BIM2019 estao misturados eh normal que um dos procedimentos falhe e o outro funcione"
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 44 -e 2> /dev/null
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 46 -t dp -e 2> /dev/null
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
				
				;;
			*20191204*|*20191205*|*20191207*|*20191209*|*20191210*|*20191211*|*20191212*|*20191213*|*20191214*|*20191218*|*20191219*|*20191220*|*20191222*|*20200303*"STA001"*|*20200305*"EMA002"*)
				
				echo "Detectei prova do 4o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_4BIM2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_4BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_4BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_4BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4}-${temp:9:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						#como regular e DP estão misturadas é necessário chutar qual é o registro correto
						#echo "Atencao! Como os registros de DP e regular estao misturados eh normal que um dos procedimentos falhe e o outro funcione"
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 45 -e 2> /dev/null
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 47 -t dp -e 2> /dev/null
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
				
				;;
			*20200205*|*20200206*|*20200207*)
				
				echo "Detectei prova de Exame do 3o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_3BIM2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_EXAME_3BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_EXAME_3BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_EXAME_3BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4}-${temp:9:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						#como regular e DP estão misturadas é necessário chutar qual é o registro correto
						#echo "Atencao! Como os registros de DP e regular estao misturados eh normal que um dos procedimentos falhe e o outro funcione"
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 44 -t exam -e 2> /dev/null
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 46 -t exam -e 2> /dev/null
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
				
				;;
			*20200212*|*20200213*|*20200214*)
				
				echo "Detectei prova de Exame do 4o bimestre 2019 - ${ACTION} ${lista} ${PATH_PROVAS_EXAME_4BIM2019}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_EXAME_4BIM2019}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_EXAME_4BIM2019}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_EXAME_4BIM2019}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4}-${temp:9:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						#como regular e DP estão misturadas é necessário chutar qual é o registro correto
						#echo "Atencao! Como os registros de DP e regular estao misturados eh normal que um dos procedimentos falhe e o outro funcione"
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 45 -t exam -e 2> /dev/null
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 47 -t exam -e 2> /dev/null
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
				fi
			
				;;			
			*20200302*|*20200303*|*20200304*|*20200305*|*20200306*)
			
				echo "Detectei prova do DP 1 Semestre 2020 - ${ACTION} ${lista} ${PATH_PROVAS_1DP2020}/${2}"

				${ACTION} "${lista}" ${PATH_PROVAS_1DP2020}/${2}
				
				#Limpa os arquivos do servidor para que seja novamente corrigido
				if [[ "$3" == "-f" ]]; then
					temp="${lista##*/}"
					temp="${temp%.*}"
					rm ${PATH_PROVAS_1DP2020}/${2}/result/${temp}.txt 2> /dev/null
					rm ${PATH_PROVAS_1DP2020}/${2}/${temp}.csv 2> /dev/null
					
					if [[ $temp != *"ocorrencia"* ]] && [[ $temp != *"presenca"* ]] && [[ $temp != *"oficio"* ]];then
						#reverte o status de ausente, anulada e ilegível
						echo -e "${temp:0:8},${temp:9:4},${temp:14:6},${temp:21:4},${temp:26:7}" > ${WORKING_FOLDER}/reverte_status.csv
						~/src/sgaPresentes.py -a ${WORKING_FOLDER}/reverte_status.csv -c 48 -t dp -e
						rm ${WORKING_FOLDER}/reverte_status.csv
					fi
					
					#Fix para aplicacao de dois tipos de calendarios na mesma data
					if [[ $lista == *20200303*"ocorrencia"* ]] || [[ $lista == *20200305*"ocorrencia"* ]];then
						${ACTION} "${lista}" ${PATH_PROVAS_1DP2020}/${2}
					if
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
