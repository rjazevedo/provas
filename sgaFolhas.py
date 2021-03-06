#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Carrega links de folhas de resposta de provas no SGA a partir de um CSV:
Cód. da disciplina,Cód. da prova,RA do aluno,Número da folha,Link do arquivo da folha de resposta"""

###############################################
# Uso: sgaFolhas.py -a folhas.csv -c 38
#
# folhas.csv: link deve começar em "SGA/..."
# 38: é o calendário do bimestre 2019/2
#
# o arquivo dbpass.txt deve estar no diretório
#
# Corresponde à: CreateSubmissionsResponseSheetsFromCSV
###############################################

from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
import os
import sys
import argparse
import db
import csv

args = None

offer_types = { 'regular': 1, 'dp': 2, 'exam': 1, 'dpexam': 2 } #acrescentado o exam #dsc
TEST_PATH = '/var/data/nfs/provas/' # está no .ENV no SGA
####################
# Inicia Sessão 
####################
sess = db.Session()
sess.autoflush = True  # default

def erro( str ):
    print( "Erro: " + str )

def carregaFolha( 
                  ac,         # activity_code
                  tc,         # test_code
                  ar,         # academic_register
                  n,          # number
                  ls,         # link_sheet
                  st,         # submission_type
                  cid,        # calendar_id
                  forca,      # forca substituição
                  decrescente # associa a folha usando a segunda ocorrencia de uma mesma disciplina
                ):

    """Carrega o link de uma folha de resposta, de uma prova, de um aluno, no SGA"""

    print(  
            "Tenta carregar link de folha de resposta: ",
            ac,         # activity_code
            tc,         # test_code
            ar,         # academic_register
            n,          # number
            ls,         # link_sheet
            st,         # submission_type
            cid,        # calendar_id
            forca,      # forca substituição
            decrescente # associa a folha usando a segunda ocorrencia de uma mesma disciplina
          )

    # ####################
    # # Inicia Sessão 
    # ####################
    # sess = db.Session()
    # sess.autoflush = True  # default

    # disciplina
    activity = sess.query(db.CurricularActivities) \
                   .filter(db.CurricularActivities.code == ac) \
                   .first()

    if not activity: 
      erro( "Missing CurricularActivities: %s" % (ac) )
      return

    # oferta
    if decrescente:
        offer = sess.query(db.ActivityOffers) \
                    .filter(db.ActivityOffers.curricular_activity_id == activity.id) \
                    .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                    .filter(db.ActivityOffers.calendar_id == cid) \
                    .order_by(db.ActivityOffers.id.desc()) \
                    .first()
    
    else:
        offer = sess.query(db.ActivityOffers) \
                    .filter(db.ActivityOffers.curricular_activity_id == activity.id) \
                    .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                    .filter(db.ActivityOffers.calendar_id == cid) \
                    .first()

    if not offer: 
      erro( "Missing ActivityOffers: %d, %d" % (cid, offer_types[st]) )
      return

    # aluno
    student = sess.query(db.Students).filter(db.Students.academic_register == ar).first()

    if not student: 
      erro( "Missing Students: %d" %(ar) )
      return

    # registro
    record = sess.query(db.ActivityRecords) \
                 .filter(db.ActivityRecords.student_id == student.id) \
                 .filter(db.ActivityRecords.curricular_activity_id == activity.id) \
                 .filter(db.ActivityRecords.activity_offer_id == offer.id) \
                 .first()

    if not record:
      erro( "Missing ActivityRecord: %d, %d, %d" % (student.id, activity.id, offer.id) )
      return

    # prova
    test = sess.query(db.ActivityTests) \
               .filter(db.ActivityTests.code == tc) \
               .filter(db.ActivityTests.curricular_activity_id == activity.id) \
               .first()

    if not test:
      erro( "Missing ActivityTests: %s, %d" % (tc, activity.id) )
      return
      
    if st == 'dpexam': #dsc
        st = 'exam' #dsc

    # submissão (cria uma caso não exista)
    submission = sess.query(db.ActivityRecordSubmissions) \
                     .filter(db.ActivityRecordSubmissions.activity_record_id == record.id) \
                     .filter(db.ActivityRecordSubmissions.submission_type == st) \
                     .first()

    if not submission:
        submission = db.ActivityRecordSubmissions(
                                                    activity_record_id = record.id,
                                                    submission_type = st,
                                                    activity_test_id = test.id,
                                                    created_at = func.now(),
                                                    updated_at = func.now()
                                                 )
        sess.add(submission)

    submission.activity_test_id = test.id

    # anexo (cria um caso não exista)
    attach = sess.query(db.Attachments) \
                 .filter(db.Attachments.attach_reference_id == submission.id) \
                 .filter(db.Attachments.attach_reference_type == 'ActivityRecordSubmission') \
                 .filter(db.Attachments.attach_type == 'response_sheets') \
                 .first()

    if not attach:
        attach = db.Attachments(
                                  attach_reference_id = submission.id,
                                  attach_reference_type = 'ActivityRecordSubmission',
                                  attach_type = 'response_sheets',
                                  created_at = func.now(),
                                  updated_at = func.now()
                               )
        sess.add(attach)

    if not attach.sheets_data: attach.sheets_data = []

    has_sheet_n = False
    sheet_n_i = 0
    for i in range(len(attach.sheets_data)):
        e = attach.sheets_data[i]
        if e['number'] == n:
            has_sheet_n = True
            sheet_n_i = i

    sheet_link = {'number': n, 'path': TEST_PATH + ls}

    # carrega folha caso não exista
    if not has_sheet_n:
        attach.sheets_data.append(sheet_link)
    elif forca:
        attach.sheets_data[sheet_n_i] = sheet_link
        
    flag_modified(attach, "sheets_data")  # Sqlalchemy JSON é imutável por default

    sess.commit()
    # sess.close()

    print( "Sucesso!" )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Carrega links de folhas de resposta de provas no SGA'
                                                 ' a partir de um CSV com as colunas: Cód. da disciplina,'
                                                 'Cód. da prova,RA do aluno,Número da folha,'
                                                 'Link do arquivo da folha de resposta')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV de folhas de resposta')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')
    parser.add_argument('-f', '--forca', action='store_true', help='Substitui forçosamente o link, caso já exista uma folha de mesmo número')
    parser.add_argument('-d', '--decrescente', action='store_true', help='Caso exista duas disciplinas com mesmo código, ao invés de inserir na primeira ocorrencia usa a segunda')

    args = parser.parse_args()

    arquivo = args.arquivo
    calendario = args.calendario
    tipo = args.tipo

    if args.tipo is not None:
        if args.tipo not in ['regular','dp','exam','dpexam']: #acrescimo de exam
            print( 'Tipo de submissão deve ser regular, exam ou dp' )
            sys.exit(1)
        tipo = args.tipo

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
                          row[0],          # str, Cód. da disciplina
                          row[1],          # str, Cód. da prova
                          row[2],          # str, RA do aluno
                          int(row[3]),     # int, Número da folha
                          row[4],          # str, Link do arquivo da folha de resposta
                          tipo,            ### str, Tipo da submissão
                          calendario,      ### int, ID do calendário
                          args.forca,      # bool, força substituição do link, caso já exista
                          args.decrescente # associa a folha usando a segunda ocorrencia de uma mesma disciplina
                        )
