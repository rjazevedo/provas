#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Verifica se os múltiplos leitores concordam com a mesma resposta da imagem"""

import os
import argparse
import csv
import sys
from utils import BuscaArquivos


def Compara(arquivoCSV, arquivoTXT):
    respostaCSV = list(csv.reader(open(arquivoCSV)))
    tmpTXT = open(arquivoTXT).readlines()

    if len(respostaCSV) != len(tmpTXT):
        print('Tamanhos diferentes:', len(respostaCSV), len(tmpTXT))
    else:
        respostaTXT = [x.split('. ') for x in tmpTXT]

        for i in range(0, len(respostaTXT)):
            if respostaCSV[i][1][0] != respostaTXT[i][1][0]:
                print('Respostas diferentes para questão:', i, respostaCSV[i][1], respostaTXT[i][1])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Verifica se os múltiplos leitores concordam com as respostas das questões de múltipla escolha')
    parser.add_argument('-1', '--corretor1', type=str, required=True, help='Pasta com as respostas do corretor 1 (CSV)')
    parser.add_argument('-2', '--corretor2', type=str, required=True, help='Pasta com as respostas do corretor 2 (TXT)')

    args = parser.parse_args()

    l1 = BuscaArquivos(args.corretor1, recursivo=False, tipo='.csv')
    l2 = BuscaArquivos(args.corretor2, recursivo=True, tipo='.txt')

    print(len(l1), len(l2))

    dadosCSV = {}
    for arquivo in l1:
        dadosCSV[os.path.basename(arquivo)[:-4]] = arquivo

    dadosTXT = {}
    for arquivo in l2:
        dadosTXT[os.path.basename(arquivo)[:-4]] = arquivo

    for arquivo in dadosTXT.keys():
        print(arquivo)
        if arquivo in dadosCSV:
            Compara(dadosCSV[arquivo], dadosTXT[arquivo])    