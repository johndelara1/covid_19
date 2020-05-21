import streamlit as st
import pandas as pd
import base64
import random
import datetime
import plotly.express as px
import plotly.graph_objects as go
import base64
from PIL import Image
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima_model import ARIMA
import glob

try:
    xlsx = glob.glob("/home/vinho/Downloads/*.xlsx")[0]
except NameError:
    from raspagem_covid import Raspagem
    xlsx = glob.glob("/home/vinho/Downloads/*.xlsx")[0]
except:
    xlsx = 'null'
if xlsx != 'null':
    from transform_df import Transform

def is_authenticated(password):
    return password == "admin"


def generate_login_block():
    block1 = st.empty()
    block2 = st.empty()

    return block1, block2


def clean_blocks(blocks):
    for block in blocks:
        block.empty()


def login(blocks):
    blocks[0].markdown("""
            <style>
                input {
                    -webkit-text-security: disc;
                }
            </style>
        """, unsafe_allow_html=True)

    return blocks[1].text_input('Password')


#login_blocks = generate_login_block()
#password = login(login_blocks)

def sortear_cor():
    color_list=['#4682B4','#90EE90','#BC8F8F','#DDA0DD','#FFB6C1','#FF6347','#F0E68C','#FF6347','#483D8B']
    color_select =random.choice(color_list) 
    return color_select

def plot_bar(df, list_var):
    df=df
    x_values = df['estado']
    data_bar = []

    for i in list_var:
             cor_bar = sortear_cor()
             data_bar.append(go.Bar(name=i, x=x_values, y=df[i],orientation='v',
             text = df[i],
              textposition='outside'
             ))

    fig = go.Figure(data=data_bar
                )

    fig.update_layout(barmode='group',
                      title_text = ('Valores '+' por'+' Estado'),
                      showlegend = True,
                       plot_bgcolor='AliceBlue',
                       autosize=True,
                       margin=dict(
                       autoexpand=True,
                       l=100,
                       r=20,
                       t=110))
    return fig

def plot_scatter(df, list_var,list_estado,x):
    df=df[df[list_var[0]]>0]
    df.sort_values(x, inplace= True)
    
    data_scatter = []

    for j in list_estado:
        df_scatter= df[df['estado']==j]
        x_values = df_scatter[x]
        for i in list_var:
                cor_bar = sortear_cor()
                data_scatter.append(go.Scatter(name=(j+' - '+i), x=x_values, y=df_scatter[i]))
    
    fig = go.Figure(data_scatter)
    fig.update_layout(
         title_text = ('Valores por Data'),
        xaxis=dict(
        showline=True,
        showgrid=True,
        gridcolor = 'lightgray',
        showticklabels=True,
        linecolor='rgb(204, 204, 204)',
        linewidth=2,
        ticks='outside',
        tickfont=dict(
            family='Arial',
            size=12,
            color='rgb(82, 82, 82)',
        ),
        ),
        yaxis=dict(
        showgrid=True,
        gridcolor = 'lightgray',
        zeroline=True,
        showline=False,
        showticklabels=True,
        ),
        autosize=True,
        margin=dict(
        autoexpand=True,
        l=100,
        r=20,
        t=110,
        ),
        showlegend=True,
        legend_title_text='Legenda',
        plot_bgcolor='AliceBlue'
        )   

    return fig

def tratar_df(df):
        df.query('regiao in ["Norte","Nordeste","Sudeste","Sul","Centro-Oeste"]', inplace = True)
        while True:
            try:
                df['data']= pd.to_datetime(df['data'], format='%d/%m/%Y')
                break
            except ValueError:
                df['data']= pd.to_datetime(df['data'], format='%Y-%m-%d')
        df['casosNovos']= df['casosNovos'].astype(float)
        df['casosAcumulados']= df['casosAcumulados'].astype(float)
        df['obitosNovos']= df['obitosNovos'].astype(float)
        df['obitosAcumulados']= df['obitosAcumulados'].astype(float)
        df['letalidade'] = (df['obitosAcumulados']/df['casosAcumulados']).astype(float)
        df.sort_values(by = ['estado'], inplace = True)
        
def var_MilhaoPop(df):
        df['obitoMilhaoPop'] = (df['obitosAcumulados']/(df['PopCenso2012']/1000000)).astype(float)
        df['casosMilhaoPop'] = (df['casosAcumulados']/(df['PopCenso2012']/1000000)).astype(float)
        df['duration'] = (pd.to_datetime(df['data']) - pd.to_datetime(df['data_100'])).dt.days.astype(float)

def arima(data, texto, time_prediction):
    data = data[f'{texto}'].reset_index(drop=True)
    # fit model
    model = ARIMA(data, order=(1, 1, 1))
    model_fit = model.fit(disp=False)
    # make prediction
    yhat = model_fit.predict(len(data), len(data) + time_prediction-1, typ='levels')
    return yhat

def tabela_previsao (df, max_date):
    from datetime import timedelta, date
    # Previsão dos próximos 7 dias
    dias_de_previsao = 7
    predict_df = df.groupby([df.data.dt.year, df.data.dt.month, df.data.dt.day]).sum()
    predict_casosNovos = pd.DataFrame(arima(predict_df,
                                            'casosNovos',
                                            dias_de_previsao))
    predict_obitosNovos = arima(predict_df,
                                'obitosNovos',
                                dias_de_previsao)

    st.subheader(
        ('Previsão até o dia - ' + format(format(max_date + timedelta(days=dias_de_previsao), '%d/%m/%Y'))))

    df_teste = predict_df.sort_index(ascending=False).head(dias_de_previsao).filter(items=['casosNovos', 'obitosNovos'])

    datelist = pd.date_range(max_date + timedelta(days=1), periods=dias_de_previsao)
    df_teste.index = datelist
    df_teste['casosNovos'] = list(predict_casosNovos[0])
    df_teste['casosNovos'] = df_teste['casosNovos'].astype(int)
    df_teste['obitosNovos'] = list(predict_obitosNovos)
    df_teste['obitosNovos'] = df_teste['obitosNovos'].astype(int)
    df_teste = df_teste.reset_index()

    df_teste.columns = ["data", "casosNovos", "obitosNovos"]
    df_anterior = df.filter(items=['data', 'casosNovos', 'obitosNovos'])
    df_anterior = df_anterior.groupby([df_anterior.data]).sum()
    df_anterior = df_anterior.sort_values(by=['data'], ascending=False)

    juncaoDeDados = pd.concat([df_anterior, df_teste]).reset_index(drop=True)
    final = juncaoDeDados.sort_values(by=['data'], ascending=False)
    final = final.filter(items=['data', 'casosNovos', 'obitosNovos'])
    st.dataframe(final)

def main ():
    st.sidebar.image(Image.open('JOHN.jpg'), use_column_width=True, width=350, clamp=True)
    st.sidebar.markdown('**E-Mail**: johndelara1@gmail.com \n'
                        '- [Linkedin](https://www.linkedin.com/in/johndelara1/) '
                        '- [Medium](https://medium.com/@johndelara1) '
                        '- [Portfólio](https://johndelara1.github.io/portfolioweb/) '
                        '- [GitHub](https://github.com/johndelara1)')

    st.sidebar.markdown('Opção Desejada')
    selecao_secao = st.sidebar.selectbox('Seleciona a seção desejada', ('Gráficos', 'Resumo','Visualizar Base'))

    #Importandado dados Default
    df = pd.read_csv('arquivo_geral.csv',sep = ';', encoding = 'latin')
    pop = pd.read_csv('popCenso2012.csv',sep = ';',encoding = 'latin')


    #Definindo Layout topo
    st.image("https://covid.saude.gov.br/assets/imgs/logo-app.png",  width= 500)

    #Seleção da seção

    #Sessão para import de dados
    st.write('Para atualizar os dados acesse a página https://covid.saude.gov.br/ ,faça o download do "Arquivo.Csv" e faça o Upload na sessão abaixo.')
    file = st.file_uploader('Faça o upload do arquivo csv', type = 'csv', encoding = 'latin')
    if file is not None:
        df=pd.read_csv(file, sep = ';')

    #tratando dataset
    tratar_df(df) #função para tratar variaveis
    df_caso_100 = df[['estado','casosAcumulados','data']][df['casosAcumulados']>=100]
    df_caso_100 =df_caso_100.groupby(['estado']).agg({'data':'min'})
    df_caso_100.columns = ['data_100']
    df_caso_100.head(30)
    df = df.merge(df_caso_100, left_on = 'estado', right_on = 'estado', how ='left')
    df = df.merge(pop,left_on = 'estado', right_on = 'UF', how = 'left') #Join com base de Censo
    df.update(df['data_100'].fillna(datetime.date.today()))
    var_MilhaoPop(df) #Criar variaiveis de população
    max_data_import = max(df['data'])


    #Seletor de Data de Última Data
    st.sidebar.markdown('Filtros para Gráficos')
    filter_date = st.sidebar.date_input('Selecione data fim da visualização', max(df['data']))
    max_date = max(df['data'])
    if filter_date <= max_date:
        max_date = filter_date
    else:
        st.sidebar.error('Data selecionada é maior do que a última disponível.')

    df = df[df['data']<= str(max_date)]
    st.sidebar.markdown('Dados atualizados até: {}'.format(format(max_data_import,'%d/%m/%Y')))

    #Seletor de Estado
    filter_estado = st.sidebar.multiselect('Selecione os Estados',  df['Unidade da Federação'].unique())
    if filter_estado == []:
        pass
    else:
        df = df[df['Unidade da Federação'].isin(filter_estado)]

    #Seletor de Variaveis
    aux = pd.DataFrame({'colunas' : df.columns, 'tipos' : df.dtypes})
    lista = list(aux['colunas'].loc[(aux['tipos'] == 'float')])
    df[lista]=df[lista].apply(lambda x:round(x,2))

    #filter bar
    filter_var = st.sidebar.multiselect('Selecione a Variavel Gráfico de Barras', lista)
    if filter_var == []:
        filter_var = lista
    else:
       pass

    #filter scattter
    filter_var_sc = st.sidebar.multiselect('Selecione a Variavel Gráfico de Linhas', lista)
    if filter_var_sc == []:
        filter_var_sc = lista
    else:
       pass

       #Criando data set 'hoje'
    df_hoje = df[df['data']==max(df['data'])]

    if selecao_secao == 'Gráficos':

        #Grafico de barras
        st.title('Gráficos')
        st.subheader(('Gráfico - Resumo de Dados -'+format(format(max_date,'%d/%m/%Y'))))
        st.plotly_chart(plot_bar(df_hoje, filter_var)) #Chamando função para plotar gráfico plot_bar
        st.subheader(('Gráfico - Evolução na Linha do Tempo'))
        st.plotly_chart(plot_scatter(df, filter_var_sc, df['estado'].unique(), 'data')) #Chamando função para plotar gráfico plot_bar
        df = df[df['duration']>=0]
        st.subheader(('Gráfico - Evolução à partir do Caso 100'))
        st.plotly_chart(plot_scatter(df, filter_var_sc, df['estado'].unique(), 'duration'))

    if selecao_secao == 'Resumo':
        st.title('Resumo')
        st.subheader('Descrição da ferramenta:')
        st.write(
            'A ferramenta auxilia na visualização de dados do COVID-19 no Brasil, ela foi desenvolvida para interagir com os dados disponibilizados pelo Ministério da Saúde.')
        st.write(
            'A ferramenta é totalmente interativa, portanto para gerar os dados você deve interagir com os filtros da barra lateral esquerda.')
        st.write(
            'Para atualizar os dados acesse a página https://covid.saude.gov.br/ ,faça o download do "Arquivo.Csv" e faça o Upload no ínicio da página.')
        st.subheader('Descrição dos dados:')
        st.markdown(
            '<b>data:</b> Data do reporte, não significa que a morte ou o caso aconteceu neste dia, mas sim a data que o estado reportou ao ministério.',
            unsafe_allow_html=True)
        st.markdown('<b>casosNovos: </b> Casos reportados na data.', unsafe_allow_html=True)
        st.markdown('<b>casosAcumulados: </b> Casos somados até a data.', unsafe_allow_html=True)
        st.markdown('<b>obitosNovos: </b> Óbitos reportados na data.', unsafe_allow_html=True)
        st.markdown('<b>obitosAcumulados: </b> Óbitos somados até a data.', unsafe_allow_html=True)
        st.markdown('<b>letalidade: </b> Letalidade é a relação entre óbitos e casos acumulados (óbitos/casos).',
                    unsafe_allow_html=True)
        st.markdown('<b>PopCenso2012: </b> População do estado segundo censo realizado em 2012.',
                    unsafe_allow_html=True)
        st.markdown(
            '<b>obitoMilhaoPop: </b> Óbitos por milhão de habitantes, esse indicador é importante pois dá dimensão da proporção da doença em cada região.',
            unsafe_allow_html=True)
        st.markdown('<b>casosMilhaoPop: </b> Casos por milhão de habitantes.', unsafe_allow_html=True)
        st.markdown(
            '<b>data_100: </b> Este parametro, traz o dia que a doença está, a partir do reporte do caso 100, como a pândemia está em tempos diferentes para cada região, esta variável põe as regiões na mesma linha do tempo.',
            unsafe_allow_html=True)

    if selecao_secao == 'Visualizar Base':
        tabela_previsao(df, max_date)13
        # Mostrando Data Set
        st.subheader('Dados completos')
        st.dataframe(df)
        st.subheader('Dados do dia')
        st.dataframe(df_hoje)

#if is_authenticated(password):
#    #st.success('Parabéns, você logou!')
#    clean_blocks(login_blocks)
#    if __name__ == '__main__':
#        main()

#elif password:
#    st.error("Por favor verifique sua senha")

if __name__ == '__main__':
    main()
