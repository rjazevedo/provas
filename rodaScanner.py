#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Roda o scanner nos arquivos de folhas de prova de múltipla escolha"""
import os
import argparse
import csv
import sys
from utils import BuscaArquivos, LinhaProva, Arquivos2Dict
import shutil

CMD='/home/provas/folhasProvas/scanner/scanner -c '

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Roda o scanner nos arquivos de respostas de múltipla escolha.')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com descrição de todas as provas (.csv)')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Pasta com as provas')
    parser.add_argument('-t', '--teste', action='store_true', required=False, help='Testa a execução (não executa nada)')

    args = parser.parse_args()

    arquivos = BuscaArquivos(args.provas, recursivo = True, tipo = '.png')
    entrada = Arquivos2Dict(arquivos)
    print(len(arquivos), 'arquivos a verificar')

    provas = csv.reader(open(args.entrada))
    next(provas)
    provas = [LinhaProva(a) for a in provas]

    contagem = 0
    for p in provas:
        if p.questoesObjetivas != 0:
            folha = p.idPaginas()[0]

            # A folha .png tem que existir na pasta de entrada mas o arquivo .csv não pode existir
            if folha in entrada and not os.path.isfile(entrada[folha][:-4] + '.csv'):
                if args.teste:
                    print(CMD,  str(p.questoesObjetivas), entrada[folha])
                else:
                    os.system(CMD + ' ' + str(p.questoesObjetivas) + ' ' + entrada[folha])
                contagem += 1

    print(contagem, 'arquivos processados')
