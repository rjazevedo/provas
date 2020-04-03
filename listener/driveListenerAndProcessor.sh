#!/bin/bash
#Objetivo: Esse script eh um listener para pastas do Drive de processamento Manual - Versao Beta
#Esse script depende de move_arquivos.sh e alternative-decoder-local.sh
#Autor: Daniel Consiglieri
#Data Criacao:Out 2019
#Revisao:03-jan-2020
#Observacao: Caso alterar numero de polos, repreparar a estrutura e alterar os loops

#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
ESTRUTURA_PROCESSAMENTO="/home/provas/dados/DriveListener/png_renomeados"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Path para Home
HOME="/home/provas"
PATH_MONITORAMENTO_PNG="/home/provas/dados/gdrive_rclone/Nucleo-Processamento-Provas/Png-Remomeados-COPIA-FORCADA"
PATH_MONITORAMENTO_PDF_PASSIVO="/home/provas/dados/gdrive_rclone/Nucleo-Processamento-Provas/Pdf-COPIA-PASSIVA"
PATH_MONITORAMENTO_PDF_FORCADO="/home/provas/dados/gdrive_rclone/Nucleo-Processamento-Provas/Pdf-COPIA-FORCADA"
PATH_LOG="/home/provas/dados/gdrive_rclone/Nucleo-Processamento-Provas"
PATH_DESTINO_PNG="/home/provas/dados/DriveListener/Referencia/Png-Remomeados-COPIA-FORCADA"
PATH_DESTINO_PDF_PASSIVO="/home/provas/dados/DriveListener/Referencia/Pdf-COPIA-PASSIVA"
PATH_DESTINO_PDF_FORCADO="/home/provas/dados/DriveListener/Referencia/Pdf-COPIA-FORCADA"
POLOS=400

TEMPO_PAUSA=900
###Fim Variáveis globais


echo "Iniciando ..."

while true
do
	echo $(date)
	find ${PATH_MONITORAMENTO_PNG} -type f -iname '*.png' | while read i
	do
		
		if [[ ! -z "$i" ]]
		then	
			
			#Criação de Log de processamento
			DATA=$(date +%Y%m%d)
			b="${i##*/}"
			
			# copia apenas novos arquivos
			
			if [ "${PATH_MONITORAMENTO_PNG}/${b}" -nt "${PATH_DESTINO_PNG}/${b}" ]
			then
				
				echo "Lendo o arquivo  : $i"
				
				cat ${PATH_LOG}/log_copiaForcadaPNG.csv > ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaForcadaPNG.csv
				echo -e "$b,Processado,$DATA" >> ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaForcadaPNG.csv
				
				mv ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaForcadaPNG.csv ${PATH_LOG}/log_copiaForcadaPNG.csv
			
				cp -n "${i}" "${ESTRUTURA_PROCESSAMENTO}"/Saida
				
				cd	 ${ESTRUTURA_PROCESSAMENTO}/Saida
				
				normaliza=${b// /_}
				
				convert -quality 100 -density 150 -fill white -fuzz 80% +opaque black -antialias ${ESTRUTURA_PROCESSAMENTO}/Saida/"${b}" ${ESTRUTURA_PROCESSAMENTO}/Saida/"${normaliza}"
				
				if [[ "${normaliza}" != "${b}" ]]
				then
					rm ${ESTRUTURA_PROCESSAMENTO}/Saida/"${b}"
				fi
				
				#Move os arquivos dentro das sub-pastas
				for a in `seq -f "%04.0f" 0 $POLOS`
				do 
				  mv *-$a-* $a 2> /dev/null
				done
				
				#Organiza arquivos processados por data de upload
				DATA_BACKUP=$(date +%Y%m%d)
				mkdir -p ${ESTRUTURA_PROCESSAMENTO}/Processado/${DATA_BACKUP}

				#Move arquivos no local de provas correspondente
				for a in 0*;
				do
					${HOME}/src/listener/move_arquivos.sh "${ESTRUTURA_PROCESSAMENTO}/Saida/${a}" "${a}" "-f"
					
					#Verifica se o diretorio contem arquivo
					[ "$( ls -A ${ESTRUTURA_PROCESSAMENTO}/Saida/${a} )" ] && \
					mv ${ESTRUTURA_PROCESSAMENTO}/Saida/${a}/* ${ESTRUTURA_PROCESSAMENTO}/Processado/${DATA_BACKUP}
				done

				#Copia para a pasta de referencia
				cp -p "${PATH_MONITORAMENTO_PNG}/${b}" "${PATH_DESTINO_PNG}/${b}"
				
			fi
		fi
	done

#Verificacao da Pasta PDF Passivo

	find ${PATH_MONITORAMENTO_PDF_PASSIVO} -type f -iname '*.pdf' | while read i
	do
	
		if [[ ! -z "$i" ]]
		then
			
			#Criação de Log de processamento
			DATA=$(date +%Y%m%d)
			b="${i##*/}"
			
			if [ "${PATH_MONITORAMENTO_PDF_PASSIVO}/${b}" -nt "${PATH_DESTINO_PDF_PASSIVO}/${b}" ]
			then
				
				cp -n "${i}" "${ESTRUTURA_PROCESSAMENTO}"/Provas
				
				cd ${ESTRUTURA_PROCESSAMENTO}
				${HOME}/src/scripts-auxiliares/alternative-decoder-local.sh
				
				DATA=$(date +%Y%m%d)
				
				#arquivo de log de processados
				cat ${PATH_LOG}/log_copiaPassivaPDF.csv > ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaPassivaPDF.csv
				for j in $( find ${ESTRUTURA_PROCESSAMENTO}/Saida -maxdepth 1 -iname '*.png' ) ; do
					bj="${j##*/}"
					echo "Copiando o arquivo  : $j"
					
					echo -e "$b,$bj,Processado,$DATA" >> ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaPassivaPDF.csv
				done
				#Salva o log no Drive
				mv ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaPassivaPDF.csv ${PATH_LOG}/log_copiaPassivaPDF.csv
			   
				#Move os arquivos dentro das sub-pastas
				cd	 ${ESTRUTURA_PROCESSAMENTO}/Saida
				for a in `seq -f "%04.0f" 0 $POLOS`
				do 
				  mv *-$a-* $a 2> /dev/null
				done

				#Organiza arquivos processados por data de upload
				DATA_BACKUP=$(date +%Y%m%d)
				mkdir -p ${ESTRUTURA_PROCESSAMENTO}/Processado/${DATA_BACKUP}

				#Move arquivos no local de provas correspondente
				for a in 0*;
				do
					${HOME}/src/listener/move_arquivos.sh "${ESTRUTURA_PROCESSAMENTO}/Saida/${a}" "${a}"
					
					#Verifica se o diretorio contem arquivo
					[ "$( ls -A ${ESTRUTURA_PROCESSAMENTO}/Saida/${a} )" ] && \
					mv ${ESTRUTURA_PROCESSAMENTO}/Saida/${a}/* ${ESTRUTURA_PROCESSAMENTO}/Processado/${DATA_BACKUP}
				done
				rm -rf ${ESTRUTURA_PROCESSAMENTO}/Provas
				mkdir -p ${ESTRUTURA_PROCESSAMENTO}/Provas
				#Copia para a pasta de referencia
				cp -p "${PATH_MONITORAMENTO_PDF_PASSIVO}/${b}" "${PATH_DESTINO_PDF_PASSIVO}/${b}"
				
			fi
		fi
	done

#Verificacao da Pasta PDF Ativo

	find ${PATH_MONITORAMENTO_PDF_FORCADO} -type f -iname '*.pdf' | while read i
	do
		if [[ ! -z "$i" ]]
		then
			
			#Criação de Log de processamento
			DATA=$(date +%Y%m%d)
			b="${i##*/}"
			
			if [ "${PATH_MONITORAMENTO_PDF_FORCADO}/${b}" -nt "${PATH_DESTINO_PDF_FORCADO}/${b}" ]
			then
				
				cp -n "${i}" "${ESTRUTURA_PROCESSAMENTO}"/Provas
				
				cd ${ESTRUTURA_PROCESSAMENTO}
				${HOME}/src/scripts-auxiliares/alternative-decoder-local.sh
				
				DATA=$(date +%Y%m%d)
				
				#arquivo de log de processados
				cat ${PATH_LOG}/log_copiaForcadaPDF.csv > ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaForcadaPDF.csv
				for j in $( find ${ESTRUTURA_PROCESSAMENTO}/Saida -maxdepth 1 -iname '*.png' ) ; do
					bj="${j##*/}"
					echo "Copiando o arquivo  : $j"
					echo -e "$b,$bj,Processado,$DATA" >> ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaForcadaPDF.csv
				done
				#Salva o log no Drive
				mv ${ESTRUTURA_PROCESSAMENTO}/tmp_log_copiaForcadaPDF.csv ${PATH_LOG}/log_copiaForcadaPDF.csv
			   
			   
				#Move os arquivos dentro das sub-pastas
				cd	 ${ESTRUTURA_PROCESSAMENTO}/Saida
				for a in `seq -f "%04.0f" 0 $POLOS`
				do 
				  mv *-$a-* $a 2> /dev/null
				done

				#Organiza arquivos processados por data de upload
				DATA_BACKUP=$(date +%Y%m%d)
				mkdir -p ${ESTRUTURA_PROCESSAMENTO}/Processado/${DATA_BACKUP}

				#Move arquivos no local de provas correspondente
				for a in 0*;
				do
					${HOME}/src/listener/move_arquivos.sh "${ESTRUTURA_PROCESSAMENTO}/Saida/${a}" "${a}" "-f"
					
					#Verifica se o diretorio contem arquivo
					[ "$( ls -A ${ESTRUTURA_PROCESSAMENTO}/Saida/${a} )" ] && \
					mv ${ESTRUTURA_PROCESSAMENTO}/Saida/${a}/* ${ESTRUTURA_PROCESSAMENTO}/Processado/${DATA_BACKUP}
				done
				rm -rf ${ESTRUTURA_PROCESSAMENTO}/Provas
				mkdir -p ${ESTRUTURA_PROCESSAMENTO}/Provas
				#Copia para a pasta de referencia
				cp -p "${PATH_MONITORAMENTO_PDF_FORCADO}/${b}" "${PATH_DESTINO_PDF_FORCADO}/${b}"
				
			fi
		fi
	done

	echo "************** dormindo *****************"
	sleep ${TEMPO_PAUSA}
done
