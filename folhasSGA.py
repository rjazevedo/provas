#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Carrega o link de uma folha de resposta, de uma prova, de um aluno, no SGA"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Table, ForeignKey, or_
from sqlalchemy.orm import sessionmaker, relationship
import os
import sys
import argparse
import db
import datetime

args = None

offer_types = { 'regular': 1, 'dp': 2 }

def carregaFolha( 
                  ac,  # activity_code
                  tc,  # test_code
                  ar,  # academic_register
                  n,   # number
                  ls,  # link_sheet
                  st,  # submission_type
                  cid, # calendar_id
                ):

    """Carrega o link de uma folha de resposta, de uma prova, de um aluno, no SGA"""

    ####################
    # TO DO
    # Logs
    ####################

    # disciplina
    activity = db.session.query(db.CurricularActivities) \
                         .filter(db.CurricularActivities.code == ac) \
                         .first()

    # oferta
    offer = db.session.query(db.ActivityOffers) \
                      .filter(db.ActivityOffers.calendar_id == cid) \
                      .filter(db.ActivityOffers.offer_type == offer_types[st]) \
                      .first()

    # aluno
    student = db.session.query(db.Students).filter(db.Students.academic_register == ar).first()

    if not activity: return
    if not offer: return
    if not student: return

    # registro
    record = db.session.query(db.ActivityRecords) \
                       .filter(db.ActivityRecords.student_id == student.id) \
                       .filter(db.ActivityRecords.curricular_activity_id == activity.id) \
                       .filter(db.ActivityRecords.activity_offer_id == offer.id) \
                       .first()

    # prova
    test = db.session.query(db.ActivityTests) \
                     .filter(db.ActivityTests.code == tc) \
                     .filter(db.ActivityTests.curricular_activity_id == activity.id) \
                     .first()

    if not record: return
    if not test: return

    # submissão (cria uma caso não exista)
    submission = db.session.query(db.ActivityRecordSubmissions) \
                           .filter(db.ActivityRecordSubmissions.activity_record_id == record.id) \
                           .filter(db.ActivityRecordSubmissions.submission_type == st) \
                           .first()
    if not submission:
        submission = db.ActivityRecordSubmissions(
                                                    activity_record_id = record.id,
                                                    submission_type = st,
                                                    activity_test_id = test.id
                                                 )
        db.add(submission)
    else:
        submission.activity_test_id = test.id

    db.flush()

    # folha

    # TO DO




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Carrega o link de uma folha de resposta, de uma prova, de um aluno, no SGA')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV de folhas de resposta')
    parser.add_argument('-c', '--calendario', type=int , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
    parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular"')

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
    number = 1
    link_sheet = '/home/provas/dados/SGA/provas/0001/20190425-0001-AAG002-P001-1600311-01.png'

    carregaFolha( 
                  activity_code,     # Cód. da disciplina
                  test_code,         # Cód. da prova
                  academic_register, # RA do aluno
                  number,            # Número da folha
                  link_sheet,        # Link do arquivo da folha de resposta
                  submission_type,   ## Tipo da submissão
                  calendar_id        ## ID do calendário
                )

    ####################

