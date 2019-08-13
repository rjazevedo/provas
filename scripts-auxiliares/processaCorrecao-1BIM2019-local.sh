#!/bin/bash
echo "Executando o rodaScannerME, aguarde o processamento..."
~/src/rodaScannerME.py -e ~/dados/SGA/db/todasProvasJuntas.csv -p Saida/
echo "Executando converte, aguarde o processamento..."
~/src/converte.py -e Saida/ -s ausentes.csv
echo "Executando rodaLeitorPresenca, aguarde o processamento..."
~/src/rodaLeitorPresenca.py -e ~/dados/SGA/db/todasProvasJuntas.csv -a ausentes.csv -p Saida/
echo "Executando distribuiFolhasAusentes, aguarde o processamento..."
~/src/distribuiFolhasAusentes.py -e ~/dados/SGA/db/todasProvasJuntas.csv -a ausentes.csv -p Saida/
echo "Executando corrigeME, aguarde o processamento..."
~/src/corrigeME.py -e ~/dados/SGA/db/todasProvasJuntas.csv -g ~/dados/SGA/db/GabaritoMultiplasEscolhas.csv -a Saida/ -s notas.csv
echo "acessando a pasta de Saida..."
cd Saida/
echo "Copiando as provas para o servidor..."
~/src/copiamantem-1BIM2019.sh
