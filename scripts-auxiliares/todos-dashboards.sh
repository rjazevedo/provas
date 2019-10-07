#!/bin/bash
#Descricao: Gera todos os dashboards de uma única vez

cd ~/src/scripts-auxiliares

for conf in config/*-conf.sh
do
    ./dashboard.sh $conf
done
