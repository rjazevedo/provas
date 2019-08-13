#!/bin/bash
echo "Inicio da geração do PopulaDB - 1 Bimestre"
~/src/populaDB.py -e ~/dados/SGA/db/todasProvasJuntas.csv -b ~/dados/SGA/db/baseCorrecoes.csv -c ~/dados/SGA/db/corretores.csv -a ~/dados/SGA/provas/ -g ~/dados/SGA/guias/  -s ~/dados/SGA/provas/Saida/