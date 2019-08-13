#!/bin/bash
#Subrotina do programa:Programa alternativo de decoder para pastas Locais
#Autor:Daniel Consiglieri
#Data:07-ago-2019
#Revisao: 13-ago-2019

#**Inicialiazacao de Variaveis**#
#Diretorio de Home
HOME="/home/provas"
#**Fim de variáveis de parametrizacao**#

echo "Seja bem-vindo ao alternative decoder local"
echo "Atencao!!! esse programa deve rodar dentro da configuração preparada, (rodar preparaEstrutura.sh antes)"
#Essa linha localiza todos os pdfs e os quebras e apaga os PDFs
echo "Quebrando os PDFs..."
#Busca os arquivos PDFs efetua a quebra depois os remove
find  -iname \*.pdf -exec pdfimages {} {} -png \; -exec rm {} \; -exec echo "Pdf desmembrado: "{} \;
echo "Executando o decodeqr apos o quebra alternativa de PDF"
${HOME}/src/decodeqr.py -e Provas/ -t Trabalho/ -s Saida/ -r Refugo
#procedimento para verificar se pasta é vazia
ls Refugo 2> /dev/null
#Se pasta nao vazia efetua a repescagem de arquivos anomalos
if [ $? -ne 0 ]
then
	cd Refugo/
	#Entra no refugo para tratar casos anomalos em que a imagem ficou espelhada
	for a in *.png;
	do
		convert -flop $a $a
		echo "Corrigindo o arquivo"$a
	done;
	mkdir Refugo2
	cd -
	echo "Mais uma tentativa de recuperar Provas"
	${HOME}/src/decodeqr.py -e Refugo/ -t Trabalho/ -s Saida/ -r Refugo/Refugo2
fi
echo "Fim do alternative decoder"