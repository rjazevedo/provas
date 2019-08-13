#!/bin/bash
echo "Iniciando o processamento de CorreÃ§Ã£o 1 Bimestre de 2019"
echo "Executando o rodaScannerME, aguarde o processamento..."
~/src/rodaScannerME.py -e ~/dados/SGA/db/todasProvasJuntas.csv -p ~/dados/SGA/provas/
echo "Executando converte, aguarde o processamento..."
~/src/converte.py -e ~/dados/SGA/provas/ -s ausentes.csv
echo "Executando rodaLeitorPresenca, aguarde o processamento..."
#~/src/rodaLeitorPresenca.py -e ~/dados/SGA/db/todasProvasJuntas.csv -a ausentes.csv -p ~/dados/SGA/provas/
echo "Executando distribuiFolhasAusentes, aguarde o processamento..."
#~/src/distribuiFolhasAusentes.py -e ~/dados/SGA/db/todasProvasJuntas.csv -a ausentes.csv -p ~/dados/SGA/provas/
echo "Organizando as provas de ausentes no servidor..."
#~/src/distribuiPorPolos.sh
echo "Executando corrigeME-modificado com as alteracoes de gabarito, aguarde o processamento..."
#~/src/corrigeME.py -e ~/dados/SGA/db/todasProvasJuntas.csv -g ~/dados/SGA/db/GabaritoMultiplasEscolhas.csv -a ~/dados/SGA/provas/ -s notas.csv
~/src/corrigeME-20190717.py -e ~/dados/SGA/db/todasProvasJuntas.csv -g ~/dados/SGA/db/beta.csv -a ~/dados/SGA/provas/ -s notas.csv
echo "Provas corrigidas..."
echo "Script processaCorreção 1 Bimestre de 2019 finalizado"

