#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import db
import os
from sqlalchemy.orm.attributes import flag_modified

quantidade = 0
# folha_nao_digitalizada = '/var/data/nfs/provas/SGA/folha-nao-digitalizada.png'

for att in db.session.query(db.Attachments).all():
    if att.sheets_data is not None:
        modificado = False
        for pageInfo in att.sheets_data:
            if pageInfo['path'].startswith('/var/data/nfs/provas//home/provas/dados/SGA/2019b3/provas/'): 
                arquivo = pageInfo['path'].replace('/home/provas/dados/', '')
                print(pageInfo['path'], '--->', arquivo)
                pageInfo['path'] = arquivo
                modificado = True
            
        if modificado:
            flag_modified(att, "sheets_data")
            db.session.commit()
            print('Atualizado')
