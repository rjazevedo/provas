#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Gera dashboard com status de correcao de provas"""

import argparse
import csv
import datetime
import json
import os
import psycopg2
import sys

def MostraPolo(codStr):
    return codStr[5:9]
def MostraCodigoProva(codStr):
    return codStr[0:4]
    
class ProvasIlegiveis:
    def __init__(self, campos):
        self.numeroPolo = MostraPolo(campos[2])
        self.nomePolo = campos[5]
        self.codigoDisciplina = campos[1]
        self.nomeDisciplina = campos[0]
        self.codigoProva = MostraCodigoProva(campos[2])
        self.ra = str(campos[3])
        self.aluno = campos[20]
    def GeraLinha(self):
        return '<tr><td>' + self.numeroPolo \
                + '</td><td>' + self.nomePolo \
                + '</td><td>' + self.codigoDisciplina \
                + '</td><td>' + self.nomeDisciplina \
                + '</td><td>' + self.codigoProva \
                + '</td><td>' + self.ra \
                + '</td><td>' + self.aluno \
                + '</td></tr>\n'

if __name__ == '__main__':
        parser = argparse.ArgumentParser(description='Gera um dashboard com status do banco de dados')
        parser.add_argument('-c', '--calendario', type=str , required=True, help='Id do Calendario (calendars.id no BD do SGA)')
        parser.add_argument('-t', '--tipo', required=False, default='regular', help='Tipo de submissão (default: "regular")')
        parser.add_argument('-s', '--saida', type=str, required=True, help='Pasta de saida')
        
        args = parser.parse_args()  

        conn = {}
        fileName = os.path.join(os.path.dirname(sys.argv[0]), 'dbpass-S.txt')
        with open(fileName, 'r') as file:
            conn = json.loads(file.read())

        connection = psycopg2.connect ( user = conn["user"], \
                                        password = conn["password"], \
                                        host = conn["host"], \
                                        port = conn["port"], \
                                        database = conn["database"] )
        
        cursor = connection.cursor()
        
        if "," in str(args.calendario) :
            consulta = open(os.path.join(os.path.dirname(sys.argv[0]), 'query-dashboard-dual.txt')).read()
            consulta_part = consulta.split("#")
            entrada_calendario = str(args.calendario)
            entrada_tipo = str(args.tipo)
            calendario_part = entrada_calendario.split(",")
            tipo_part = entrada_tipo.split(",")
            cursor.execute( consulta_part[0] + calendario_part[0] + consulta_part[1] + tipo_part[0] + consulta_part[2] + calendario_part[1] + consulta_part[3] + tipo_part[1] + consulta_part[4])
            
        else:
        
            consulta = open(os.path.join(os.path.dirname(sys.argv[0]), 'query-dashboard.txt')).read()
            consulta_part = consulta.split("#")       
            cursor.execute( consulta_part[0] + str(args.calendario) + consulta_part[1] + args.tipo + consulta_part[2] )
            
        record = cursor.fetchall()
        
        disciplinas = {}
        correcoes = {}
        
        disciplinas_aCorrigir = {}
        disciplinas_anulada = {}
        disciplinas_ausente = {}
        disciplinas_anulada_ausente = {}
        disciplinas_corrigida = {}
        disciplina_ilegiveis = {}
        disciplinas_total = {}
        
        provas_ilegiveis = []
        
        for r in record:
            disciplinas[r[1]] = r[0]
            correcoes[r[1] + str(r[3])] = r[12]
            disciplinas_aCorrigir[r[1]] = 0
            disciplinas_anulada[r[1]] = 0
            disciplinas_ausente[r[1]] = 0
            disciplinas_anulada_ausente[r[1]] = 0
            disciplinas_corrigida[r[1]] = 0
            disciplina_ilegiveis[r[1]] = 0
            disciplinas_total[r[1]] = 0
            if r[12] == "Prova Ilegível":
                provas_ilegiveis.append(ProvasIlegiveis(r))

        for x,y in correcoes.items():
            disciplinas_total[x[:6]] += 1
            if y == "A Corrigir":
                disciplinas_aCorrigir[x[:6]] += 1
            elif y == "Prova anulada":
                disciplinas_anulada[x[:6]] += 1
            elif y == "Aluno ausente":
                disciplinas_ausente[x[:6]] += 1
            elif y == "Aluno ausente / Prova anulada":
                disciplinas_anulada_ausente[x[:6]] += 1
            elif y == "Corrigido":
                disciplinas_corrigida[x[:6]] += 1
            elif y == "Prova Ilegível":
                disciplina_ilegiveis[x[:6]] += 1

        saida = open(os.path.join(args.saida,'correcao.html'), 'wt')
        header = open(os.path.join(os.path.dirname(sys.argv[0]), 'header.html')).read() 
        footer = open(os.path.join(os.path.dirname(sys.argv[0]), 'footer.html')).read()
        saida.write(header)
        saida.write('<h4>Gerado em: ' + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") +'</h4>\n')        
        saida.write('<h3><a href="ilegiveis.html">Provas ileg&iacuteis;ge</a></h3>')       
        
        saida.write('<thead><tr><th>C&oacute;digo</th><th>Disciplina</th><th>Ausentes</th><th>anuladas</th><th>Ileg&iacute;vel</th><th>Ausente &amp; anulada</th><th>Falta corrigir</th><th>Corrigido</th><th>Total</th><th>Percentual</th></tr></thead><tbody>\n')
        
        for x, y in disciplinas.items():
            saida.write('<tr><td>' + x \
                + '</td><td>' + y \
                + '</td><td>' + str(disciplinas_ausente[x]) \
                + '</td><td>' + str(disciplinas_anulada[x]) \
                + '</td><td>' + str(disciplina_ilegiveis[x]) \
                + '</td><td>' + str(disciplinas_anulada_ausente[x]) \
                + '</td><td>' + str(disciplinas_aCorrigir[x]) \
                + '</td><td>' + str(disciplinas_corrigida[x]) \
                + '</td><td>' + str(disciplinas_total[x]) \
                + '</td><td>' + '{:05.2f}'.format((1.0 - float(disciplinas_aCorrigir[x]/disciplinas_total[x]))* 100.0) + '% </td></tr>\n')
                
        saida.write(footer)
        saida.close()
        
        ilegiveis = open(os.path.join(args.saida,'ilegiveis.html'), 'wt')
        ilegiveis.write(header)
        ilegiveis.write('<h3>Gerado em: ' + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") +'</h3>\n')
        ilegiveis.write('<thead><tr><th>Polo</th><th>Nome</th><th>Disciplina</th><th>Nome</th><th>Prova</th><th>RA</th><th>Nome</th></tr></thead><tbody>\n')
        
        for p in provas_ilegiveis:
            ilegiveis.write(p.GeraLinha())

        ilegiveis.write(footer)
        ilegiveis.close()
