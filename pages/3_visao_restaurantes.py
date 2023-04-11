#biblioteca
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from haversine import haversine
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import numpy as np

st.set_page_config(page_title='Visão Restaurantes', page_icon='🍽️', layout='wide' )


#===============================================
#------------------Funções---------------------
#===============================================

def clean_code ( df ):
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

def distance(df, fig):
    if fig == False:
        df['distance']=df.loc[:,['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
        avg_distance = np.round(df['distance'].mean(), 2)
        return avg_distance
    else:
        df['distance']=df.loc[:,['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']].apply(lambda x: haversine((x['Restaurant_latitude'],x['Restaurant_longitude']), (x['Delivery_location_latitude'],x['Delivery_location_longitude']) ), axis=1)
        avg_distance = df.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data = [go.Pie ( labels = avg_distance['City'], values = avg_distance['distance'], pull = [0, 0.01, 0])])
        return fig
                
def avg_std_time(df, avg_std, festival):
    df_aux = (df.loc[:,['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival,avg_std],2)
    return df_aux

def avg_std_graph(df):
    df_aux = (df.loc[:,['Time_taken(min)', 'City']]
                    .groupby('City')
                    .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name = "Control",
                            x = df_aux['City'],
                            y = df_aux['avg_time'],
                            error_y = dict(type='data', array = df_aux['std_time'] )))
    fig.update_layout(barmode='group')
    return fig

def table(df):
    df_aux = (df.loc[:,['Time_taken(min)', 'City', 'Type_of_order']]
                    .groupby(['City','Type_of_order'])
                    .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    return df_aux
def avg_std_time_traffic(df):
    df_aux = (df.loc[:,['Time_taken(min)', 'City', 'Road_traffic_density']]
                .groupby(['City','Road_traffic_density'])
                .agg({'Time_taken(min)':['mean','std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

#importação dataset
df_raw = pd.read_csv('../dataset/dataframe/train.csv')

#limpeza dataset
df = clean_code(df_raw)

# ======================================================================================
#  Barra Lateral  - kernel -  & c:/Users/User/Desktop/ftc/repos/dataset/venv/Scripts/Activate.ps1
# ======================================================================================
st.header('Marketplace - Restaurantes')
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
            st.markdown('''___''')
            st.header('Overall Metrics')
            
            col1, col2, col3, col4, col5, col6, = st.columns(6)
            with col1:
                entregadores_unicos = len(df['Delivery_person_ID'].unique())
                col1.metric('Entregadores',entregadores_unicos )
                
            with col2:
                avg_distance = distance(df, fig=False)
                col2.metric('Distancia Média', avg_distance)
                
            with col3:
                df_aux = avg_std_time(df, avg_std='avg_time', festival='Yes')
                col3.metric('Tempo Médio de Entrega', df_aux)
                
            with col4:
                df_aux = avg_std_time(df, avg_std='std_time', festival='Yes')
                col4.metric('Desvio Padrão de Entrega c/ Festival', df_aux)
                
            with col5:
                df_aux = avg_std_time(df,'avg_time','No') #Forma *2* de como atribuir os valores na função
                col5.metric('Tempo Médio', df_aux)
                
            with col6:
                df_aux = avg_std_time(df, avg_std='std_time', festival='No')
                col6.metric('STD Entrega', df_aux)
        
        with st.container():
            st.markdown('## Média e Desvio Padrão')
                
            col1, col2 = st.columns(2, gap='medium')
            with col1:
                fig = avg_std_graph(df)
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                df_aux = table(df)
                st.dataframe(df_aux, use_container_width=True)
            st.markdown('''___''')
        
        
        with st.container():
            st.header('Distribuição do tempo')
            
            col1, col2 = st.columns(2)
            with col1:
                fig = distance(df, fig=True)
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                fig = avg_std_time_traffic(df)
                st.plotly_chart(fig, use_container_width=True)    
        st.markdown('''___''')
        
           