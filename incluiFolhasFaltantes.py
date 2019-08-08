#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Remove Pendências de Folhas Faltantes dos Polos incluindo folhas em branco"""
import os
import argparse
import csv
import sys
from utils import BuscaArquivos, LinhaProva, Arquivos2Dict
import shutil
import functools


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Inclui folhas em branco nas provas incompletas dos polos, removendo as pendências. É preciso que alguma folha da prova esteja presente ou que a opção -f seja usada')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Arquivo de entrada com descrição de todas as provas (.csv)')
    parser.add_argument('-n', '--numeroPolo', type=str, required=True, help='Numero do polo a preencher as folhas ausentes (4 dígitos)')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Pasta com as provas')
    parser.add_argument('-d', '--disciplina', type=str, required=False, help='Processa somente a disciplina especificada')
    parser.add_argument('-a', '--aluno', type=str, required=False, help='Processa somente o aluno especificado')
    parser.add_argument('-t', '--teste', action='store_true', required=False, help='Testa a execução (não realiza as cópias nada)')
    parser.add_argument('-f', '--forcar', action='store_true', required=False, help='Força a criação das folhas quando não há nenhuma folha de uma prova')
    parser.add_argument('-v', '--verbose', action='store_true', required=False, help='Indica as folhas que foram incluidas')

    folhaBranca = os.path.join(os.path.dirname(sys.argv[0]), 'folha-nao-digitalizada.png')

    args = parser.parse_args()

    arquivos = BuscaArquivos(args.provas, recursivo = True, tipo = '.png')
    entrada = Arquivos2Dict(arquivos)
    print(len(arquivos), 'arquivos presentes')

    provas = csv.reader(open(args.entrada))
    next(provas)
    provas = [LinhaProva(a) for a in provas]
    print(len(provas), 'provas a verificar')

    contagem = 0

    for prova in provas:
        if prova.polo == args.numeroPolo:
            if args.disciplina is None or prova.disciplina == args.disciplina:
                if args.aluno is None or prova.ra == args.aluno:
                    paginas = prova.idPaginas()
                    presentes = [f in entrada for f in paginas]
                    temFolha = functools.reduce(lambda a, b: a or b, presentes)
                    if not temFolha and not args.forcar:
                        continue
                    for (folha, presente) in zip(paginas, presentes):
                        if not presente:
                            if args.teste:
                                print(folha)
                            else:
                                if args.verbose:
                                    print(folha)
                                shutil.copyfile(folhaBranca, os.path.join(args.provas, prova.polo, folha + '.png'))
                                if folha.endswith('-01') and prova.questoesObjetivas != 0:
                                    nomeArquivo = os.path.join(args.provas, prova.polo, folha + '.csv')
                                    respostasBranco = [[x, '_'] for x in range(1, prova.questoesObjetivas + 1)]
                                    csv.writer(open(nomeArquivo, 'wt')).writerows(respostasBranco)

                            contagem += 1


    print(contagem, 'arquivos em branco distribuidos')

