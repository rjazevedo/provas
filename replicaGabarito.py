#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Corrige questões de Múltipla Escolha"""

import csv
import sys
import argparse
import os

NUMERO_POLOS=337


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Replica gabaritos de múltipla escolha para todos os polos')
    parser.add_argument('-g', '--gabarito', type=str, required=True, help='Arquivo de entrada com a descrição dos gabaritos sem identificação dos polos')
    parser.add_argument("-f", "--forca", required=False, action='store_true', help="Força a escrita no arquivo de saída se ele existir")

    args = parser.parse_args()

    print('Lendo entrada...')
    gabaritos = list(csv.reader(open(args.gabarito)))[1:]

    # Pasta onde estão os gabaritos
    baseGabarito = os.path.dirname(args.gabarito)

    for gabarito in gabaritos:
        disciplina = gabarito[0]
        prova = gabarito[1]
        resto = gabarito[2:]
        print(disciplina, prova)
        
        resposta = []
        for polo in range(0, NUMERO_POLOS):
            linha = [disciplina, '{0}-{1:04d}'.format(prova, polo)]
            linha.extend(resto)
            resposta.append(linha)
            
        nomeArquivo = os.path.join(baseGabarito, 'gabarito-{0}-{1}.csv'.format(disciplina, prova))
        if not os.path.isfile(nomeArquivo) or args.forca:
            print('Gravando', nomeArquivo)
            saida = csv.writer(open(nomeArquivo, 'wt'))
            saida.writerows(resposta)
        else:
            print(nomeArquivo, 'já existe, não foi regravado.')


