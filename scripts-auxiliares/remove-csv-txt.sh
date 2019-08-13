#!/bin/sh
#remove as correções antigas -Daniel Consiglieri

for a in 0*;
do echo $a;
	find ./$a/result/ -type f  -iname "*.txt" -exec rm '{}' \;
	find ./$a/ -type f  -iname "*.csv" -exec rm '{}' \;
	echo "Removendo correcoes";
done
