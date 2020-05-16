#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import db
import datetime
import csv

def Consolida(corretores, tarefas, indice):
    for correcao in tarefas:
        corretor = correcao.corrector_data.get('corrector_id', 0)
        c = corretores.get(corretor, [0, 0, 0, 0]) 
        c[indice] += 1
        corretores[corretor] = c
        
    return corretores


def ColetaDadosCorretores(periodo):
    corretores = {}
    d7 = datetime.date.today() - datetime.timedelta(days = 7)
    d14 = datetime.date.today() - datetime.timedelta(days = 14)
    d30 = datetime.date.today() - datetime.timedelta(days = 30)
    
    # Teremos um vetor com as correções das mais velhas para as mais novas: [>=d30, d30>X>=d14, d14>X>=d7, <d7]
    
    # Coleta correções antigas = número de questões corrigidas antes de período
    tarefas = db.session.query(db.ActivityRecordSubmissionCorrections) \
                        .filter(db.ActivityRecordSubmissionCorrections.updated_at < d30)
    corretores = Consolida(corretores, tarefas, 0)
            
    tarefas = db.session.query(db.ActivityRecordSubmissionCorrections) \
                        .filter(db.ActivityRecordSubmissionCorrections.updated_at >= d30) \
                        .filter(db.ActivityRecordSubmissionCorrections.updated_at < d14)
    corretores = Consolida(corretores, tarefas, 1)
                    
                        
    tarefas = db.session.query(db.ActivityRecordSubmissionCorrections) \
                        .filter(db.ActivityRecordSubmissionCorrections.updated_at >= d14) \
                        .filter(db.ActivityRecordSubmissionCorrections.updated_at < d7)
    corretores = Consolida(corretores, tarefas, 2)
        
    tarefas = db.session.query(db.ActivityRecordSubmissionCorrections) \
                        .filter(db.ActivityRecordSubmissionCorrections.updated_at >= d7)
    corretores = Consolida(corretores, tarefas, 3)
                           
    tabela = []
    for corretor in corretores:
        iu = db.session.query(db.InternalUsers).filter(db.InternalUsers.id == corretor).first()
        if iu != None:
            linha = [iu.email]
            linha.extend(corretores[corretor])
            tabela.append(linha)
            
    csv.writer(open('estatisticas-corretores.csv', 'wt')).writerows(tabela)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Coleta Estatísticas dos Corretores das Provas.')
    parser.add_argument('-p', '--periodo', type=int, required=False, help='Período, em dias, a considerar na contagem')

    args = parser.parse_args()

    if args.periodo is None:
        args.periodo = 30

    ColetaDadosCorretores(args.periodo)
    