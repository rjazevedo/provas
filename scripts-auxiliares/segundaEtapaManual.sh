#-not/bin/bash
#Script de segunda etapa que é a após o decoder, para processamento semi-automático
#Deve ser rodado a partir da Pasta mãe de todos os processamentos - Forca Bruta
#Data: 11-set-2019

#########################
#
#Para copiar caso não exista, nao eh necessario usar nenhum parametro
#Para copia forcada usar -f
#
###################


PATH_PROVAS_1BIM="/home/provas/dados/SGA/provas"
PATH_PROVAS_2BIM="/home/provas/dados/SGA/2019b2/provas"
PATH_PROVAS_1DP="/home/provas/dados/SGA/2019dp1/provas"
PATH_PROVAS_EXAME_1BIM="/home/provas/dados/SGA/2019e1/provas"
PATH_PROVAS_EXAME_2BIM="/home/provas/dados/SGA/2019e2/provas"
PATH_LIMBO="/home/provas/dados/tmp/Limbo"

#Opcoes de comando
ACTION="cp -n"
FORCED_ACTION="cp -f"
#Fim das opcoes de comando

mkdir Movidos_1BIM
mkdir Movidos_2BIM
mkdir Movidos_1DP
mkdir Movidos_Exame_1BIM
mkdir Movidos_Exame_2BIM

echo "acessando a pasta de Saida..."
cd Saida/
echo "Criando todos os diretorios"
~/src/criaDirPolos.sh
echo "Distribuindo as provas nos diretorios correspondete"
~/src/distribuiPorPolos.sh

if [[ "$1" == "-f" ]]; then
	ACTION=${FORCED_ACTION};
	echo "+++++++++Copia Forcada++++++++" #debug
fi
echo "Copiando as provas para o servidor..."
for a in 0*;
do
	#Provas Regulares Primeiro Bimestre
	find ./$a/ -type f  \( -iname '20190417*png' \
	-o -iname '20190418*png' \
	-o -iname '20190422*png' \
	-o -iname '20190423*png' \
	-o -iname '20190424*png' \
	-o -iname '20190425*png' \
	-o -iname '20190426*png' \
	-o -iname '20190427*png' \
	-o -iname '20190429*png' \
	-o -iname '20190502*png' \
	-o -iname '20190509*png' \) -exec ${ACTION} {} ${PATH_PROVAS_1BIM}/$a  \; -exec echo "Copiando " '{}' "para ${PATH_PROVAS_1BIM}/$a" \; -exec mv {} ../Movidos_1BIM \;
	#Provas Regulares Segundo Bimestre
	find ./$a/ -type f  \( -iname '20190626*png' \
	-o -iname '20190627*png' \
	-o -iname '20190701*png' \
	-o -iname '20190702*png' \
	-o -iname '20190703*png' \
	-o -iname '20190704*png' \
	-o -iname '20190705*png' \
	-o -iname '20190706*png' \
	-o -iname '20190711*png' \
	-o -iname '20190712*png' \) -exec ${ACTION} {} ${PATH_PROVAS_2BIM}/$a  \; -exec echo "Copiando " '{}' "para ${PATH_PROVAS_2BIM}/$a" \; -exec mv {} ../Movidos_2BIM \;
	#Prova 1DP
	find ./$a/ -type f  \( -iname '20190610*png' \
	-o -iname '20190611*png' \
	-o -iname '20190612*png' \
	-o -iname '20190617*png' \
	-o -iname '20190619*png' \) -exec ${ACTION} {} ${PATH_PROVAS_1DP}/$a  \; -exec echo "Copiando " '{}' "para ${PATH_PROVAS_1DP}/$a" \; -exec mv {} ../Movidos_1DP \;
	#Prova Exame 1o Bimestre
	find ./$a/ -type f  \( -iname '20190819*png' \
	-o -iname '20190820*png' \
	-o -iname '20190821*png' \
	-o -iname '20190822*png' \
	-o -iname '20190823*png' \
	-o -iname '20190829*png' \) -exec ${ACTION} {} ${PATH_PROVAS_EXAME_1BIM}/$a  \; -exec echo "Copiando " '{}' "para ${PATH_PROVAS_EXAME_1BIM}/$a" \; -exec mv {} ../Movidos_Exame_1BIM \;
	#Prova Exame 2o Bimestre
	find ./$a/ -type f  \( -iname '20190909*png' \
	-o -iname '20190910' \
	-o -iname '20190911' \
	-o -iname '20190912' \
	-o -iname '20190913' \
	-o -iname '20190916' \
	-o -iname '20190920' \) -exec ${ACTION} {} ${PATH_PROVAS_EXAME_2BIM}/$a  \; -exec echo "Copiando " '{}' "para ${PATH_PROVAS_EXAME_2BIM}/$a" \; -exec mv {} ../Movidos_Exame_2BIM \;
	#Arquivos Limbo, sao os que nenhum padrao foi encontrado
	find ./$a/ -type f -iname '*png' -exec ${ACTION} {} ${PATH_LIMBO}  \; -exec echo "Copiando Limbo" '{}' "para ${PATH_LIMBO}/" \;	-exec mv {} ${PATH_LIMBO} \;
done