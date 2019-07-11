#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Modelo de dados do SGA"""

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, JSON, Table, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import os
import sys
import argparse
import db
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Estatística das Notas das Disciplinas.')
    parser.add_argument('-p', '--periodo', type=str, required=False, help='Seleciona apenas um período de oferta das disciplinas')
    parser.add_argument('-l', '--listaPeriodo', action='store_true', required=False, help='Lista todos os períodos de oferta de disciplinas')

    args = parser.parse_args()

    if args.listaPeriodo:
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

    if args.periodo is not None:
        ao = db.session.query(db.ActivityOffers).filter(db.ActivityOffers.offer_date == args.periodo)

        pdf1 = PdfPages('estatistica-notas-' + args.periodo + '.pdf')
        pdf2 = PdfPages('estatistica-resumo-' + args.periodo + '.pdf')

        dados = []

        for offer in ao:
            histograma = [0] * 12
            for d in offer.activity_records:
                if d.grade_total != None and d.grade_total >= 0 and d.grade_total <= 10:
                    histograma[int(d.grade_total)] += 1
                else:
                    histograma[11] += 1
            print(offer.curricular_activity, histograma)
            x = list(range(0, 11))
            plt.bar(x, histograma[0:11])
            plt.title(offer.curricular_activity)
            plt.xticks(np.arange(0, 11, 1))
            pdf1.savefig()
            plt.close()

            x = ['Reprovados', 'Aprovados', 'Sem Informação']
            reprovado = sum(histograma[0:5])
            aprovado = sum(histograma[5:11])
            semInformacao = histograma[11]
            y = [aprovado, reprovado, semInformacao]
            plt.bar(x, y)
            plt.title(offer.curricular_activity)
            pdf2.savefig()
            plt.close()

            total = aprovado + reprovado + semInformacao
            if total < 100:
                continue

            dados.append([aprovado / total * 100, reprovado / total * 100, semInformacao / total * 100, offer.curricular_activity.code])

        pdf1.close()
        pdf2.close()

        pdf3 = PdfPages('estatistica-tudo-' + args.periodo + '.pdf')

        dados.sort()

        for i in range(0, len(dados), 20):
            elementos = [e for e in dados[i:i+20]]
            codigos = [c for [a, r, s, c] in elementos]
            aprovados = [a for [a, r, s, c] in elementos]
            reprovados = [r for [a, r, s, c] in elementos]
            semInformacoes = [s for [a, r, s, c] in elementos]
            baseSI = [a + r for [a, r, s, c] in elementos]

            # plt.stackplot(codigos, aprovados, reprovados)
            p1 = plt.bar(codigos, aprovados)
            p2 = plt.bar(codigos, reprovados, bottom=aprovados)
            p3 = plt.bar(codigos, semInformacoes, bottom=baseSI)
            plt.xticks(codigos, rotation='45')
            plt.yticks(np.arange(0, 101, 10))
            #plt.set_ylabel('Porcentagem de alunos')
            plt.title('Distribuição de resultados por disciplinas')
            plt.legend((p1[0], p2[0], p3[0]), ('Aprovados', 'Reprovados', 'Sem Informação'))
            pdf3.savefig()
            plt.close()

        pdf3.close()



