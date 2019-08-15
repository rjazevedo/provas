#!/bin/bash
#Script de segunda etapa que é a após o decoder, para processamento seme-automático
#Deve ser rodado a partir da Pasta mãe de todos os processamentos
#Data:05/08/2019

echo "acessando a pasta de Saida..."
cd Saida/
echo "Criando todos os diretorios"
~/src/criaDirPolos.sh
echo "Distribuindo as provas nos diretorios correspondete"
~/src/distribuiPorPolos.sh
echo "Copiando as provas para o servidor..."
~/src/copiamantem-2BIM2019.sh
