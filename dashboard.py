#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Gera um dashboard sobre o status das provas no sistema"""

import argparse
import os
import csv
import math
import sys
from utils import LinhaProva, BuscaArquivos


def DashboardProva(pasta, alunos, arquivos):
    nomeArquivo = alunos[0].LabelProva() + '.html'
    saida = open(os.path.join(pasta, nomeArquivo), 'wt')
    header = open('header.html').read() 
    footer = open('footer.html').read()
    saida.write(header)

    saida.write('<div class="row"><h2>' + alunos[0].LabelProva() + '</h2></div>')

    totalAlunos = 0
    alunosCompletos = 0
    alunosIncompletos = 0
    alunosFaltantes = 0
    folhasFaltantes = 0

    saida.write('<tr><th>RA</th><th>Nome</th><th colspan="5">Folhas</th></tr>\n')
    for aluno in alunos:
        totalAlunos += 1
        saida.write('<tr><td>' + aluno.ra + '</td><td>' + aluno.nomeAluno + '</td>')
        folhas = 0
        for i in range(1, aluno.totalFolhas + 1):
            arquivo = aluno.codigo + '-' + '{:02d}'.format(i) + '.png'
            if arquivo in arquivos:
                saida.write('<td>' + str(i) + '</td>')
                folhas += 1
            else:
                saida.write('<td class="red">' + str(i) + '</td>')
                folhasFaltantes += 1

        if folhas == aluno.totalFolhas:
            alunosCompletos += 1
        elif folhas != 0:
            alunosIncompletos += 1
        else:
            alunosFaltantes += 1
        
        saida.write('</tr>\n')

    saida.write(footer)

    return (nomeArquivo, totalAlunos, alunosCompletos, alunosIncompletos, alunosFaltantes, folhasFaltantes)


def GeraDashboard(pasta, provas, arquivos, base):

    resumoPolos = {}
    saida = open(os.path.join(pasta, 'index.html'), 'wt')
    header = open(os.path.join(base, 'header.html')).read() 
    footer = open(os.path.join(base, 'footer.html')).read()
    saida.write(header)
    saida.write('<h2><a href="resumo.html">Resumo por polo</a></h2>\n')
    saida.write('<thead><tr><th>Polo</th><th>Nome</th><th>Data</th><th>Disciplina</th><th>Nome</th><th>Ocorrência</th><th>Presença</th><th>Alunos Totais</th><th>Provas Completas</th><th>Provas Incompletas</th><th>Alunos que faltam</th><th>Folhas faltantes</th></tr></thead><tbody>\n')
    for p in sorted(provas.keys()):
        print(p, ' ' * 30, end='\r')
        prova = provas[p]
        (nomeArquivo, totalAlunos, alunosCompletos, alunosIncompletos, alunosFaltantes, folhasFaltantes) = DashboardProva(pasta, prova, arquivos)
        if not prova[0].nomePolo in resumoPolos:
            resumoPolos[prova[0].nomePolo] = [[totalAlunos, alunosCompletos, alunosIncompletos, alunosFaltantes, folhasFaltantes]]
        else:
            resumoPolos[prova[0].nomePolo].append([totalAlunos, alunosCompletos, alunosIncompletos, alunosFaltantes, folhasFaltantes])

        folhas = math.ceil(len(prova) / 20)
        saida.write('<tr><td>' + prova[0].polo + '</td><td>' + prova[0].nomePolo + '</td><td>' + prova[0].data + '</td><td><a href="' + nomeArquivo + '">' + prova[0].disciplina + '</a></td><td>' + prova[0].nomeDisciplina + '</td>')

        if prova[0].dataStr + '-' + prova[0].polo + '-ocorrencia.png' in arquivos:
            saida.write('<td>Presente</td>')
        else:
            saida.write('<td class="red">Ausente</td>')

        saida.write('<td>')
        for f in range(1, folhas + 1):
            n = prova[0].LabelProva() + '-presenca-' + format(f, '02d') + '.png'
            if n in arquivos:
                saida.write(format(f, '02d') + ' ')

        saida.write('</td>')

        saida.write('<td>' + str(totalAlunos) + '</td>')
        saida.write('<td>' + str(alunosCompletos) + '</td>')

        if alunosIncompletos == 0:
            saida.write('<td>' + str(alunosIncompletos) + '</td>')
        else:
            saida.write('<td class="red">' + str(alunosIncompletos) + '</td>')

        if alunosFaltantes == 0:    
            saida.write('<td>' + str(alunosFaltantes) + '</td>')
        else:
            saida.write('<td class="red">' + str(alunosFaltantes) + '</td>')

        if folhasFaltantes == 0:
            saida.write('<td>' + str(folhasFaltantes) + '</td></tr>\n')
        else:
            saida.write('<td class="red">' + str(folhasFaltantes) + '</td></tr>\n')

    saida.write(footer)
    saida.close()

    resumo = open(os.path.join(pasta, 'resumo.html'), 'wt')
    resumo.write(header)
    resumo.write('<thead><tr><th>Polo</th><th>Alunos Totais</th><th>Provas Completas</th><th>Provas Incompletas</th><th>Alunos que faltam</th><th>Folhas faltantes</th></tr></thead><tbody>\n')
    for polo in sorted(resumoPolos.keys()):
        provas = resumoPolos[polo]
        somaAlunos = somaCompletos = somaIncompletos = somaAlunosFaltantes = somaFolhasFaltantes = 0
        for [totalAlunos, alunosCompletos, alunosIncompletos, alunosFaltantes, folhasFaltantes] in provas:
            somaAlunos += totalAlunos
            somaCompletos += alunosCompletos
            somaIncompletos += alunosIncompletos
            somaAlunosFaltantes += alunosFaltantes
            somaFolhasFaltantes += folhasFaltantes

        resumo.write('<tr><td>' + polo + '</td><td>' + str(somaAlunos) + '</td><td>' + str(somaCompletos) + '</td>')

        if somaIncompletos != 0:
            resumo.write('<td class="red">' + str(somaIncompletos) + '</td>')
        else:
            resumo.write('<td>0</td>')

        if somaAlunosFaltantes != 0:
            resumo.write('<td class="red">' + str(somaAlunosFaltantes) + '</td>')
        else:
            resumo.write('<td>0</td>')

        if somaFolhasFaltantes != 0:
            resumo.write('<td class="red">' + str(somaFolhasFaltantes) + '</td></tr>\n')
        else:
            resumo.write('<td>0</td></tr>\n')

    resumo.write(footer)
    resumo.close()

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gera um dashboard com o status das provas no sistema')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Pasta de entrada')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Arquivo informações sobre as provas')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Pasta de saida')

    args = parser.parse_args()

    listaArquivos = BuscaArquivos(args.entrada, recursivo=True, tipo='.png', nomeCompleto=False)
    print(len(listaArquivos), 'arquivos considerados.')

    entrada = csv.reader(open(args.provas))
    next(entrada)
    alunos = [LinhaProva(a) for a in entrada]
    print(len(alunos), 'provas consideradas.')

    base = os.path.dirname(sys.argv[0])

    provas = {}
    for aluno in alunos:
        aluno.GeraCodigo()
        if aluno.OrdemProva() in provas:
            provas[aluno.OrdemProva()].append(aluno)
        else:
            provas[aluno.OrdemProva()] = [aluno]

    GeraDashboard(args.saida, provas, listaArquivos, base)
