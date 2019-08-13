#!/bin/bash

echo "Inicio da leitura do decoder"
~/src/decodeqr.py -e Provas/ -t Trabalho/ -s Saida/ -r Refugo
echo "acessando a pasta de Saida..."
cd Saida/
echo "Criando todos os diretorios"
~/src/criaDirPolos.sh
echo "Distribuindo as provas nos diretorios correspondete"
~/src/distribuiPorPolos.sh
echo "Copiando as provas para o servidor..."
~/src/copiamantem-1BIM2019.sh
echo "Gerando um novo dashboard"
~/scr/scripts-auxiliares/dashboard-1BIM2019.sh
