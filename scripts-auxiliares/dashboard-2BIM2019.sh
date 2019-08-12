#!/bin/bash
#Descricao: Script que gera Dashboard do 2 Bimestre
#Autor: Daniel Consiglieri
#Data Criacao:Jun 2019
#Revisao:
cd ~/tmp
mkdir d2BIM2019
echo "Inicio da geração do DashBoard - 2 Bimestre 2019"
~/src/dashboard.py -e ~/dados/SGA/provas_2_bimestre -p ~/dados/gdrive_rclone/2_bimestre/origem/csv/dashboard-2BIM-2019.csv -s ~/tmp/d2BIM2019 -a ~/dados/SGA/provas_2_bimestre/ausentes.csv
cd ~/tmp/d2BIM2019
cp -f *.html ~/dados/SGA/dashboard/2bim
cd ~/tmp
rm -rf d2BIM2019
