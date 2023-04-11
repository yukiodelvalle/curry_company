#biblioteca
import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão entregadores', page_icon='🛵', layout='wide' )


#===============================================
#------------------Funções---------------------
#===============================================

def clean_code ( df ):
    ''' Função para limpeza de dados '''
#remover espaços das strings
    df.iloc[:,12] = df.iloc[:,12].str.strip()
    df.iloc[:,14] = df.iloc[:,14].str.strip()
    df.iloc[:,15] = df.iloc[:,15].str.strip()
    df.iloc[:,17] = df.iloc[:,17].str.strip()
    df.iloc[:,18] = df.iloc[:,18].str.strip()

    # ( Conceitos de seleção condicional )
    df = df.loc[df['Delivery_person_Age']!='NaN',:]

    # Remove as linhas da culuna multiple_deliveries que tenham o conteudo igual a 'NaN '
    df = df.loc[df['multiple_deliveries']!="NaN",:]

    # Excluir as linhas com a idade dos entregadores vazia
    df = df.loc[df['Delivery_person_Age']!= 'NaN',:]

    # Excluir as linhas com a tipos de densidade vazia
    df = df.loc[df['Road_traffic_density']!='NaN',:]

    # Excluir as linhas com a tipos de densidade vazia
    df = df.loc[df['City']!='NaN',:]

    df = df.loc[df['Delivery_person_Ratings']!='NaN ',:]

    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( "int64" )

    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )

    # # Comando para remover o texto de números
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1])

    df['Time_taken(min)'] = df['Time_taken(min)'].astype( 'int64')
    
    return df

def top_delivers(df, top_asc):
    df2 = (df.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
            .groupby(['City','Delivery_person_ID'])
            .mean()
            .sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
            .reset_index() )
    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([df_aux1, df_aux2,df_aux3]).reset_index(drop=True)
    return df3



#import Dataset
df_raw = pd.read_csv('../dataset/dataframe/train.csv')

#cópia dos dados
df = clean_code(df_raw)

#
# ======================================================================================
#  Barra Lateral  - kernel -  & c:/Users/User/Desktop/ftc/repos/dataset/venv/Scripts/Activate.ps1
# ======================================================================================
st.header('Marketplace - Entregadores')
# image_path = 'C:/Users/User/Desktop/ftc/repos/dataset/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=100)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''___''')
st.sidebar.markdown('##Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual data?',
    value=pd.datetime(2023, 3, 24),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)
st.sidebar.markdown('''___''') 

traffic_options = st.sidebar.multiselect(
    'Quais as condições do transito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = 'Low'
)

weather_options = st.sidebar.multiselect(
    'Tipos de climas',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms','conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default = 'conditions Sunny'
)
st.sidebar.markdown('''___''')
st.sidebar.markdown('### Powered by *Comunidade DS*')

#filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider 
df = df.loc[linhas_selecionadas,:]

#filtro de trafego
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas,:]

#filtro de clima
linhas_selecionadas = df['Weatherconditions'].isin(weather_options)
df = df.loc[linhas_selecionadas,:]

# =================================================================================================
# LAYOUT STREAMLIT  - kernel -  & c:/Users/User/Desktop/ftc/repos/dataset/venv/Scripts/Activate.ps1
# ==================================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])
with tab1:
        with st.container():
            st.title('Overall Metrics')
            
            col1, col2, col3, col4 = st.columns(4, gap='large')
            with col1:
                #Entregador com maior idade
                maior_idade = df.loc[:,'Delivery_person_Age'].max()
                col1.metric('Maior idade', maior_idade)
                
            with col2:
                #Entregador com menor idade
                menor_idade = df.loc[:,'Delivery_person_Age'].min()
                col2.metric('Menor Idade', menor_idade)
                
            with col3:
                #Melhor condição de veiculo
                melhor_condicao = df.loc[:,'Vehicle_condition'].max()
                col3.metric('Melhor Condição', melhor_condicao)

            with col4:
                #Pior condição de veiculo
                pior_condicao = df.loc[:,'Vehicle_condition'].min()
                col4.metric('Pior Condição', pior_condicao)
                
        with st.container():
            st.markdown('''___''')
            st.title('Avaliações')
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('##### Avaliações Medias por Entregador')
                avg_entrega = (df.loc[:,['Delivery_person_Ratings', 'Delivery_person_ID']]
                                .groupby('Delivery_person_ID')
                                .mean()
                                .reset_index() )
                st.dataframe(avg_entrega)
                
            with col2:
                st.markdown('##### Avaliação media por transito')
                avg_traffic = (df.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                 .groupby('Road_traffic_density')
                                 .agg({'Delivery_person_Ratings':['mean','std']}) )
                #mudanca nome das colunas
                avg_traffic.columns = ['delivery_mean', 'delivery_std']
                st.dataframe(avg_traffic)
                st.markdown('##### Avaliação media por Clima')
                avg_weather = (df.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                 .groupby('Weatherconditions')
                                 .agg({'Delivery_person_Ratings':['mean','std']}) )
                #mudanca nome das colunas
                avg_weather .columns = ['Weather_mean', 'Weather_std']
                st.dataframe(avg_weather)                
        with st.container():
            st.markdown('''___''')
            st.title('Velocidade de Entrega')    
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('##### Top Entregadores mais rápidos')
                df3 = top_delivers(df, top_asc=True)
                st.dataframe(df3)
                
            with col2:
                st.markdown('##### Top Entregadores mais lentos')
                df3 = top_delivers(df, top_asc=False)
                st.dataframe(df3)
                
                
                