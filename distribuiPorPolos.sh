#!/bin/bash
date
for a in `seq -f "%04.0f" 0 336`
do 
  #echo $a
  mv *-$a-* $a 2> /dev/null
done
