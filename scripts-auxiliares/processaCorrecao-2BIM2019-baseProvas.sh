#!/bin/bash
echo "Iniciando o processamento de CorreÃ§Ã£o 2 Bimestre de 2019"

cd ~/dados/SGA/provas_2_bimestre/
#~/dados/tmp/srcTMP/remove-csv-txt.sh
echo "Executando o rodaScannerME, aguarde o processamento..."
~/src/rodaScannerME.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -p ~/dados/SGA/provas_2_bimestre/
echo "Executando converte, aguarde o processamento..."
~/src/converte.py -e ~/dados/SGA/provas_2_bimestre/ -s ausentes.csv
echo "Executando rodaLeitorPresenca, aguarde o processamento..."
~/src/rodaLeitorPresenca.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -a ausentes.csv -p ~/dados/SGA/provas_2_bimestre/
echo "Executando distribuiFolhasAusentes, aguarde o processamento..."
#~/src/distribuiFolhasAusentes.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -a ausentes.csv -p ~/dados/SGA/provas_2_bimestre/
echo "Organizando as provas de ausentes no servidor..."
~/src/distribuiPorPolos.sh
echo "Executando corrigeME, aguarde o processamento..."
~/src/corrigeME-20190717.py -e ~/dados/gdrive_rclone/2_bimestre/origem/csv/todasProvasJuntas.csv -g ~/dados/gdrive_rclone/2_bimestre/origem/csv/GabaritoMultiplasEscolhas-2BIM-2019.csv -a ~/dados/SGA/provas_2_bimestre/ -s notas.csv
echo "Provas Corrigidas"
echo "Script processaCorreção 2 Bimestre de 2019 finalizado"
