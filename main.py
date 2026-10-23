import sqlite3 as sq
import pandas as pd
import streamlit as st
import urllib.parse

st.set_page_config(page_title="Gerenciador de Endereços", layout="wide")
st.title("📍 Endereços Itaúna-MG")

def conectarDB():
    conn = sq.connect('cepsItaunaMG.db')
    return conn


def pesquisar_cep(keyword):
    if len(keyword) == 8:
        conn = conectarDB()
        cursor = conn.cursor()
        cursor.execute('SELECT ID, logradouro, bairro FROM enderecos WHERE id LIKE ?', (f'%{keyword}%',))
        result = cursor.fetchall()
        conn.close()
        return result
    else:
        st.warning('O cep tem que conter 8 dígitos!')
        return ''


def pesquisar_logradouro(keyword):
    conn = conectarDB()
    cursor = conn.cursor()
    cursor.execute('SELECT cep, logradouro, bairro FROM enderecos WHERE logradouro LIKE ?', (f'%{keyword}%',))
    result = cursor.fetchall()
    conn.close()
    return result


@st.cache_data
def carregar_dados():
    try:
        conn = conectarDB()
        query = "SELECT * FROM enderecos"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return pd.DataFrame()


st.subheader('Buscar pelo CEP')
query = st.text_input('Digite o cep:')
if query:
    results = pesquisar_cep(query)
    for r in results:        
        pesquisa_cep = f'{r[0]} - {r[1]} - {r[2]}'
        texto_cep = urllib.parse.quote(pesquisa_cep)
        s = "None"
        if s in texto_cep:
            st.warning('CEP não encontrado!')
        else:
            st.success(pesquisa_cep)
            url_maps_cep = f"https://www.google.com/search?q={texto_cep}, Itaúna-MG"
            st.link_button('MAPS', url_maps_cep)


st.subheader('Buscar pelo endereço')
query1 = st.text_input('Digite o nome da rua/av./rod.:')
if query1:
    resposta = pesquisar_logradouro(query1)
    if resposta == []:
        st.warning('Endereço não encontrado!')            
    else:    
        for res in resposta:
            pesquisa_rua = f'{res[0]} - {res[1]} - {res[2]}'
            texto_rua = urllib.parse.quote(pesquisa_rua)
            st.success(pesquisa_rua)
            url_maps_rua = f"https://www.google.com/search?q={texto_rua}, Itaúna-MG"
            st.link_button('MAPS', url_maps_rua)


if st.button('Listar tabela CEP'):
    df_enderecos = carregar_dados()
    if not df_enderecos.empty:
        def gerar_url_maps(row):
            endereco_completo = f"{row.get('logradouro', '')}, {row.get('bairro', '')}"
            texto_busca = urllib.parse.quote(endereco_completo)
            return f"https://www.google.com/search?q={texto_busca}, Itaúna-MG"

        df_enderecos["Google Maps"] = df_enderecos.apply(gerar_url_maps, axis=1)

        colunas_originais = [col for col in df_enderecos.columns if col != "Google Maps"]
        nova_ordem = ["Google Maps"] + colunas_originais
        df_enderecos = df_enderecos[nova_ordem]

        st.write("Todos os endereços de Itaúna-MG")
        
        st.dataframe(
            df_enderecos,
            column_config={
                "Google Maps": st.column_config.LinkColumn(
                    "Ação",                      
                    help="Clique para abrir este endereço no Google Maps",
                    validate="^https://.*",
                    display_text="🌐Maps"
                )
            },
            hide_index=True,
            width='stretch'
        )
    else:
        st.warning("Nenhum dado encontrado ou tabela 'enderecos' vazia.")
