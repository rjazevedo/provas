#!/bin/bash

cd ~/src/scripts-auxiliares
#./3Bfipa.sh config/2019b3-conf.sh -- Desnecessário, pois populaDB emabaralhado não libera folhas parciais diferente da versão regular
./3Bpcbpa.sh config/2019b3-conf.sh
./3Bpa.sh config/2019b3-conf.sh
