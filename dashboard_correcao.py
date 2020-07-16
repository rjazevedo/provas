#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" Gera dashboard com status de correcao de provas e status de facilitadores"""

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
class Corretores:
    def __init__(self, campos):
        self.email = campos[15]
        self.disciplina = campos[1]
        self.aCorrigir = 0
        self.anulada = 0
        self.ausente = 0
        self.anulada_ausente = 0
        self.corrigida = 0
        self.ilegiveis = 0
        self.total = 1
    def SomaACorrigir(self):
        self.aCorrigir += 1
    def SomaAnulada(self):
        self.anulada += 1
    def SomaAusente(self):
        self.ausente += 1
    def SomaAnuladaAusente(self):
        self.anulada_ausente += 1
    def SomaCorrigidas(self):
        self.corrigida += 1
    def SomaIlegiveis(self):
        self.ilegiveis += 1
    def SomaTotal(self):
        self.total += 1
    def ShowDisciplina(self):
        return self.disciplina
    def ShowEmail(self):
        return self.email
    def GeraLinhaCompleta(self):
        if self.email == None:
            self.email = "reverificar"            
        return '<tr><td>' + self.email \
                + '</td><td>' + str(self.ausente) \
                + '</td><td>' + str(self.anulada) \
                + '</td><td>' + str(self.ilegiveis) \
                + '</td><td>' + str(self.anulada_ausente) \
                + '</td><td>' + str(self.aCorrigir) \
                + '</td><td>' + str(self.corrigida) \
                + '</td><td>' + str(self.total) \
                + '</td><td>' + '{:05.2f}'.format((1.0 - float(self.aCorrigir/self.total))* 100.0) + '% </td></tr>\n'
    def GeraLinha(self):
        if self.email == None:
            self.email = "reverificar"
        return '<tr><td>' + self.email \
                + '</td><td>' + str(self.aCorrigir) \
                + '</td><td>' + '{:05.2f}'.format((1.0 - float(self.aCorrigir/self.total))* 100.0) + '% </td></tr>\n'
    def GeraLinhaCSV(self):
        if self.email == None:
            self.email = "reverificar"
        return self.email + ',' + str(self.aCorrigir)
    def ExportaCorretoresComPendencias(self,facilitadores):
        if self.aCorrigir != 0:
            if self.email == "reverificar":
                return "sem corretor" + "," + str(self.aCorrigir) + "," + "-" + "\n"
            else:                
                return self.email + "," + str(self.aCorrigir) + "," + facilitadores[self.email].ShowStatus() + "\n"
        else:
            return ""
class Facilitadores:
    def __init__(self,campos):
        self.email = campos[0]
        self.nome = campos[1]
        self.status = campos[3]
    def ShowEmail(self):
        return self.email
    def ShowStatus(self):
        return self.status
    def GeraLinhaHTML(self):
        return '<tr><td>' + self.email + '</td><td>' + self.status + '</td></tr>\n'
    def GeraLinhaCSV(self):
        return self.email + ',' + self.nome + ',' + self.status + '\n'
def GeraDashboardDisciplinasCorretores(conjuntoCorretor,conjuntoDisciplinas,conjuntoFacilitador,saida):
    html_disciplinas = {}
    html_arquivo = {}
    
    header = open(os.path.join(os.path.dirname(sys.argv[0]), 'header.html')).read()
    footer = open(os.path.join(os.path.dirname(sys.argv[0]), 'footer.html')).read()
    resumo_csv = open(os.path.join(saida,'resumo.csv'), 'wt')
    resumo_csv.write("Disciplina,Email,Pendências,Status\n")
    
    sufixo_arquivos = "-correcoes.html"
        
    for d in conjuntoDisciplinas:
        html_disciplinas[d] = ""
        html_arquivo[d] = open(os.path.join(saida, d + sufixo_arquivos), 'wt')
        
    for c in conjuntoCorretor:
        html_disciplinas[conjuntoCorretor[c].ShowDisciplina()] += conjuntoCorretor[c].GeraLinha()
        if conjuntoCorretor[c].ShowEmail() == "reverificar":
            resumo_csv.write(conjuntoCorretor[c].ShowDisciplina() + "," + conjuntoCorretor[c].GeraLinhaCSV() + ",-\n" )
        else:
            resumo_csv.write(conjuntoCorretor[c].ShowDisciplina() + "," + conjuntoCorretor[c].GeraLinhaCSV() + "," + conjuntoFacilitador[conjuntoCorretor[c].ShowEmail()].ShowStatus() + "\n" )
    for d in conjuntoDisciplinas:
        modificado_header = header.replace("</ul>","<li><li class=\"active\"><a href=\"" + d + sufixo_arquivos +"\">" + d + "-Corre&ccedil;&otilde;es" + "</a></li><li><a href=\"correcao.html\">Voltar</a></li></ul>")
        html_arquivo[d].write(modificado_header)
        html_arquivo[d].write('<div class="row"><br><br><br><h4>' + d + "-" + conjuntoDisciplinas[d] + ' - Gerado em: ' + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") + '</h4></div>')
        #html_arquivo[d].write('<thead><tr><th>Email</th><th>Ausentes</th><th>Anuladas</th><th>Ileg&iacute;vel</th><th>Ausente &amp; anulada</th><th>Falta corrigir</th><th>Corrigido</th><th>Total</th><th>Percentual</th></tr></thead><tbody>\n') - relatorio completo
        html_arquivo[d].write('<thead><tr><th>Email</th><th>Falta corrigir</th><th>Percentual Corrigido</th></tr></thead><tbody>\n')
        html_arquivo[d].write(html_disciplinas[d])
        html_arquivo[d].write(footer)
        html_arquivo[d].close()
    resumo_csv.close()

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
                + '</td><td>' + self.aluno.title() \
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
            cursor.execute( consulta_part[0] + args.calendario + consulta_part[1] + args.tipo + consulta_part[2] )
            
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
        
        provas_ilegiveis = {}
        pp_ilegiveis = {}
        corretores = {}
        
        
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
            #Objeto de corretores
            if r[15] == None:
                chave_corretores = r[1] + "sem-Corretor"
            else:
                chave_corretores = r[1] + r[15]
                
            if (chave_corretores in corretores):
                corretores[chave_corretores].SomaTotal()
                if r[12] == "A Corrigir":
                    corretores[chave_corretores].SomaACorrigir()
                elif r[12] == "Prova anulada":
                    corretores[chave_corretores].SomaAnulada()
                elif r[12] == "Aluno ausente":
                    corretores[chave_corretores].SomaAusente()
                elif r[12] == "Aluno ausente / Prova anulada":
                    corretores[chave_corretores].SomaAnuladaAusente()
                elif r[12] == "Corrigido":
                    corretores[chave_corretores].SomaCorrigidas()
                elif r[12] == "Prova Ilegível":
                    corretores[chave_corretores].SomaIlegiveis()
                    provas_ilegiveis[r[1] + str(r[3])] = (ProvasIlegiveis(r))
            else:
                corretores[chave_corretores] = (Corretores(r))
                if r[12] == "A Corrigir":
                    corretores[chave_corretores].SomaACorrigir()
                elif r[12] == "Prova anulada":
                    corretores[chave_corretores].SomaAnulada()
                elif r[12] == "Aluno ausente":
                    corretores[chave_corretores].SomaAusente()
                elif r[12] == "Aluno ausente / Prova anulada":
                    corretores[chave_corretores].SomaAnuladaAusente()
                elif r[12] == "Corrigido":
                    corretores[chave_corretores].SomaCorrigidas()
                elif r[12] == "Prova Ilegível":
                    corretores[chave_corretores].SomaIlegiveis()
                    provas_ilegiveis[r[1] + str(r[3])] = (ProvasIlegiveis(r))

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
        #Gera a consulta do status dos facilitadores
        consulta = open(os.path.join(os.path.dirname(sys.argv[0]), 'query_status_facilitador.txt')).read()
        cursor.execute(consulta)
        record = cursor.fetchall()
        
        facilitadores = {}
        
        for r in record:
            facilitadores[r[0]] = (Facilitadores(r))

        saida = open(os.path.join(args.saida,'correcao.html'), 'wt')
        header = open(os.path.join(os.path.dirname(sys.argv[0]), 'header.html')).read() 
        footer = open(os.path.join(os.path.dirname(sys.argv[0]), 'footer.html')).read()
        correcao_header = header.replace("<li><a href=\"correcao.html\"","<li class=\"active\"><a href=\"correcao.html\"")
        saida.write(correcao_header)
        total_pendencia = 0
        
        for x in disciplinas:
            total_pendencia += disciplinas_aCorrigir[x]
        
        
        saida.write('<br><br><br><h4>Gerado em: ' + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") +"  -- Faltam corrigir : " + str(total_pendencia) + ' provas.</h4>\n')
        saida.write('<thead><tr><th>C&oacute;digo</th><th>Disciplina</th><th>Ausentes</th><th>Anuladas</th><th>Ileg&iacute;vel</th><th>Ausente &amp; anulada</th><th>Falta corrigir</th><th>Corrigido</th><th>Total</th><th>Progresso</th></tr></thead><tbody>\n')
        
        for x, y in disciplinas.items():
            saida.write('<tr><td><a href="' + x + "-correcoes.html" + '">' + x  \
                + '</td><td>' + y  \
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
        ilegiveis_header = header.replace("<li><a href=\"ilegiveis.html\"","<li class=\"active\"><a href=\"ilegiveis.html\"")
        ilegiveis.write(ilegiveis_header)
        ilegiveis.write('<br><br><br><h4>Gerado em: ' + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") +'</h4>\n') 
        ilegiveis.write('<thead><tr><th>Polo</th><th>Nome</th><th>Disciplina</th><th>Nome</th><th>Prova</th><th>RA</th><th>Nome</th></tr></thead><tbody>\n')
        
        for p in provas_ilegiveis:
            ilegiveis.write(provas_ilegiveis[p].GeraLinha())
            
        ilegiveis.write(footer)
        ilegiveis.close()
        
        #Gera cada uma das sub-paginas de disciplinas X corretores
        GeraDashboardDisciplinasCorretores(corretores,disciplinas,facilitadores,args.saida)

        status_facilitadores_html = open(os.path.join(args.saida,'facilitadores.html'), 'wt')
        status_facilitadores_csv = open(os.path.join(args.saida,'facilitadores.csv'), 'wt')
        facilitadores_correcao_pendente_csv = open(os.path.join(args.saida,'facilitadores_correcao_pendente_csv.csv'), 'wt')
        facilitadores_correcao_pendente_csv.write("Email,Pendências,Status\n")
        status_facilitadores_html.write(header)
        status_facilitadores_html.write('<br><br><br><h4>Gerado em: ' + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S") +'</h4>\n')
        status_facilitadores_html.write('<thead><tr><th>Email</th><th>Status</th></tr></thead><tbody>\n')
        
        for c in corretores:
            facilitadores_correcao_pendente_csv.write(corretores[c].ExportaCorretoresComPendencias(facilitadores))
        
        
        for f in facilitadores:
            status_facilitadores_html.write(facilitadores[f].GeraLinhaHTML())
            status_facilitadores_csv.write(facilitadores[f].GeraLinhaCSV())
            
        status_facilitadores_html.write(footer)
        status_facilitadores_html.close()
        status_facilitadores_csv.close()
        facilitadores_correcao_pendente_csv.close()