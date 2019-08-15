#!/bin/bash
#Script Zera todas as pendencias do 1BIM2019

echo "Zerando todas as pendencias do DashBoard - 1 Bimestre 2019"

for a in `seq -f "%04.0f" 0 336`
do 
  ~/src/incluiFolhasFaltantes.py -e ~/dados/SGA/db/todasProvasJuntas.csv -p ~/dados/SGA/provas/ -n $a
  echo "Polo: "$a "Zerado."
done
