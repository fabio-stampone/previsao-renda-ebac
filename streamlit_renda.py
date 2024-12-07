import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import plotly.figure_factory as ff
import time

# Função para filtrar o DataFrame
@st.cache_data
def filter(df):
    ''' Função para filtrar as informações do DataFrame '''
    df = df.drop(['Unnamed: 0', 'id_cliente'], axis=1)
    df['data_ref'] = pd.to_datetime(df['data_ref'])
    df_new = df.dropna().reset_index(drop=True)
    return df_new

# Função para gerar todos os pointplots de estabilidade
@st.cache_data
def point(_df):
    ''' Gera todos os pointplots da renda média em função do tempo para variáveis qualitativas '''
    var_qualitativo = _df.select_dtypes(exclude=['int64', 'float64', 'datetime']).columns   
    for var in var_qualitativo:
        st.markdown(f'#### Estabilidade da variável explicativa {var} ao longo do tempo:')
        fig, ax = plt.subplots(figsize=(20, 5))
        sns.pointplot(data=_df, x='data_ref', y='renda', hue=var, dodge=True, errorbar=('ci', 95), ax=ax)
        
        tick_data = _df['data_ref'].map(lambda data: data.strftime('%m/%Y')).unique()
        ax.set_xticks(range(len(tick_data)))
        ax.set_xticklabels(tick_data, rotation=45)
        
        plt.xlabel('Tempo')
        plt.ylabel('Média Renda ($)')
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0, title=var.capitalize())
        st.pyplot(fig)

# Função para gerar um pointplot de uma única variável
def point_unico(_var: str):
    ''' Gera um pointplot da renda média em função do tempo para uma variável específica '''
    st.markdown(f'#### Estabilidade da variável explicativa {_var} ao longo do tempo:')
    
    fig, ax = plt.subplots(figsize=(20, 5))
    sns.pointplot(data=previsao_renda_filter, x='data_ref', y='renda', hue=_var, dodge=True, errorbar=('ci', 95), ax=ax)
    
    tick_data = previsao_renda_filter['data_ref'].map(lambda data: data.strftime('%m/%Y')).unique()
    ax.set_xticks(range(len(tick_data)))
    ax.set_xticklabels(tick_data, rotation=45)
    
    plt.xlabel('Tempo')
    plt.ylabel('Média Renda ($)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0, title=_var.capitalize())
    st.pyplot(fig)

# Função para gerar o histograma de uma variável
def hist(_var: str):
    ''' Gera o histograma da variável quantitativa '''
    st.markdown(f'##### Distribuição da variável quantitativa {_var}:')
    fig, ax = plt.subplots(figsize=(20, 5))
    sns.histplot(previsao_renda_filter, x=_var, kde=True)
    plt.ylabel('Contagem')
    st.pyplot(fig)

# Função para gerar histogramas de todas as variáveis quantitativas
@st.cache_data  
def hist_todos(_df: pd.DataFrame):
    var_quantitativo = _df.select_dtypes(exclude=['bool', 'object', 'datetime']).columns
    for var in var_quantitativo:
        st.markdown(f'##### Distribuição da variável quantitativa {var}:')
        fig, ax = plt.subplots(figsize=(20, 5))
        sns.histplot(_df, x=var, kde=True)
        plt.ylabel('Contagem')
        st.pyplot(fig)

# Configuração da página
st.set_page_config(page_title='Análise Exploratória', page_icon='https://cdn-icons-png.freepik.com/512/8649/8649621.png', layout='wide')

# Leitura e filtragem do DataFrame
previsao_renda = pd.read_csv(r'C:\Users\fabio\Documents\EBAC\Projeto2\input\previsao_de_renda.csv')
previsao_renda_filter = filter(previsao_renda)

# Exibição de metadados
metadados = pd.DataFrame({'dtypes': previsao_renda_filter.dtypes})
metadados['missing'] = previsao_renda_filter.isna().sum()
metadados['perc_missing'] = round((metadados['missing'] / previsao_renda_filter.shape[0]) * 100)
metadados['valores_unicos'] = previsao_renda_filter.nunique()

# Título da página
st.title('Análise Exploratória para a Previsão de Renda:')
st.markdown('----')

left_column, right_column = st.columns(2)
with left_column:
    st.markdown('#### Dataframe utilizado:')
    st.markdown('Dataframe interativo completo.')
    if st.checkbox('Exibir o DataFrame', key='exibir_dataframe'):
        st.write(previsao_renda_filter)

with right_column:
    st.markdown('#### Metadados do Dataframe:')
    st.markdown('O Dataframe abaixo contém os metadados de todas as variáveis do Dataframe utilizado.')
    if st.checkbox('Exibir os metadados do DataFrame', key='exibir_metadados'):
        st.write(metadados)

st.markdown('----')

# Gráficos de distribuição das variáveis qualitativas ao longo do tempo
st.markdown('### Gráficos da distribuição das variáveis qualitativas ao longo do tempo:')
st.markdown('Para os seguintes gráficos o eixo X apresenta o tempo analisado e o eixo Y pode variar entre uma contagem total ou normalizada.')
st.markdown(' ')

st.sidebar.markdown('### Gráficos da distribuição das variáveis qualitativas ao longo do tempo:')

# Visualização de todas as variáveis qualitativas
if st.sidebar.checkbox('Exibir todas as variáveis', key='exibir_todas_variaveis'):
    var_qualitativo = previsao_renda_filter.select_dtypes(exclude=['int64', 'float64', 'datetime']).columns
    chosen_comp = st.sidebar.radio('Escolha como observar as distribuições:', ('Empilhada', 'Sobreposta', 'Porcentagem'))
    
    # Mapeamento correto para os valores aceitos pelo Streamlit
    if chosen_comp == 'Empilhada':
        chosen_comp = 'center'
    elif chosen_comp == 'Sobreposta':
        chosen_comp = 'layered'
    elif chosen_comp == 'Porcentagem':
        chosen_comp = 'normalize'
    
    for var in var_qualitativo:
        tab_freq = pd.crosstab(previsao_renda_filter['data_ref'], previsao_renda_filter[var])
        st.markdown(f'#### Distribuição da variável explicativa {var} ao longo do tempo:')
        st.bar_chart(tab_freq, x_label='Data', y_label='Contagem', stack=chosen_comp)

else:
    var_qualitativo = previsao_renda_filter.select_dtypes(exclude=['int64', 'float64', 'datetime']).columns
    selectbox_var_comp = st.sidebar.selectbox('Escolha a variável:', var_qualitativo)
    tab_freq = pd.crosstab(previsao_renda_filter['data_ref'], previsao_renda_filter[selectbox_var_comp])
    st.markdown(f'##### Distribuição da variável explicativa {selectbox_var_comp} ao longo do tempo:')
    chosen = st.sidebar.radio('Escolha como quer observar a distribuição:', ('Empilhada', 'Sobreposta', 'Porcentagem'))

    # Mapeamento correto para os valores aceitos pelo Streamlit
    if chosen == 'Empilhada':
        chosen = 'center'
    elif chosen == 'Sobreposta':
        chosen = 'layered'
    elif chosen == 'Porcentagem':
        chosen = 'normalize'

    st.bar_chart(tab_freq, x_label='Data', y_label='Contagem', stack=chosen)

    if st.sidebar.checkbox('Comparar com outra variável?', key='comparar_outra_variavel'):
        selectbox_var_comp = st.sidebar.selectbox('Escolha a variável:', var_qualitativo)
        tab_freq = pd.crosstab(previsao_renda_filter['data_ref'], previsao_renda_filter[selectbox_var_comp])
        st.bar_chart(tab_freq, x_label='Data', y_label='Contagem', stack=chosen)

# Gráficos da estabilidade das variáveis qualitativas ao longo do tempo
st.markdown('### Gráficos da estabilidade das variáveis qualitativas ao longo do tempo:')
st.sidebar.markdown('### Gráficos da estabilidade das variáveis qualitativas ao longo do tempo:')

if st.sidebar.checkbox('Exibir todas as variáveis', key='exibir_variaveis_estabilidade'):
    point(previsao_renda_filter)
else:
    var_qualitativo = previsao_renda_filter.select_dtypes(exclude=['int64', 'float64', 'datetime']).columns
    selectbox_var_est = st.sidebar.selectbox('Escolha a variável:', var_qualitativo)
    point_unico(selectbox_var_est)

    if st.sidebar.checkbox('Comparar com outra variável?', key='comparar_variavel_estabilidade'):
        selectbox_var_comp_est = st.sidebar.selectbox('Escolha a variável:', var_qualitativo)
        point_unico(selectbox_var_comp_est)

# Gráficos da distribuição das variáveis quantitativas
st.markdown('### Gráficos da distribuição das variáveis quantitativas:')
st.sidebar.markdown('### Gráficos da distribuição das variáveis quantitativas:')

if st.sidebar.checkbox('Exibir todas as variáveis', key='exibir_todas_quantitativas'):
    hist_todos(previsao_renda_filter)
else:
    var_quantitativo = previsao_renda_filter.select_dtypes(exclude=['bool', 'object', 'datetime']).columns
    selectbox_var_quant = st.sidebar.selectbox('Escolha a variável:', var_quantitativo)
    hist(selectbox_var_quant)

    if st.sidebar.checkbox('Comparar com outra variável?', key='comparar_variavel_quantitativa'):
        selectbox_var_comp_quant = st.sidebar.selectbox('Escolha a variável:', var_quantitativo)
        hist(selectbox_var_comp_quant)

st.sidebar.button('Recarregar')
