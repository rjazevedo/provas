#!/bin/bash
#Objetivo: Esse script gera as saídas necessárias para os arquivos de csv para subir no Banco de dados os corretores-2BIM-2019
#Autor:Daniel Consiglieri
#Criação:Junho 2019

echo "Inicio da geração do PopulaDB - 2 Bimestre"
~/src/populaDB.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -b ~/dados/gdrive_rclone/2_bimestre/origem/csv/baseCorrecoes-2BIM-2019.csv -c ~/dados/gdrive_rclone/2_bimestre/origem/csv/corretores-2BIM-2019.csv -a ~/dados/SGA/provas_2_bimestre/ -g ~/dados/SGA/guias_2_bimestre_2019 -s ~/dados/SGA/provas_2_bimestre/Saida/