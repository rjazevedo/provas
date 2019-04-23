#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Gera um dashboard sobre o status das provas no sistema"""

import argparse
import os
import csv
import math

def DataInvertida(dataStr):
    return dataStr[6:10] + dataStr[3:5] + dataStr[0:2]


class Aluno:
    def __init__(self, campos):
        self.nome = campos[0]
        self.ra = campos[1]
        self.polo = campos[2]
        self.nomePolo = campos[3]
        self.data = campos[4]
        self.curso = campos[5]
        self.turma = campos[6]
        self.bimestre = campos[7]
        self.disciplina = campos[8]
        self.nomeDisciplina = campos[9]
        self.prova = campos[10]
        self.questoesObjetivas = int(campos[11])
        self.folhasDissertativas = int(campos[12])
        self.dataStr = DataInvertida(self.data)
        self.codigo = ''
        self.totalFolhas = self.folhasDissertativas
        if self.questoesObjetivas != 0:
            self.totalFolhas += 1
        return

    def GeraCodigo(self):
        self.codigo = self.dataStr + '-' + \
                      self.polo + '-' + self.disciplina + '-' + \
                      self.prova + '-' + self.ra

        return self.codigo

    def LabelProva(self):
        return self.dataStr + '-' + self.polo + '-' + self.disciplina + '-' + self.prova

    def Esvazia(self, ra):
        self.nome = '__________________________________________________'
        self.curso = '_________________________'
        self.turma = '_______________'
        self.bimestre = '___'
        self.ra = ra
        self.GeraCodigo()
        self.ra = '________'
        return



def BuscaArquivos(p):
    resposta = []
    for arquivo in os.scandir(p):
        if not arquivo.name.startswith('.'):
            if arquivo.is_file():
                resposta.append(arquivo.name)
            elif arquivo.is_dir():
                resposta.extend(BuscaArquivos(os.path.join(p, arquivo.name)))

    return resposta


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
        saida.write('<tr><td>' + aluno.ra + '</td><td>' + aluno.nome + '</td>')
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


def GeraDashboard(pasta, provas, arquivos):

    saida = open(os.path.join(pasta, 'index.html'), 'wt')
    header = open('header.html').read() 
    footer = open('footer.html').read()
    saida.write(header)
    saida.write('<tr><th>Polo</th><th>Nome</th><th>Disciplina</th><th>Nome</th><th>Ocorrência</th><th>Presença</th><th>Alunos Totais</th><th>Provas Completas</th><th>Provas Incompletas</th><th>Alunos que faltam</th><th>Folhas faltantes</th></tr>\n')
    for p in provas.keys():
        prova = provas[p]
        (nomeArquivo, totalAlunos, alunosCompletos, alunosIncompletos, alunosFaltantes, folhasFaltantes) = DashboardProva(pasta, prova, arquivos)
        folhas = math.ceil(len(prova) / 20)
        saida.write('<tr><td>' + prova[0].polo + '</td><td>' + prova[0].nomePolo + '</td><td><a href="' + nomeArquivo + '">' + prova[0].disciplina + '</a></td><td>' + prova[0].nomeDisciplina + '</td>')

        if prova[0].dataStr + '-' + prova[0].polo + '-ocorrencia.png' in arquivos:
            saida.write('<td>OK</td>')
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
    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gera um dashboard com o status das provas no sistema')
    parser.add_argument('-e', '--entrada', type=str, required=True, help='Pasta de entrada')
    parser.add_argument('-p', '--provas', type=str, required=True, help='Arquivo informações sobre as provas')
    parser.add_argument('-s', '--saida', type=str, required=True, help='Pasta de saida')

    args = parser.parse_args()

    listaArquivos = BuscaArquivos(args.entrada)

    entrada = csv.reader(open(args.provas))
    next(entrada)
    alunos = [Aluno(a) for a in entrada]

    provas = {}
    for aluno in alunos:
        aluno.GeraCodigo()
        if aluno.LabelProva() in provas:
            provas[aluno.LabelProva()].append(aluno)
        else:
            provas[aluno.LabelProva()] = [aluno]

    GeraDashboard(args.saida, provas, listaArquivos)
