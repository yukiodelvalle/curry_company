#biblioteca
import pandas as pd
import plotly.express as px
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide' )

#import Dataset
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

def order_metric(df):
    df1 = df.loc[:,['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    fig = px.bar(df1, x='Order_Date', y='ID')
    return fig

def traffic_order_share(df):
    df1 = df.loc[:,['Road_traffic_density','ID']].groupby('Road_traffic_density').count().reset_index()
    df1['percent'] = df1['ID'] / df1['ID'].sum()
    fig = px.pie(df1, values='ID', names='Road_traffic_density')
    return fig

def traffic_order_city(df):
    df1 = df.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    fig = px.scatter(df1, x = 'City', y='Road_traffic_density',color='City',size='ID')
    return fig

def order_week(df):
    df['week'] = df['Order_Date'].dt.strftime('%U')
    df1 = df.loc[:,['ID','week']].groupby('week').count().reset_index()
    fig = px.line(df1, x = 'week', y='ID')
    return fig

def order_deliver ( df ):
    df1 = df.loc[:,['ID', 'week']].groupby('week').count().reset_index()
    df2 = df.loc[:,['Delivery_person_ID','week']].groupby('week').nunique().reset_index()
    df_aux = pd.merge(df1, df2, how='inner', on='week')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week', y='order_by_deliver')
    return fig

def country_maps(df):
    #5. A localização central de cada cidade por tipo de tráfego.
    data_plot = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby( ['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map(zoom_start=11)
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'], location_info['Delivery_location_longitude']], popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    
    folium_static(map, width=1024, height=600)
#==========================================================================#
#_________________________Inicio Estrutura de Código_______________________#
#==========================================================================#
#impor Dataframe
df_raw = pd.read_csv('../dataset/dataframe/train.csv')

#limpeza de dados
df = clean_code(df_raw)

# ======================================================================================
#  Barra Lateral  - kernel -  & c:/Users/User/Desktop/ftc/repos/dataset/venv/Scripts/Activate.ps1
# ======================================================================================
st.header('Marketplace - Empresa')
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
    'Tipos de clima',
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
df = df.loc[linhas_selecionadas, :]

# =================================================================================================
# LAYOUT STREAMLIT  - kernel -  & c:/Users/User/Desktop/ftc/repos/dataset/venv/Scripts/Activate.ps1
# ==================================================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #grafico de barra - vendas diarias
        fig = order_metric(df)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)        
        
    with st.container():
    
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.header('Traffic Order City')
            fig = traffic_order_city(df)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig = order_week(df)
        st.plotly_chart(fig, use_container_width=True)

        
    with st.container():
        st.markdown('# Order by deliver')
        fig = order_deliver(df)
        st.plotly_chart(fig, user_container_width=True)

with tab3:
    st.markdown('# Country Map')
    country_maps(df)
    