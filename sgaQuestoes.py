#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Cria registros de questões de provas no SGA a partir de um CSV:
Cód. da disciplina,Cód. da prova,Número da questão,Tipo da questão,Peso da questão"""

####################################################
# Uso: sgaQuestoes.py -a questoes.csv
#
# o arquivo dbpass.txt deve estar no diretório
#
# Corresponde à: CreateSubmissionsTestQuestionsFromCSV
####################################################

from sqlalchemy import func
import os
import sys
import argparse
import db
import csv

args = None

def erro( str ):
    print( "Erro: " + str )

def format_question_type( t ):
    lt = t.lower()
    if lt == 'objetiva': return 'objective'
    if lt == 'dissertativa': return 'essay'
    return ''

def carregaQuestao( 
                    ac,  # activity_code
                    tc,  # test_code
                    nq,  # number of question
                    tq,  # type of question
                    wq   # weight of question
                  ):

    """Cria registros de questões de provas no SGA"""

    print(  
            "Tenta criar registro de questao: ",
            ac,  # activity_code
            tc,  # test_code
            nq,  # number of question
            tq,  # type of question
            wq   # weight of question
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

    # prova
    test = sess.query(db.ActivityTests) \
               .filter(db.ActivityTests.code == tc) \
               .filter(db.ActivityTests.curricular_activity_id == activity.id) \
               .first()

    if not test:
      erro( "Missing ActivityTests: %s, %d" % (tc, activity.id) )
      return

    # questão (cria uma caso não exista)
    question = sess.query(db.ActivityTestQuestions) \
                   .filter(db.ActivityTestQuestions.activity_test_id == test.id) \
                   .filter(db.ActivityTestQuestions.number == nq) \
                   .first()
    if not question:
        question = db.ActivityTestQuestions(
                                            activity_test_id = test.id, 
                                            number = nq,
                                            created_at = func.now(),
                                            updated_at = func.now()
                                           )
        sess.add(question)

    question.question_type = format_question_type(tq)
    question.weight = wq
    question.annulled = False
    sess.commit()
    sess.close()

    print( "Sucesso!" )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cria registros de questões de provas no SGA a partir de um CSV:'
                                                 ' Cód. da disciplina,Cód. da prova,Número da questão, Tipo da questão,'
                                                 ' Peso da questãoCria registros de provas e guias de correção no SGA')
    parser.add_argument('-a', '--arquivo', type=str, required=True, help='Arquivo CSV de questões')

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
            carregaQuestao(
                            row[0],       # str, Cód. da disciplina
                            row[1],       # str, Cód. da prova
                            int(row[2]),  # int, Número da questão
                            row[3],       # str, Tipo da questão
                            float(row[4]) # float, Peso da questão
                          )
