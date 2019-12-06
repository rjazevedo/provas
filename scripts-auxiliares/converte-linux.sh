#!/bin/bash
#Objetivo:Esse script tem como objetivo converter um arquivo csv excel para linux utf-8 virgula
#Autor: Daniel Consiglieri
#Data:30-ago-2019
#Modificado:06-dez-2019
#usar encguess no futuro

#**Inicialiazacao de Variaveis**#
FORMATO_ENTRADA="iso-8859-1"
FORMATO_SAIDA="utf-8"

cp ${1} ${1}.bkp
sed -i "s#;#,#g" ${1}
iconv -f ${FORMATO_ENTRADA} -t ${FORMATO_SAIDA} ${1} > tmp_${1}
mv tmp_${1} ${1}



