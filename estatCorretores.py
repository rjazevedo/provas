#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import db
import datetime
import csv

def ColetaDadosCorretores(periodo):
    corretores = {}
    data = datetime.date.today() - datetime.timedelta(days = periodo)
    
    # Coleta correções antigas = número de questões corrigidas antes de período
    
    antigas = db.session.query(db.ActivityRecordSubmissionCorrections).filter(db.ActivityRecordSubmissionCorrections.updated_at < data)
    for correcao in antigas:
        corretor = correcao.corrector_data.get('corrector_id', 0)
        c = corretores.get(corretor, [0, 0]) # primeira coluna é passado (antigas), segunda é do último período
        c[0] += 1
        corretores[corretor] = c
        
    # Coleta correções novas = número de questões corrigidas nos últimos período dias
    atuais = db.session.query(db.ActivityRecordSubmissionCorrections).filter(db.ActivityRecordSubmissionCorrections.updated_at >= data)
    for correcao in atuais:
        corretor = correcao.corrector_data.get('corrector_id', 0)
        c = corretores.get(corretor, [0, 0]) # primeira coluna é passado (antigas), segunda é do último período
        c[1] += 1
        corretores[corretor] = c

    tabela = []
    for corretor in corretores:
        iu = db.session.query(db.InternalUsers).filter(db.InternalUsers.id == corretor).first()
        if iu != None:
            tabela.append([iu.email, corretores[corretor][0], corretores[corretor][1]])
            
    csv.writer(open('estatisticas-corretores.csv', 'wt')).writerows(tabela)
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Coleta Estatísticas dos Corretores das Provas.')
    parser.add_argument('-p', '--periodo', type=int, required=False, help='Período, em dias, a considerar na contagem')

    args = parser.parse_args()

    if args.periodo is None:
        args.periodo = 30

    ColetaDadosCorretores(args.periodo)
    