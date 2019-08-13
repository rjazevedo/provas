#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Cria registros de provas e guias de correção no SGA a partir de um CSV:
Cód. da disciplina,Cód. da prova,Número de folhas,Link do arquivo"""

####################################################
# Uso: sgaTestesGuias.py -a guias.csv
#
# o arquivo dbpass.txt deve estar no diretório
#
# Corresponde à: CreateSubmissionsTestsAndGuidesFromCSV
####################################################

from sqlalchemy import func
import os
import sys
import argparse
import db
import csv

args = None

offer_types = { 'regular': 1, 'dp': 2 }
TEST_PATH = '/var/data/nfs/provas/' # está no .ENV no SGA

def erro( str ):
    print( "Erro: " + str )

def carregaFolha( 
                  ac,  # activity_code
                  tc,  # test_code
                  ns,  # number of sheets
                  lk   # link
                ):

    """Cria registros de provas e guias de correção no SGA"""

    print(  
            "Tenta criar registro de prova e guias: ",
            ac,  # activity_code
            tc,  # test_code
            ns,  # number of sheets
            lk   # link
        )

    ####################
    # Inicia Sessão 
    ####################
    sess = db.Session()
    sess.autoflush = True  # default

    # disciplina
    activity = sess.query(db.CurricularActivities) \
                   .filter(db.CurricularActivities.code == ac) \
                   .first()

    if not activity: 
      erro( "Missing CurricularActivities: %s" % (ac) )
      return

    # prova (cria uma caso não exista)
    test = sess.query(db.ActivityTests) \
               .filter(db.ActivityTests.code == tc) \
               .filter(db.ActivityTests.curricular_activity_id == activity.id) \
               .first()

    if not test:
        test = db.ActivityTests(
                                  code = tc,
                                  curricular_activity_id = activity.id,
                                  created_at = func.now(),
                                  updated_at = func.now()
                               )
        sess.add(test)

    test.total_pages = ns

    # anexo (cria um caso não exista)
    attach = sess.query(db.Attachments) \
                 .filter(db.Attachments.attach_reference_id == test.id) \
                 .filter(db.Attachments.attach_reference_type == 'ActivityTest') \
                 .filter(db.Attachments.attach_type == 'correction_guide') \
                 .first()

    if not attach:
        attach = db.Attachments(
                                  attach_reference_id = test.id,
                                  attach_reference_type = 'ActivityTest',
                                  attach_type = 'correction_guide',
                                  created_at = func.now(),
                                  updated_at = func.now()
                               )
        sess.add(attach)

    attach.attach_path = TEST_PATH + lk

    sess.commit()

    print( "Sucesso!" )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cria registros de provas e guias de correção no SGA'
                                                 ' a partir de um CSV: Cód. da disciplina,Cód. da prova,'
                                                 ' Número de folhas,Link do arquivo')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV de provas e guias')

    args = parser.parse_args()

    arquivo = args.arquivo

    if not os.path.isfile(arquivo):
        print( 'Arquivo ' + arquivo + ' não encontrado!' )
        sys.exit(1)

    ####################
    # percorre CSV
    ####################

    with open(arquivo, newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            carregaFolha(
                          row[0],      # str, Cód. da disciplina
                          row[1],      # str, Cód. da prova
                          int(row[2]), # int, Número de folhas
                          row[3]       # str, Link do arquivo
                        )
