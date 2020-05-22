#!/bin/bash
eval "$(conda shell.bash hook)"
cd ~/git/covid_19/
conda deactivate
conda activate covid
python raspagem_covid.py
python transform_df.py
git add . && git commit -m "adicionada função que transforma xlsx" && git push origin master
