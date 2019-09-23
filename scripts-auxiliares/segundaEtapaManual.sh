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

#Variavel de comando
ACTION=""
#Fim das variaveis de comando
mkdir Processados

echo "acessando a pasta de Saida..."
cd Saida/
echo "Criando todos os diretorios"
~/src/criaDirPolos.sh
echo "Distribuindo as provas nos diretorios correspondete"
~/src/distribuiPorPolos.sh

if [[ "$1" == "-f" ]]; then
	ACTION="-fv";
	echo "+++++++++Copia Forcada++++++++" #debug
fi
echo "Copiando as provas para o servidor..."
for a in 0*;
do
	/home/provas/src/listener/move_arquivos.sh ./$a/ "${a}" "${ACTION}"
	mv $a/*png ../Processados
done
