#!/bin/bash
echo "Iniciando o processamento de Correção 2 Bimestre de 2019"
echo "Executando o rodaScannerME, aguarde o processamento..."
~/src/rodaScannerME.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -p Saida/
echo "Executando converte, aguarde o processamento..."
~/src/converte.py -e Saida/ -s ausentes.csv
echo "Executando rodaLeitorPresenca, aguarde o processamento..."
~/src/rodaLeitorPresenca.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -a ausentes.csv -p Saida/
echo "Executando distribuiFolhasAusentes, aguarde o processamento..."
~/src/distribuiFolhasAusentes.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -a ausentes.csv -p Saida/
echo "Executando corrigeME, aguarde o processamento..."
~/src/corrigeME-20190717.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -g ~/dados/gdrive_rclone/2_bimestre/origem/csv/GabaritoMultiplasEscolhas-2BIM-2019.csv -a Saida/ -s notas.csv
echo "acessando a pasta de Saida..."
cd Saida/
echo "Copiando as provas de ausentes para o servidor..."
~/src/copiamantem-2BIM2019.sh
