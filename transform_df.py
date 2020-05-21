#!/usr/bin/env python
# coding: utf-8

# ### região | estado | data | casosNovos | casosAcumulados | obitosNovos | obitosAcumulados
import pandas as pd
from IPython.display import display
import warnings
import os
import glob

class Transform:
    arquivo_xlsx = glob.glob("/home/vinho/Downloads/*.xlsx")[0]
    df = pd.read_excel(arquivo_xlsx)
    df = df[["regiao", "estado", "data", "casosAcumulado", "obitosAcumulado"]]
    df1 = df[df.regiao.eq('Brasil')]
    df1['casosNovos'] = df1['casosAcumulado'].diff().abs()
    df1['obitosNovos'] = df1['obitosAcumulado'].diff().abs()
    df1['casosNovos'][0] = df1.iloc[0].casosAcumulado
    df1['obitosNovos'][0] = df1.iloc[0].obitosAcumulado
    with pd.option_context('display.max_rows', 1000, 'display.max_columns', 10):
        display(df1.head(1000))
    df = df[df.regiao != 'Brasil']
    estados = df.estado.unique()
    for i in estados:
        df2 = df[df.estado.eq(i)]
        df2 = df2.sort_values(by='data', ascending=False)
        df2 = df2.groupby(["regiao", "estado", "data"])['casosAcumulado', 'obitosAcumulado'].sum()
        df2['casosNovos'] = df2['casosAcumulado'].diff().abs()
        df2['obitosNovos'] = df2['obitosAcumulado'].diff().abs()
        df2.reset_index(inplace=True)
        df2.loc[:0].casosAcumulado[0]
        df2['casosNovos'][0] = df2.iloc[0].casosAcumulado
        df2['obitosNovos'][0] = df2.iloc[0].obitosAcumulado
        df1 = pd.concat([df1, df2])
    df = df1[df1.regiao != 'Brasil']
    df = df[['regiao', 'estado', 'data', 'casosNovos', 'casosAcumulado', 'obitosNovos', 'obitosAcumulado']]
    df.columns = "regiao", "estado", "data", "casosNovos", "casosAcumulados", "obitosNovos", "obitosAcumulados"
    df.to_csv(r'arquivo_geral.csv', index = False, sep=';')
    os.remove(arquivo_xlsx)
