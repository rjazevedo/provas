#!/bin/bash
#Objetivo: Processamento de provas 4Bimestre, incluindo a correção para todas as particularidades e ocorrencias
#Data Criacao:09-abr-2020
#Autor: Daniel Consiglieri
#Data Ultima alteracao: 16-jun-2020

source ~/src/scripts-auxiliares/config/2019b4-conf.sh

#Direcionamento do logbest.txt
cd ${LOG}

#Correcao de caderno respostas nao correspondente a guia
for i in $( find ${HOME_NFS}/${PATH_PROVAS} -iname '*20200303*STA001*P006*png' );
do
	echo -e "mv ${i} ${i/-P006/-P010}" >> ${LOG}/log_arquivosRenomeados_${DATA}.log
	mv ${i} ${i/-P006/-P010}
done

#**********Modulo de geracao de csv*************#
echo ${MSG_POPULADB_AUTOMATICO_INICIO}
${HOME}/src/populaDB-embaralhado.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -b ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES} -c ${HOME_NFS}/${ESTRUTURA_CORRETORES} -a ${HOME_NFS}/${PATH_PROVAS}/ -g ${HOME_NFS}/${ESTRUTURA_GUIAS} -s ${SAIDA_CSV} > ${LOG}/log_populaDB_${DATA}.log
#Correcao de path
sed -i "s#${HOME_NFS}/##g" ${SAIDA_CSV}/*.csv

#Tratamento para disciplinas diferentes no BD, mas como mesma sigla
awk '/STA001/' ${SAIDA_CSV}/folhas.csv > ${SAIDA_CSV}/folhas_disciplina_ambigua.csv
awk '/STA001/' ${SAIDA_CSV}/correcoes.csv > ${SAIDA_CSV}/correcoes_disciplina_ambigua.csv

#*************Modulo de backup ************************#
cp ${SAIDA_CSV}/correcoes.csv ${BACKUP_CSV}/${DATA}-correcoes.csv
cp ${SAIDA_CSV}/folhas.csv ${BACKUP_CSV}/${DATA}-folhas.csv
cp ${SAIDA_CSV}/guias.csv ${BACKUP_CSV}/${DATA}-guias.csv
cp ${SAIDA_CSV}/provas.csv ${BACKUP_CSV}/${DATA}-provas.csv
cp ${SAIDA_CSV}/questoes.csv ${BACKUP_CSV}/${DATA}-questoes.csv
cp ${SAIDA_CSV}/folhas_disciplina_ambigua.csv ${BACKUP_CSV}/${DATA}-folhas_disciplina_ambigua.csv
cp ${SAIDA_CSV}/correcoes_disciplina_ambigua.csv ${BACKUP_CSV}/${DATA}-correcoes_disciplina_ambigua.csv

#Remove duplicados
cat ${SAIDA_CSV}/guias.csv | sort | uniq > ${SAIDA_CSV}/guias_tmp.csv
cat ${SAIDA_CSV}/questoes.csv | sort | uniq > ${SAIDA_CSV}/questoes_tmp.csv

mv ${SAIDA_CSV}/questoes_tmp.csv ${SAIDA_CSV}/questoes.csv
mv ${SAIDA_CSV}/guias_tmp.csv ${SAIDA_CSV}/guias.csv

${HOME}/src/sgaTestesGuias.py -a ${SAIDA_CSV}/guias.csv > ${LOG}/log_sgaTestesGuias_${DATA}.log
${HOME}/src/sgaQuestoes.py -a ${SAIDA_CSV}/questoes.csv > ${LOG}/log_sgaQuestoes_${DATA}.log

#******Modulo de Insercao de Banco de dados*****#
#Incluindo folhas
echo "Iniciando insercao no Banco de Dados"
${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_full-insertion_sgaFolhas_regular_${DATA}.log
${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} > ${LOG}/log_full-insertion_sgaFolhas_DP_${DATA}.log

#Tratamento para o caso de duas disciplinas diferentes que usam a mesma disciplina
${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas_disciplina_ambigua.csv -c ${CALENDARIO} -t ${TIPO_PROVA} -d > ${LOG}/log_full-insertion_sgaFolhas_regular_ambiguo${DATA}.log
${HOME}/src/sgaFolhas.py -a ${SAIDA_CSV}/folhas_disciplina_ambigua.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} -d > ${LOG}/log_full-insertion_sgaFolhas_DP_ambiguo${DATA}.log

echo "Insercao de folhas no Banco de Dados finalizada"
echo ${MSG_POPULADB_AUTOMATICO_FIM}

echo ${MSG_CORRECAO_AUTOMATICO_INICIO}
#Incializa um arquivo de ausentes
> ${SAIDA_CSV}/ausentes.csv
echo "Executando o rodaScannerME, aguarde o processamento..."
${HOME}/src/rodaScannerME.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -p ${HOME_NFS}/${PATH_PROVAS} > ${LOG}/log_rodaScannerME_${DATA}.log
echo "Executando converte, aguarde o processamento..."
${HOME}/src/converte.py -e ${HOME_NFS}/${PATH_PROVAS} -s ${SAIDA_CSV}/ausentes.csv > ${LOG}/log_converte_${DATA}.log
echo "Executando rodaLeitorPresenca, aguarde o processamento..."
${HOME}/src/rodaLeitorPresenca.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -a ${SAIDA_CSV}/ausentes.csv -p ${HOME_NFS}/${PATH_PROVAS} > ${LOG}/log_rodaLeitorPresenca_${DATA}.log
echo "Executando corrigeME, aguarde o processamento..."
${HOME}/src/corrigeME.py -e ${HOME_NFS}/${ESTRUTURA_PROVAS} -g ${HOME_NFS}/${GABARITO_PROVAS} -a ${HOME_NFS}/${PATH_PROVAS} -s ${SAIDA_CSV}/notas.csv > ${LOG}/log_corrigeME_${DATA}.log
echo "Filtrando arquivo de saida de correcao"
#Esse passo é necessário para não sobrescrever correcoes de Notas manuais --segundo awk é um fix para inibir a re-escrita de provas mal escaneadas
awk '!/em branco/' ${SAIDA_CSV}/notas.csv | awk '!/respostas/' > ${SAIDA_CSV}/nota_filtrada.csv

#Tratamento para disciplinas diferentes no BD, mas como mesma sigla
awk '/STA001/' ${SAIDA_CSV}/nota_filtrada.csv > ${SAIDA_CSV}/nota_filtrada_disciplina_ambigua.csv
awk '/STA001/' ${SAIDA_CSV}/ausentes.csv> ${SAIDA_CSV}/ausentes_disciplina_ambigua.csv

#*************Modulo de backup ************************#
cp ${SAIDA_CSV}/nota_filtrada.csv ${BACKUP_CSV}/${DATA}_nota_filtrada.csv
cp ${SAIDA_CSV}/notas.csv ${BACKUP_CSV}/${DATA}_nota_raw.csv
cp ${SAIDA_CSV}/nota_filtrada_disciplina_ambigua.csv ${BACKUP_CSV}/${DATA}_nota_filtrada_disciplina_ambigua.csv

#Concatena o ausentes manual e automatico
cat ${SAIDA_CSV}/ausentes.csv ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual.csv | sort | uniq > ${SAIDA_CSV}/ausentes_tmp.csv

#Retira de ausentes as disciplinas que tiveram reaplicação (resolução de conflito presença de duas provas)
awk '!/STA001/' ${SAIDA_CSV}/ausentes.csv | awk '!/EMA002/' > ${SAIDA_CSV}/ausentes_filtrado.csv
mv ${SAIDA_CSV}/ausentes_filtrado.csv ${SAIDA_CSV}/ausentes.csv

cp ${SAIDA_CSV}/ausentes_tmp.csv ${SAIDA_CSV}/ausentes.csv
cp ${SAIDA_CSV}/ausentes.csv ${BACKUP_CSV}/${DATA}_ausentes.csv

cat ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual.csv | sort | uniq > ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual_tmp.csv
mv ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual_tmp.csv ${HOME_NFS}/${ESTRUTURA_CSV}/ausentes_manual.csv

#******Modulo de Insercao de Banco de dados*****#
#Incluindo notas
echo "Iniciando insercao no Banco de Dados"
${HOME}/src/sgaNotas.py -a ${SAIDA_CSV}/nota_filtrada.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaNotas_regular_${DATA}.log
${HOME}/src/sgaNotas.py -a ${SAIDA_CSV}/nota_filtrada.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} > ${LOG}/log_sgaNotas_DP_${DATA}.log

${HOME}/src/sgaNotas.py -a ${SAIDA_CSV}/nota_filtrada_disciplina_ambigua.csv -c ${CALENDARIO} -t ${TIPO_PROVA} -d > ${LOG}/log_sgaNotas_regular_ambiguo_${DATA}.log
${HOME}/src/sgaNotas.py -a ${SAIDA_CSV}/nota_filtrada_disciplina_ambigua.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} -d > ${LOG}/log_sgaNotas_DP_ambiguo_${DATA}.log

echo "Insercao de Notas no Banco de Dados finalizada"

#Essa rotina é exclusiva do populaDB, nao deve ser usada em fullInsertion
if [ "${BIMESTRE_CONSOLIDADO}" == "sim" ]; then
	cat ${SAIDA_CSV}/correcoes.csv > ${SAIDA_CSV}/lista_referencia_liberacao.csv
	sed -i -e 's/^/X,X,/' ${SAIDA_CSV}/lista_referencia_liberacao.csv
	${HOME}/src/sgaPresentes.py -a ${SAIDA_CSV}/lista_referencia_liberacao.csv -c ${CALENDARIO} -t ${TIPO_PROVA} -oe > ${LOG}/log_sgaPresentes_liberados_regular_${DATA}.log
	${HOME}/src/sgaPresentes.py -a ${SAIDA_CSV}/lista_referencia_liberacao.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} -oe > ${LOG}/log_sgaPresentes_liberados_DP_${DATA}.log
	
	#Tratamento para disciplinas diferentes no BD, mas como mesma sigla
	awk '/STA001/' ${SAIDA_CSV}/lista_referencia_liberacao.csv > ${SAIDA_CSV}/disciplina_ambigua_lista_referencia_liberacao.csv
	${HOME}/src/sgaPresentes.py -a ${SAIDA_CSV}/disciplina_ambigua_lista_referencia_liberacao.csv -c ${CALENDARIO} -t ${TIPO_PROVA} -oe -d > ${LOG}/log_sgaPresentes_liberados_regular_ambiguo${DATA}.log
	${HOME}/src/sgaPresentes.py -a ${SAIDA_CSV}/disciplina_ambigua_lista_referencia_liberacao.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} -oe -d > ${LOG}/log_sgaPresentes_liberados_DP_ambiguo${DATA}.log
	#rm ${SAIDA_CSV}/lista_referencia_liberacao.csv
fi

#Inclui ausentes
${HOME}/src/sgaAusentes.py -a ${SAIDA_CSV}/ausentes.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaAusentes_regular_${DATA}.log
${HOME}/src/sgaAusentes.py -a ${SAIDA_CSV}/ausentes.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} > ${LOG}/log_sgaAusentes_DP_${DATA}.log

#Tratamento para disciplinas diferentes no BD, mas como mesma sigla
#Inclui ausentes
${HOME}/src/sgaAusentes.py -a ${SAIDA_CSV}/ausentes_disciplina_ambigua.csv -c ${CALENDARIO} -t ${TIPO_PROVA} -d > ${LOG}/log_sgaAusentes_regular_${DATA}.log
${HOME}/src/sgaAusentes.py -a ${SAIDA_CSV}/ausentes_disciplina_ambigua.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} -d > ${LOG}/log_sgaAusentes_DP_${DATA}.log

echo "Insercao de ausentes no Banco de Dados finalizada"

#Rotina de atualizacao Ausentes
mv ${SAIDA_CSV}/ausentes_tmp.csv ${HOME_NFS}/${ESTRUTURA_AUSENTES}

echo "Provas Corrigidas"

#Inclui corretores
${HOME}/src/sgaCorretores.py -a ${SAIDA_CSV}/correcoes.csv -c ${CALENDARIO} -t ${TIPO_PROVA} > ${LOG}/log_sgaCorretores_regular_${DATA}.log
${HOME}/src/sgaCorretores.py -a ${SAIDA_CSV}/correcoes.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} > ${LOG}/log_sgaCorretores_DP_${DATA}.log
#Tratamento para disciplinas diferentes no BD, mas como mesma sigla
#Inclui corretores
${HOME}/src/sgaCorretores.py -a ${SAIDA_CSV}/correcoes_disciplina_ambigua.csv -c ${CALENDARIO} -t ${TIPO_PROVA} -d > ${LOG}/log_sgaCorretores_regular_${DATA}.log
${HOME}/src/sgaCorretores.py -a ${SAIDA_CSV}/correcoes_disciplina_ambigua.csv -c ${CALENDARIO_DP} -t ${TIPO_PROVA_DP} -d > ${LOG}/log_sgaCorretores_DP_${DATA}.log

echo "Insercao de corretores no Banco de Dados finalizada"

#Rotina de atualizacao BaseCorrecoes
cat ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES} ${SAIDA_CSV}/correcoes.csv > ${SAIDA_CSV}/correcoes_tmp.csv
mv ${SAIDA_CSV}/correcoes_tmp.csv ${HOME_NFS}/${ESTRUTURA_BASE_CORRECOES}

echo ${MSG_CORRECAO_AUTOMATICO_FIM}