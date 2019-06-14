#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Verifica se os múltiplos leitores concordam com a mesma resposta da imagem"""

import os
import argparse
import csv
import sys
from utils import BuscaArquivos


def QuebraNome(nome):
    campos = os.path.basename(nome).split('-')
    if len(campos) == 6:
        return campos
    else:
        return ['', '', '', '', '', '']


def ConverteTXT2CSV(nome, ausentes):
    dados = open(nome).readlines()

    arquivoResposta = os.path.join(os.path.dirname(os.path.dirname(nome)), os.path.basename(nome)[:-4] + '.csv')
    if len(dados) == 1 and dados[0].startswith('Ausente'):
        campos = QuebraNome(nome)
        ausentes.append(campos[0:5])
        if campos[2].startswith('LIN'):   # 6 questões
            resposta = '1,_\n2,_\n3,_\n4,_\n5,_\n6,_\n'
        else:
            resposta = '1,_\n2,_\n3,_\n4,_\n'

        open(arquivoResposta, 'wt').writelines(resposta)
    else:
        resposta = [x[:-1].split('. ') for x in dados]
        csv.writer(open(arquivoResposta, 'wt')).writerows(resposta)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Converte os arquivos de leitura de múltipla escolha de .txt para .csv')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Pasta com os arquivos de entrada')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Arquivo com informações sobre os ausentes')

    args = parser.parse_args()

    txt = BuscaArquivos(args.entrada, recursivo=True, tipo='.txt')
    ausentes = []

    for arquivo in txt:
        print(arquivo)
        if not '-presenca-' in arquivo:
            ConverteTXT2CSV(arquivo, ausentes)

    csv.writer(open(args.saida, 'wt')).writerows(ausentes)
