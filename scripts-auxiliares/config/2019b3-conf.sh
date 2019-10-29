#!/bin/bash
#Arquivos de cofiguração

#Backup de csv anteriores (Caminho Completo)
BACKUP_CSV="/home/provas/dados/backup/2019b3"
#Isso é invariavel, é uma base de busca de string
BASE_STRING="Dashboard Provas UNIVESP"
#Caso o bimestre tenha sido consolidado preencher "sim", caso contrario deixar em branco
BIMESTRE_CONSOLIDADO=""
#Calendario SGA
CALENDARIO="44"
CALENDARIO_DP="46"
#Data
DATA=$(date +%Y%m%d_%H-%M-%S)
#Destino de Dashboad
DESTINO_DASHBOARD="SGA/dashboard/2019b3"
#Caminho do arquivo de estrutura Ausentes
ESTRUTURA_AUSENTES="csv/2019b3/ausentes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_BASE_CORRECOES="csv/2019b3/baseCorrecoes.csv"
#Caminho do arquivo de estrutura Corretores
ESTRUTURA_CORRETORES="csv/2019b3/corretores.csv"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_CSV="csv/2019b3"
#Caminho do arquivo de estrutura Dashboad
ESTRUTURA_DASHBOARD="csv/2019b3/dashboard.csv"
#Caminho estrutura de guias
ESTRUTURA_GUIAS="SGA/2019b3/guias"
#Caminho do arquivo de estrutura Provas
ESTRUTURA_PROVAS="csv/2019b3/todasProvasJuntas.csv"
#Caminho do arquivo de gabaritos
GABARITO_PROVAS="csv/2019b3/GabaritoMultiplasEscolhas.csv"
#Diretorio de NFS
HOME_NFS="/home/provas/dados"
#Path para Home
HOME="/home/provas"
#Caminnho para Logs (caminho completo)
LOG="/home/provas/dados/log/2019b3"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_FIM="Script processaCorrecao 3o Bimestre de 2019 finalizado"
#Mensagem inicial do programa populaDB-Automatico
MSG_CORRECAO_AUTOMATICO_INICIO="Iniciando o processamento de Correção 3o Bimestre de 2019"
#Mensagem do programa dashboard"
MSG_DASH_INICIO="Inicio da geração do DashBoard - 3o Bimestre 2019"
#Mensagem de fim do Full Insertion
MSG_FULLINSERTION_FIM="Fim de PopulaDB Full Insertion - 3o Bimestre"
#Mensagem de inicio do Full Insertion
MSG_FULLINSERTION_INICIO="Inicio de PopulaDB Full Insertion - 3o Bimestre"
#Mensagem final do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_FIM="Fim da geração do PopulaDB Automatico - 3o Bimestre 2019"
#Mensagem inicial do programa populaDB-Automatico
MSG_POPULADB_AUTOMATICO_INICIO="Inicio da geração do PopulaDB Automatico - 3o Bimestre 2019"
#Mensagem inicial do programa populaDB
MSG_POPULADB_INICIO="Inicio da geração do PopulaDB - 3o Bimestre 2019"
#Caminho das provas
PATH_PROVAS="SGA/2019b3/provas"
#Path Completo de Saida (caminho completo)
SAIDA_CSV="/home/provas/dados/SGA/2019b3/provas/Saida"
#Personaliza com informações relativas ao periodo de referencia
SUBSTITUI_STRING=" - 3o Bimestre 2019"
#Indicacao do tipo de prova (regular,dp)
TIPO_PROVA="regular"
TIPO_PROVA_DP="dp"
#Nome da pasta temporaria de trabalho
TRABALHO_TMP="d3BIM2019"
