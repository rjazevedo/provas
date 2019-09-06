#!/bin/bash

# Executar:
# 
# nohup ./fileListenerAndProcessorParam.sh 131 145 > nohup1.out &

# diretorio base
HOME="/home/provas/dados"

# origem dos dados no google drive
ORIGDIR="gdrive_rclone/2_bimestre"

# destino na nuvem da Univesp (repositorio definitivo)
DESTDIR="fileListener"

# diretorio para salvamento do resultado do processamento feito por decodeqr.py
SAVEDIR="fileListener/provas"

#Caminho parcial para provas destino final servidor
PATH_PROVAS="SGA/provas_2_bimestre"

# diretorio temporario para execucao de decodeqr.py nos novos arquivos
TMPDIR="fileListener/tmp${1}-${2}"

# refugo
REFUGODIR="fileListener/refugo"

# copia arquivo caso nao exista na VM Univesp, ou esteja mais novo no gdrive
# executa decodeqr.py para este arquivo apenas

copy_file_and_execute_decodeqr()
{
  orig="$1"
  dest="$2"
  polo="$3"
  filename="$4"
  
  echo "Copiando novo arquivo: polo ${polo}: ${filename}"

  cp -p "${orig}" "${dest}"
  
  rm -rf ${HOME}/${TMPDIR}/aux/*
  cp "${dest}" ${HOME}/${TMPDIR}/aux
  
  echo "Executando decodeqr.py: polo ${polo}: ${filename}"
  decodeqr.py -e ${HOME}/${TMPDIR}/aux \
              -t ${HOME}/${TMPDIR}/trabalho \
              -s ${HOME}/${SAVEDIR}/${polo} \
              -r ${HOME}/${REFUGODIR}/${polo}

  ##################
  # script do Daniel (adaptado por Guilherme, 6/8/2019)
  echo "Copiando para pasta final"
  cp -n ${HOME}/${SAVEDIR}/${polo}/*  ${HOME}/${PATH_PROVAS}/${polo}
  ##################
}

# percorre subdiretorios recursivamente no gdrive, a partir de Upload

traverse_dir()
{
  for i in "$1"/*
  do
    if [ -d "$i" ]
    then
      b="${i##*/}"
      s="$2/${b}"
      if [ "$2" = "" ]
      then
        s="${b}"
      fi      
      traverse_dir "$i" "$s" "$3"
    elif [ -f "$i" ]
    then
      # filtra por tipo
      ext="${i: -4}"
      ext=$(echo "${ext}" | tr '[:upper:]' '[:lower:]')

      orig="$i"
      polo="$3"
      filename="${orig##*/}"
      basedir="$2"
      dir="${HOME}/${DESTDIR}/${polo}/${basedir}"
      dest="${HOME}/${DESTDIR}/${polo}/${basedir}/${filename}"

      mkdir -p "${dir}"

      # copia apenas novos arquivos
      if [ "${orig}" -nt "${dest}" ]
      then
        if [ "${ext}" = ".pdf" ] || [ "${ext}" = ".png" ] || [ "${ext}" = ".jpg" ]
        then
          copy_file_and_execute_decodeqr "${orig}" "${dest}" "${polo}" "${filename}"
        else # apenas copia arquivos .zip e demais extensões, fazendo log
          cp -p "${orig}" "${dest}"
          echo "EXT: copiando arquivo espúrio, ${polo}: ${filename}"
        fi
      fi
    fi
  done
}

# ad infinitum

echo "Escutando... "

mkdir -p ${HOME}/${TMPDIR}/aux
mkdir -p ${HOME}/${TMPDIR}/trabalho

while true
do
  echo $(date)

  # copia novos arquivos do gdrive para VM Univesp:

  for polo in $(seq -f "%04.0f" $1 $2)
  do
    for orig in ${HOME}/${ORIGDIR}/${polo}-*/Upload
    do
      traverse_dir "$orig" "" "$polo"
    done
  done
  
  echo "************** dormindo *****************"
  # dorme por 10 minutos
  sleep 600
done

# sketchbook:
#
# basedir=${o%/*}
# lastdir=${basedir##*/}
