#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Remove Corretor Duplicado"""

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
import json

args = None

offer_types = { 'regular': 1, 'dp': 2, 'exam': 1 } #acrescentado o exam

####################
# Inicia Sessão 
####################
sess = db.Session()
sess.autoflush = True  # default


def erro( str ):
    print( "Erro: " + str )

def RemoveDuplicado(forca):
    """ Remove corretores duplicados para uma mesma prova """
        
    # Para cada Activity Record Submission (atividade que precisa de avaliação)
    todasProvas = sess.query(db.ActivityRecordSubmissions).all()
    apagar = []
    quantidade = 0
    
    for prova in todasProvas:
        corretores = [x for x in prova.correctors if x.role == 'grader']
        
        if len(corretores) <= 1:
            continue
          
        print('-----')
        print(prova, len(corretores))
        # Trata separadamente os casos corrigidos dos não corrigidos
        if len(prova.activity_test.questions) == len(prova.corrections):
            # Prova corrigida, mantem o(s) corretores que corrigiram
            corrigiram = {}
            for x in prova.corrections:
              corrigiram[x.corrector_data.get('corrector_id', 0)] = True
              
            for c in corretores:
                if not c.internal_user_id in corrigiram:
                    print('Corrigida. Remover:', c.internal_user)
                    if forca:
                        apagar.append(c)
                        # sess.delete(c)
                else:
                    print('Corrigida. Manter:', c.internal_user)
          
        else:
            # Prova não corrigida, mantem o primeiro corretor que não esteja inativo
            primeiro = True
            for c in corretores:
                if c.internal_user.status == 'active' and primeiro:
                    print('Não corrigida. Manter:', c.internal_user)
                    primeiro = False
                else:
                    print('Não corrigida. Remover:', c.internal_user)
                    if forca:
                        apagar.append(c)
                        # sess.delete(c)

        if len(apagar) > 100:
            for c in apagar:
                sess.delete(c)
                quantidade += 1
            apagar = []
            sess.commit()
            
    for c in apagar:
        sess.delete(c)
        quantidade += 1
    apagar = []
    sess.commit()   
    
    print(quantidade, 'tarefas de correção removidas de corretores.')     
  

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Remove múltiplos corretores duplicados para a mesma prova deixando apenas um')
    parser.add_argument('-f', '--forca', action='store_true', required=False, help='Força a execução. É obrigatório para evitar problemas')

    args = parser.parse_args()

    RemoveDuplicado(args.forca)

