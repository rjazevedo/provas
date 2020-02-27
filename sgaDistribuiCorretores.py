#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Dada duas listas de corretores contendo a alocação de disciplina e a carga de trabalho, distribui
as correções de provas"""

###############################################
# Uso: sgaCorretores.py -a corretores.csv -c 38
#
# 38: é o calendário do bimestre 2019/2
#
# o arquivo dbpass.txt deve estar no diretório
#
# Corresponde à: CreateSubmissionsCorrectorsFromCSV
###############################################

from sqlalchemy import func
import os
import sys
import argparse
import db
import csv
import heapq
import datetime

args = None
peso = 2 # Número de questões a corrigir por prova. Apesar de fazermos a alocação por prova, a contabilidade é sempre por questões.

####################
# Inicia Sessão 
####################
sess = db.Session()
sess.autoflush = True  # default


class Corretor:
    def __init__(self, disciplina, email, nome):
        self.nome = nome
        self.email = email
        self.passado = 0
        self.corrigidas = 0
        self.disciplinas = [disciplina]
        self.dbId = 0
        self.ativo = True
        
    def __cmp__(self, other):
        """ Corretores serão ordenados pelo número de questões corrigidas"""
        return self.corrigidas - other.corrigidas
    
    def __lt__(self, other):
        return self.corrigidas < other.corrigidas
    
    def __gt__(self, other):
        return self.corrigidas > other.corrigidas
    
    def __eq__(self, other):
        return self.corrigidas == other.corrigidas
    
    def __repr__(self):
        return '{0} <{1}> ({2})'.format(self.nome, self.email, str(self.corrigidas))
    
class Disciplina:
    def __init__(self, sigla):
        self.sigla = sigla
        self.dbId = 0
        self.corretores = []
        self.alocacoes = 0
        self.indice = 0
        
    def Proximo(self):
        corretor = self.corretores[self.indice]
        self.indice += 1
        if self.indice >= len(self.corretores):
            self.indice = 0      
        return corretor
            
    def Verifica(self):
        # Verifica se tem algum corretor apto a corrigir (dentro do limite)
        resultado = False
        for c in self.corretores:
            resultado = resultado or c.ativo
            
        # Se não achou ninguém, ativa todos
        if not resultado:
            for c in self.corretores:
                c.ativo = True
                
        # Remove os que não serão alocados
        self.corretores = [x for x in self.corretores if x.ativo]
        
    
def AtribuiCorretores(arqCorretores, arqEstatisticas, limite):
    if not os.path.isfile(arqCorretores):
        print('Arquivo não encontrado:', arqCorretores)
        return
  
    todosCorretores = {}
    todasDisciplinas = {}
    for [d, e, n] in csv.reader(open(arqCorretores)): # disciplina, email, nome
        if e not in todosCorretores: # email não está cadastrado ainda
            c = Corretor(d, e, n)
            todosCorretores[e] = c
            if d not in todasDisciplinas:
                disc = Disciplina(d)
                todasDisciplinas[d] = disc
                disc.corretores.append(c)
            else:
                todasDisciplinas[d].corretores.append(c)
        else:
            todosCorretores[e].disciplinas.append(d)
            if d not in todasDisciplinas:
                disc = Disciplina(d)
                todasDisciplinas[d] = disc
                disc.corretores.append(todosCorretores[e])
            else:
                todasDisciplinas[d].corretores.append(todosCorretores[e])
                
    # Se existir o arquivo  de estatísticas, lê os dados e completa a listagem.
    if os.path.isfile(arqEstatisticas):
        for [e, p, c] in csv.reader(open(arqEstatisticas)):
            if e in todosCorretores:
                todosCorretores[e].passado = int(p)
                todosCorretores[e].corrigidas = int(c)
                if int(c) >= limite:
                    todosCorretores[e].ativo = False
        
    # Ordena todas as listas no formato de heap. O menor sempre primeiro e coleta o id da disciplina
    for d in todasDisciplinas.values(): 
        # Ordena corretores do menor para o maior em número de correções já realizadas
        # Não faz muita diferença a ordenação exceto para o caso de chegar de prova em prova e não ficar em ordem alfabética
        heapq.heapify(d.corretores)
        d.Verifica()
        # Busca o código da disciplina da tabela da base de dados
        disc = db.session.query(db.CurricularActivities).filter(db.CurricularActivities.code == d.sigla).first()
        if disc is not None:
            d.dbId = disc.id
            
    # Busca os ids dos corretores na base para acelerar o processo
    for c in todosCorretores.values():
        corr = db.session.query(db.InternalUsers).filter(db.InternalUsers.email == c.email).first()
        if corr is not None:
            c.dbId = corr.id
            
    # Agora percorre todas as provas não corrigidas na base
    inicioDoModelo = datetime.date(year=2019, month=1, day=1)
    todasProvas = db.session.query(db.ActivityRecordSubmissions).filter(db.ActivityRecordSubmissions.created_at >= inicioDoModelo)
    
    for prova in todasProvas:
        if not db.ProvaCorrigida(prova):
            sigla = prova.activity_record.curricular_activity.code
            if sigla not in todasDisciplinas:
                print(sigla, ' Ops! não há nenhum corretor alocado para esta disciplina!')
                continue
            
            # Pega a disciplina
            disc = todasDisciplinas[sigla]
            # Corretor com menor número de correções
            corretor = disc.Proximo()
            print(sigla, ' Corretor selecionado:', corretor)
            
            
  

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Associa corretores (internal_users) a provas dos alunos levando em conta a carga de trabalho de correção.')
    parser.add_argument('-c', '--corretores', type=str, required=True, help='Arquivo CSV com os emails dos corretores')
    parser.add_argument('-e', '--estatisticas', type=str , required=True, help='Arquivo CSV com as estatísticas de correção por corretor')
    parser.add_argument('-l', '--limite', type=int , default=300, required=False, help='Altera o limite de número de questões corrigidas por corretor (default = 300)')

    args = parser.parse_args()
    
    AtribuiCorretores(args.corretores, args.estatisticas, args.limite)
