#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Carrega links de folhas de resposta de provas no SGA a partir de um CSV:
Cód. da disciplina,Cód. da prova,RA do aluno,Número da folha,Link do arquivo da folha de resposta"""

from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
import os
import sys
import argparse
import db

args = None

offer_types = { 'regular': 1, 'dp': 2 }
TEST_PATH = '/var/data/nfs/provas/' # está no .ENV no SGA

def erro( str ):
    print( "Erro: " + str )
    sys.exit(1)

def carregaFolha( 
                  ac,  # activity_code
                  tc,  # test_code
                  ar,  # academic_register
                  n,   # number
                  ls,  # link_sheet
                  st,  # submission_type
                  cid  # calendar_id
                ):

    """Carrega o link de uma folha de resposta, de uma prova, de um aluno, no SGA"""

    ####################
    # Inicia Sessão 
    ####################
    sess = db.Session()
    sess.autoflush = True  # default

    # disciplina
    activity = sess.query(db.CurricularActivities) \
                   .filter(db.CurricularActivities.code == ac) \
                   .first()

    # oferta
    offer = sess.query(db.ActivityOffers) \
                .filter(db.ActivityOffers.calendar_id == cid) \
                .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                .first()

    # aluno
    student = sess.query(db.Students).filter(db.Students.academic_register == ar).first()

    if not activity: erro( "Missing CurricularActivities: %s" % (ac) )
    if not offer: erro( "Missing ActivityOffers: %d, %d" % (cid, offer_types[st]) )
    if not student: erro( "Missing Students: %d" %(ar) )

    # registro
    record = sess.query(db.ActivityRecords) \
                 .filter(db.ActivityRecords.student_id == student.id) \
                 .filter(db.ActivityRecords.curricular_activity_id == activity.id) \
                 .filter(db.ActivityRecords.activity_offer_id == offer.id) \
                 .first()

    # prova
    test = sess.query(db.ActivityTests) \
               .filter(db.ActivityTests.code == tc) \
               .filter(db.ActivityTests.curricular_activity_id == activity.id) \
               .first()

    if not record: erro( "Missing ActivityRecord: %d, %d, %d" % (student.id, activity.id, offer.id) )
    if not test: erro( "Missing ActivityTests: %s, %d" % (tc, activity.id) )

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
    else:
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
    for e in attach.sheets_data:
        if e['number'] == n:
            has_sheet_n = True

    # carrega folha caso não exista
    if not has_sheet_n:
        attach.sheets_data.append( {'number': n, 'path': TEST_PATH + ls} )
        
    flag_modified(attach, "sheets_data")  # Sqlalchemy JSON é imutável por default

    sess.commit()

    print(
            ac,  # activity_code
            tc,  # test_code
            ar,  # academic_register
            n,   # number
            ls,  # link_sheet
            st,  # submission_type
            cid  # calendar_id
          )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Carrega links de folhas de resposta de provas no SGA'
                                                 ' a partir de um CSV com as colunas: Cód. da disciplina,'
                                                 'Cód. da prova,RA do aluno,Número da folha,'
                                                 'Link do arquivo da folha de resposta')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV de folhas de resposta')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')

    args = parser.parse_args()

    arquivo = args.arquivo
    calendario = args.calendario
    tipo = args.tipo

    if args.tipo is not None:
        if args.tipo not in ['regular','dp']:
            print( 'Tipo de submissão deve ser regular ou dp' )
            sys.exit(1)
        tipo = args.tipo

    if not os.path.isfile(arquivo):
        print( 'Arquivo ' + arquivo + ' não encontrado!' )
        sys.exit(1)

    ####################
    # TO DO
    # percorre CSV
    ####################

    ####################
    # teste

    submission_type = 'regular'
    calendar_id = 38

    activity_code = 'AAG002'
    test_code = 'P001'
    academic_register = '1600311'
    number = 3
    link_sheet = 'SGA/provas/0001/20190425-0001-AAG002-P001-1600311-06.png'

    carregaFolha( 
                  activity_code,     # str, Cód. da disciplina
                  test_code,         # str, Cód. da prova
                  academic_register, # str, RA do aluno
                  number,            # int, Número da folha
                  link_sheet,        # str, Link do arquivo da folha de resposta
                  submission_type,   ### str, Tipo da submissão
                  calendar_id        ### int, ID do calendário
                )

    ####################

