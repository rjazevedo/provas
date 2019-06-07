#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Recupera os arquivos perdidos da pasta de snapshot que não foram lidos automaticamente"""

import os
import argparse
import csv
import sys
from utils import BuscaArquivos, LinhaProva, Arquivos2Dict
import shutil

def QuebraNome(nome):
    campos = os.path.basename(nome).split('-')
    if len(campos) == 6:
        return [campos[1], campos[2], campos[3], campos[4]]
    else:
        return ['', '', '', '']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Recupera os arquivos perdidos da pasta de snapshot que não foram lidos automaticamente e que estão nomeados com o padrão correto.')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Pasta de entrada (snapshot)')
    parser.add_argument('-d', '--dados', type=str, required=True, help='Arquivo informações sobre as provas')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Pasta de provas (saida)')
    parser.add_argument('-t', '--teste', action='store_true', required=False, help='Testa a execução (não executa nada)')

    args = parser.parse_args()

    arquivos = BuscaArquivos(args.entrada, recursivo = True, tipo = '.png')
    entrada = Arquivos2Dict(arquivos)
    print(len(arquivos), 'arquivos a processar')

    arquivos = BuscaArquivos(args.saida, recursivo = True, tipo = '.png')
    saida = Arquivos2Dict(arquivos)

    provas = csv.reader(open(args.dados))
    next(provas)
    provas = [LinhaProva(a) for a in provas]

    contagem = 0
    for p in provas:
        for folha in p.idPaginas():
            # Folha não está na pasta de provas mas tem um arquivo com o nome correto na pasta de entrada
            if folha in entrada and not folha in saida:
                contagem += 1
                print(entrada[folha], '==>', args.saida)
                if not args.teste:
                    shutil.copyfile(entrada[folha], os.path.join(args.saida, folha + '.png'))

    print(contagem, 'arquivos encontrados')