#!/bin/bash
eval "$(conda shell.bash hook)"
cd ~/git/covid_19/
conda deactivate
conda activate covid
mkdir john
python raspagem_covid.py

#git add . && git commit -m "adicionada função que transforma xlsx" && git push origin master
