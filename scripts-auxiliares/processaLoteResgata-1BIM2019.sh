#!/bin/bash
#Copia em lote todas as pastas com o padrão de pasta iniciando com 1 
#Autor:Daniel Consiglieri
#Data:19-jul-2019
echo "Bem vindo ao processador de lotes decoder 1 Bimestre 2019\n"
echo "Localizando pastas com que comecam com o caracter 1"
for a in 1*;
do echo $a#;
	cd $a/Saida;
	~/src/copiamantem-1BIM2019.sh;
	echo "Processado";
	cd -;
done
