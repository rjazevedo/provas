#!/bin/bash
#Objetivo:Esse script tem como objetivo converter um arquivo linux para excel
#Autor: Daniel Consiglieri
#Data:30-ago-2019
#Modificado:06-dez-2019
#usar encguess nas versoes futuras

#**Inicialiazacao de Variaveis**#
FORMATO_ENTRADA="utf-8"
FORMATO_SAIDA="iso-8859-1"

sed -i "s#,#;#g" ${1}
iconv -f ${FORMATO_ENTRADA} -t ${FORMATO_SAIDA} ${1} > tmp_${1}
cp ${1} ${1}.bkp
mv tmp_${1} ${1}



