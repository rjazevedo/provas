#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import sys
import argparse
# import gspread

def GetTokens(verbose = True):
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly', 'https://www.googleapis.com/auth/spreadsheets.readonly']
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('segredo.json', SCOPES)
        creds = tools.run_flow(flow, store)
    DRIVE = discovery.build('drive', 'v3', http=creds.authorize(Http()))
    
    service = discovery.build('sheets', 'v4', credentials=creds)
    # Call the Sheets API
    SHEET = service.spreadsheets()
    
    # SHEET = gspread.authorize(creds)

    return (DRIVE, SHEET)

def GetDriveRoot(DRIVE, verbose = True):
    id = ''
    if verbose:
        print('Pasta raiz:')
    files = DRIVE.files().list(q="name = 'Provas_root' and mimeType = 'application/vnd.google-apps.folder'").execute().get('files', [])
    for f in files:
        if verbose:
            print(f['name'], f['id'])
        id = f['id']
        
    return id

def GetPastasPeriodos(DRIVE, id_root, verbose = True):
    ids = []
    if verbose:
        print('Pastas dos períodos de aplicação:')
    files = DRIVE.files().list(q="name contains '2020' and '" + id_root + "' in parents and mimeType = 'application/vnd.google-apps.folder'").execute().get('files', [])
    for f in files:
        if verbose:
            print(f['name'], f['id'])
        ids.append(f)
    return ids

def GetPastasProvas(DRIVE, id_bimestre, verbose = True): 
    if verbose:   
        print('Pastas de provas')
    pastas = []
    query = "'" + id_bimestre + "' in parents and mimeType = 'application/vnd.google-apps.folder'"
    files = DRIVE.files().list(q=query).execute().get('files', [])
    provas = []
    for f in files:
        if verbose:
            print(f['name'], f['id'])
        provas.append(f)
    return provas


def GetPastaProva(DRIVE, id_root, nome_prova, verbose = True):
    if verbose:   
        print('Procurando pasta da prova:', nome_prova)
    query = "'" + id_root + "' in parents and name contains '" + nome_prova + "' and mimeType = 'application/vnd.google-apps.folder'"
    files = DRIVE.files().list(q=query).execute().get('files', [])
    for f in files:
        if f['name'] == nome_prova:
            return f['id']
    return ''


def GetPlanilhaRespostas(DRIVE, SHEET, prova, verbose = True):
    root = GetDriveRoot(DRIVE, verbose)
    periodos = GetPastasPeriodos(DRIVE, root, verbose)
    provas = []
    for p in periodos:
        if verbose:
            print(p['name'])
        provas.extend(GetPastasProvas(DRIVE, p['id'], verbose))
        
    prova_escolhida = []
    for p in provas:
        if p['name'] == prova:
            prova_escolhida = p
            break
            
    if prova_escolhida is None:
        print('Planilha de resposta da prova não encontrada', prova)
        return None
    
    print('Prova', prova_escolhida['name'], 'encontrada. Id:', prova_escolhida['id'])
    
    if verbose:
        print('Planilha da prova')
    query = "'" + prova_escolhida['id'] + "' in parents and mimeType = 'application/vnd.google-apps.spreadsheet'"
    files = DRIVE.files().list(q=query).execute().get('files', [])
    if verbose:
        for f in files:
            print(f['name'], f['id'])

    if len(files) > 1:
        if verbose:
            print('Deveria ter um arquivo apenas, encontrei', len(files), ' e vou retornar o primeiro.')
        id_planilha = files[0]['id']
    elif len(files) == 1:
        id_planilha = files[0]['id']
    else:
        print('Não encontrei planilha com respostas')
        return None

    return (id_planilha, SHEET.get(spreadsheetId=id_planilha).execute())