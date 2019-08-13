#!/bin/bash
#Processa decoder em sequencia de todos os arquivos com inicio 0 
#Autor:Daniel Consiglieri
#Data:19-jul-2019
echo "Bem vindo ao processador de lotes decoder 1 Bimestre 2019\n"
echo "Localizando pastas com que comecam com o caracter 0"
for a in 0*;
do echo $a;
	cd $a;
	~/scr/scripts-auxiliares/decoder-1BIM2019.sh;
	cd ..;
	echo "Processado";
done
