#!/bin/bash
#Script de segunda etapa que é a após o decoder, para processamento seme-automático
#Deve ser rodado a partir da Pasta mãe de todos os processamentos
#Data:06-set-2019

FULL_PATH_PROVAS="/home/provas/dados/SGA/2019dp1/provas"

echo "acessando a pasta de Saida..."
cd Saida/
echo "Criando todos os diretorios"
~/src/criaDirPolos.sh
echo "Distribuindo as provas nos diretorios correspondete"
~/src/distribuiPorPolos.sh
echo "Copiando as provas para o servidor..."
for a in 0*;
do echo $a;
	find ./$a/ -type f  -iname "*.png" -exec cp -n '{}' ${FULL_PATH_PROVAS}/$a  \;
	echo "Copiando para pasta final ${FULL_PATH_PROVAS}/${a}";
done