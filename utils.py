#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Funções utilitárias que estão sendo utilizadas por diversos dos scripts desta pasta"""

import os

def BuscaArquivos(p, recursivo = False, tipo = '', nomeCompleto = True):
    resposta = []
    for arquivo in os.scandir(p):
        if not arquivo.name.startswith('.') and arquivo.name.endswith(tipo):
            if arquivo.is_file():
                if nomeCompleto:
                    resposta.append(os.path.join(p, arquivo.name))
                else:
                    resposta.append(arquivo.name)
        elif arquivo.is_dir() and recursivo:
            resposta.extend(BuscaArquivos(os.path.join(p, arquivo.name), recursivo=recursivo, tipo=tipo, nomeCompleto=nomeCompleto))

    return resposta

def Arquivos2Dict(lista):
    d = {}
    for arquivo in lista:
        d[os.path.basename(arquivo)[:-4]] = arquivo
    return d

def DataInvertida(dataStr):
    return dataStr[6:10] + dataStr[3:5] + dataStr[0:2]

class LinhaProva:
    def __init__(self, campos):
        self.nomeAluno = campos[0]
        self.ra = campos[1]
        self.polo = campos[2]
        if len(self.polo) < 4:
            self.polo = '0' * (4 - len(self.polo)) + self.polo
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
        self.novo = False
        self.codigo = ''
        self.GeraCodigo()
        self.totalFolhas = self.folhasDissertativas
        if self.questoesObjetivas != 0:
            self.totalFolhas += 1
        return

    def GeraCodigo(self):
        self.codigo = self.dataStr + '-' + \
                      self.polo + '-' + self.disciplina + '-' + \
                      self.prova + '-' + self.ra

        return self.codigo

    def idProva(self):
        return self.disciplina + '-' + self.prova

    def idPaginas(self, tipo = ''):
        limite = self.folhasDissertativas
        if self.questoesObjetivas > 0:
            limite += 1
        
        resposta = []
        for n in range(0, limite):
            resposta.append(self.codigo + '-' + format(n + 1, '02d') + tipo) 

        return resposta

    def idPresenca(self):
        return self.dataStr + '-' + self.polo + '-' + self.disciplina + '-' + self.prova + '-' + self.ra

    def LabelProva(self):
        return self.dataStr + '-' + self.polo + '-' + self.disciplina + '-' + self.prova

    def OrdemProva(self):
        return self.nomePolo + '-'+ self.data + '-' + self.disciplina + '-' + self.prova

    def Esvazia(self, ra):
        self.nome = '__________________________________________________'
        self.curso = '_________________________'
        self.turma = '_______________'
        self.bimestre = '___'
        self.ra = ra
        self.GeraCodigo()
        self.ra = '________'
        return

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

    def OrdemProva(self):
        return self.nomePolo + '-'+ self.data + '-' + self.disciplina + '-' + self.prova

    def Esvazia(self, ra):
        self.nome = '__________________________________________________'
        self.curso = '_________________________'
        self.turma = '_______________'
        self.bimestre = '___'
        self.ra = ra
        self.GeraCodigo()
        self.ra = '________'
        return

