#!/bin/bash

for a in `seq -f "%04.0f" 0 336`
do 
  mkdir -p $a
done
