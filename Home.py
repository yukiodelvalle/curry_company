import streamlit as st
from PIL import Image
st.set_page_config(
    page_title = 'Home',
    page_icon = '🌍',
    layout = 'wide'
)
# ======================================================================================
#  Barra Lateral  - kernel -  & c:/Users/User/Desktop/ftc/repos/dataset/venv/Scripts/Activate.ps1
# ======================================================================================

# image_path = 'C:/Users/User/Desktop/ftc/repos/dataset/'
image = Image.open('logo.png')
st.sidebar.image(image, width=100)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown('''___''')

st.write('# Curry Company Growth Dashboard')

st.markdown(
    '''
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão Restaurantes:
        - Indicadores Semanais de crescimento dos restarantes
        ### Ask for help
        - Time de Data Science no Discord
            - @Rogerdelvalle#8549
    ''' )