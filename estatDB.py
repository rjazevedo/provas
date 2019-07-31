#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Modelo de dados do SGA"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Table, ForeignKey, or_
from sqlalchemy.orm import sessionmaker, relationship
import os
import sys
import argparse
import db
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime

args = None

def ListaPeriodos():
    ao = db.session.query(db.ActivityOffers).all()
    periodos = {}
    i = 0
    for a in ao:
        periodos[a.offer_date] = True
        i += 1

    print(i, 'disciplinas ofertadas.')
    print('Ofertas de disciplinas cadastradas nos seguintes períodos:')

    for p in sorted(periodos.keys()):
        ao = db.session.query(db.ActivityOffers).filter(db.ActivityOffers.offer_date == p).count()
        print(p, '-', ao)
    
    return


def PorDisciplina(offer, pdfNotas, pdfResumo):

    # Olhar este exemplo para fazer horizontal: 
    # https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/horizontal_barchart_distribution.html#sphx-glr-gallery-lines-bars-and-markers-horizontal-barchart-distribution-py

    histograma = [0] * 15
    for d in offer.activity_records:
        if d.grade_total != None and d.grade_total >= 0 and d.grade_total <= 10 and (d.status == 3 or d.status == 4):
            histograma[int(d.grade_total)] += 1
        elif d.status == 5:
            histograma[11] += 1
        elif d.status == 6:
            histograma[12] += 1
        elif d.status == 7:
            histograma[13] += 1
        else:
            histograma[14] += 1

    reprovado = sum(histograma[0:5])
    aprovado = sum(histograma[5:11])
    trancado = histograma[11]
    aproveitamento = histograma[12]
    proficiencia = histograma[13]
    semInformacao = histograma[14]

    total = aprovado + reprovado + trancado + aproveitamento + proficiencia + semInformacao
    if total >= args.minimo:
        print('  ', offer.offer_date, offer.curricular_activity, histograma)
        x = list(range(0, 11))
        plt.bar(x, histograma[0:11])
        plt.title(offer.offer_date + ' - ' + str(offer.curricular_activity))
        plt.xticks(np.arange(0, 11, 1))
        pdfNotas.savefig()
        plt.close()

        y = [aprovado, reprovado, trancado, aproveitamento, proficiencia, semInformacao]
        x = ['Aprov.', 'Reprov.', 'Tranc.', 'Aproveit.', 'Prof.', 'Sem Informação']
        plt.bar(x, y)
        plt.title(offer.offer_date + ' - ' + str(offer.curricular_activity))
        pdfResumo.savefig()
        plt.close()

        return [aprovado / total * 100, reprovado / total * 100, trancado / total * 100, \
            aproveitamento / total * 100, proficiencia / total * 100, \
            semInformacao / total * 100, offer.curricular_activity.code, total]
    else:
        if total == 0:
            total = 1

        return [aprovado / total * 100, reprovado / total * 100, trancado / total * 100, \
            aproveitamento / total * 100, proficiencia / total * 100, \
            semInformacao / total * 100, offer.curricular_activity.code, total]



def PorPeriodo(periodo):
    ao = db.session.query(db.ActivityOffers).filter(db.ActivityOffers.offer_date == periodo, or_(db.ActivityOffers.status == 3, db.ActivityOffers == 4))

    pdf1 = PdfPages('estatistica-notas-' + periodo + '.pdf')
    pdf2 = PdfPages('estatistica-resumo-' + periodo + '.pdf')

    dados = []

    for offer in ao:
        resultado = PorDisciplina(offer, pdf1, pdf2)
        if resultado[-1] >= args.minimo:
            dados.append(resultado)

    pdf1.close()
    pdf2.close()

    pdf3 = PdfPages('estatistica-tudo-' + periodo + '.pdf')

    dados.sort()

    for i in range(0, len(dados), 20):
        elementos = [e for e in dados[i:i+20]]
        codigos = [c for [a, r, t, ae, p, s, c, n] in elementos]
        aprovados = [a for [a, r, t, ae, p, s, c, n] in elementos]
        reprovados = [r for [a, r, t, ae, p, s, c, n] in elementos]
        trancados = [t for [a, r, t, ae, p, s, c, n] in elementos]
        aproveitamentos = [ae for [a, r, t, ae, p, s, c, n] in elementos]
        proficiencias = [p for [a, r, t, ae, p, s, c, n] in elementos]
        semInformacoes = [s for [a, r, t, ae, p, s, c, n] in elementos]
        baseT = [a + r for [a, r, t, ae, p, s, c, n] in elementos]
        baseAE = [a + r + t for [a, r, t, ae, p, s, c, n] in elementos]
        baseP = [a + r + t + ae for [a, r, t, ae, p, s, c, n] in elementos]
        baseSI = [a + r + t + ae for [a, r, t, ae, p, s, c, n] in elementos]

        # plt.stackplot(codigos, aprovados, reprovados)
        p1 = plt.bar(codigos, aprovados)
        p2 = plt.bar(codigos, reprovados, bottom=aprovados)
        p3 = plt.bar(codigos, trancados, bottom=baseT)
        p4 = plt.bar(codigos, aproveitamentos, bottom=baseAE)
        p5 = plt.bar(codigos, proficiencias, bottom=baseP)
        p6 = plt.bar(codigos, semInformacoes, bottom=baseSI)

        plt.xticks(codigos, rotation='45')
        plt.yticks(np.arange(0, 101, 10))
        plt.ylabel('Porcentagem de alunos')
        plt.title('Distribuição de resultados por disciplinas')
        plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0]), ('Aprovados', 'Reprovados', 'Trancados', 'Aproveitamento', 'Proficiência', 'Sem Informação'))
        pdf3.savefig()
        plt.close()

    pdf3.close()


def TodasDisciplinas():
# Seguem os status da tabela activity_records (Registros de disciplina):

# 0 = matriculado
# 1 = aguardando nota (caiu em desuso nesse 1º semestre/2019)
# 2 = nota recebida (em desuso)
# 3 = aprovado
# 4 = reprovado
# 5 = trancado
# 6 = aproveitamento de estudo
# 7 = exame de proficiência (basicamente, Aproveitamento de Estudo para disciplinas de Inglês)
    ca = db.session.query(db.CurricularActivities).all()

    dados = []

    for disciplina in ca:
        print(disciplina)

        # if disciplina.code != 'TTG002':
        #     continue
            
        pdfDisciplina = PdfPages('estatistica-disciplina-notas-' + disciplina.code + '.pdf')
        pdfResumo = PdfPages('estatistica-disciplina-resumo-' + disciplina.code + '.pdf')

        for offer in disciplina.activity_offers:
            resultado = PorDisciplina(offer, pdfDisciplina, pdfResumo)
            resultado[-2] = offer.offer_date
            if resultado[-1] >= args.minimo:
                dados.append(resultado)

        pdfDisciplina.close()
        pdfResumo.close()

        pdf3 = PdfPages('estatistica-tudo-' + disciplina.code + '.pdf')

        dados.sort()

        for i in range(0, len(dados), 20):
            elementos = [e for e in dados[i:i+20]]
            codigos = [c for [a, r, t, ae, p, s, c, n] in elementos]
            aprovados = [a for [a, r, t, ae, p, s, c, n] in elementos]
            reprovados = [r for [a, r, t, ae, p, s, c, n] in elementos]
            trancados = [t for [a, r, t, ae, p, s, c, n] in elementos]
            aproveitamentos = [ae for [a, r, t, ae, p, s, c, n] in elementos]
            proficiencias = [p for [a, r, t, ae, p, s, c, n] in elementos]
            semInformacoes = [s for [a, r, t, ae, p, s, c, n] in elementos]
            baseT = [a + r for [a, r, t, ae, p, s, c, n] in elementos]
            baseAE = [a + r + t for [a, r, t, ae, p, s, c, n] in elementos]
            baseP = [a + r + t + ae for [a, r, t, ae, p, s, c, n] in elementos]
            baseSI = [a + r + t + ae for [a, r, t, ae, p, s, c, n] in elementos]

            # plt.stackplot(codigos, aprovados, reprovados)
            p1 = plt.bar(codigos, aprovados)
            p2 = plt.bar(codigos, reprovados, bottom=aprovados)
            p3 = plt.bar(codigos, trancados, bottom=baseT)
            p4 = plt.bar(codigos, aproveitamentos, bottom=baseAE)
            p5 = plt.bar(codigos, proficiencias, bottom=baseP)
            p6 = plt.bar(codigos, semInformacoes, bottom=baseSI)

            plt.xticks(codigos, rotation='45')
            plt.yticks(np.arange(0, 101, 10))
            plt.ylabel('Porcentagem de alunos')
            plt.title('Distribuição de resultados por disciplinas')
            plt.legend((p1[0], p2[0], p3[0], p4[0], p5[0], p6[0]), ('Aprovados', 'Reprovados', 'Trancados', 'Aproveitamento', 'Proficiência', 'Sem Informação'))
            pdf3.savefig()
            plt.close()

        pdf3.close()


def ListaCursos():
    cursos = db.session.query(db.Courses)

    for curso in cursos:
        print(curso)
        for catalog in curso.catalogs:
            q1 = db.session.query(db.AcademicRecords).filter(db.AcademicRecords.course_catalog_id == catalog.id).count()
            q2 = db.session.query(db.AcademicRecords).filter(db.AcademicRecords.course_catalog_id == catalog.id) \
                    .filter(db.AcademicRecords.date_conclusion == None) \
                    .filter(db.AcademicRecords.date_graduation == None) \
                    .filter(db.AcademicRecords.date_complete_withdrawal == None) \
                    .filter(db.AcademicRecords.date_deregistration == None).count()
            print(' -', catalog, '(', q1, ',', q2, ')')


def ListaCatalogo(c):
    catalogo = db.session.query(db.CourseCatalogs).filter(db.CourseCatalogs.code == c).one()

    lista = []
    disciplinas = {}
    ch = 0
    for atividade in catalogo.curriculums:
        lista.append((atividade.semester, atividade.period, atividade.curricular_activity.workload, str(atividade.curricular_activity)))
        ch += atividade.curricular_activity.workload
        disciplinas[atividade.curricular_activity_id] = atividade.curricular_activity.workload

    lista.sort()

    # print('Catálogo:', c)
    # for l in lista:
    #     print(*l)

    print(ch, 'horas totais no curso.')

    quantidade = db.session.query(db.AcademicRecords).filter(db.AcademicRecords.course_catalog_id == catalogo.id).count()
    print(quantidade, 'alunos totais.')

    quantidade2 = db.session.query(db.AcademicRecords).filter(db.AcademicRecords.course_catalog_id == catalogo.id) \
                    .filter(db.AcademicRecords.date_conclusion == None) \
                    .filter(db.AcademicRecords.date_graduation == None) \
                    .filter(db.AcademicRecords.date_complete_withdrawal == None) \
                    .filter(db.AcademicRecords.date_deregistration == None).count()

    print(quantidade2, 'alunos ativos.')

    ars = db.session.query(db.AcademicRecords).filter(db.AcademicRecords.course_catalog_id == catalogo.id) \
                    .filter(db.AcademicRecords.date_conclusion == None) \
                    .filter(db.AcademicRecords.date_graduation == None) \
                    .filter(db.AcademicRecords.date_complete_withdrawal == None) \
                    .filter(db.AcademicRecords.date_deregistration == None)

    data = []
    idades = []
    for ar in ars:
        if ar.student.user.birth_date != None:
            idades.append(datetime.date.today().year - ar.student.user.birth_date.year)
        ch = 0
        for activity in ar.student.activity_records:
            if (activity.status == 3 or activity.status == 6 or activity.status == 7) and activity.curricular_activity_id in disciplinas:
                ch += disciplinas[activity.curricular_activity_id]
        data.append(ch)

    pdfCatalogo = PdfPages('estatistica-catalogo-' + c + '.pdf')

    dataArray = np.array(data)
    plt.hist(dataArray, bins=20)
    plt.ylabel('Quantidade de alunos')
    plt.xlabel('Carga horária cumprida no curso')
    plt.title('Histograma de alunos por progressão: ' + c)
    pdfCatalogo.savefig()
    plt.close()

    pdfCatalogo.close()

    pdfIdade = PdfPages('estatistica-idades-' + c + '.pdf')

    idadesArray = np.array(idades)
    plt.hist(idadesArray, bins=20)
    plt.ylabel('Quantidade de alunos')
    plt.xlabel('Faixa etária')
    plt.title('Distribuição de faixa etária: ' + c)
    pdfIdade.savefig()
    plt.close()

    pdfIdade.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Estatística das Notas das Disciplinas.')
    parser.add_argument('-p', '--periodo', type=str, required=False, help='Seleciona apenas um período de oferta das disciplinas')
    parser.add_argument('-lp', '--listaPeriodos', action='store_true', required=False, help='Lista todos os períodos de oferta de disciplinas')
    parser.add_argument('-lc', '--listaCursos', action='store_true', required=False, help='Lista todos os cursos')
    parser.add_argument('-t', '--todas', action='store_true', required=False, help='Gera as estatísticas para todas as disciplinas para todas as ofertas')
    parser.add_argument('-m', '--minimo', type=int, required=False, help='Número mínimo de alunos para considerar para cada oferta de disciplina')
    parser.add_argument('-c', '--catalogo', type=str, required=False, help='Seleciona um catálogo específico')

    args = parser.parse_args()

    if args.minimo is None:
        args.minimo = 1

    if args.listaPeriodos:
        ListaPeriodos()

    if args.periodo is not None:
        PorPeriodo(args.periodo)

    if args.todas:
        TodasDisciplinas()

    if args.listaCursos:
        ListaCursos()

    if args.catalogo is not None:
        ListaCatalogo(args.catalogo)
