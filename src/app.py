import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import funcoes as fn

# Configuradno titulo da página do streamlit
st.set_page_config(
    page_title="Help Desk",
    page_icon="💻",
    layout="wide"
)

# Mudando de estilo para os gráficos
sns.set_theme(style="whitegrid")

# Imprtar dados aqui 
# Gerar DF com o vw_envio
# df = pd.read_csv("")

# Sidebar
st.sidebar.title("Login")
st.sidebar.markdown("Insira seu usuário de Login:")

usuadmin = ["Usuário", "Administrador"]

with st.sidebar:

    sucesso, funcionarios = fn.consulta_funcionarios()

    if sucesso and funcionarios:
        funcionario_selecionado = st.selectbox(
            "Selecione o funcionário",
            options=funcionarios,
            format_func=lambda funcionario: funcionario["nome_funcionario"]
        )

        administrador = funcionario_selecionado["administrador"]

    else:
        if not sucesso:
            st.error(f"Erro ao buscar funcionários: {funcionarios}")
        else:
            st.warning("Nenhum funcionário cadastrado no sistema.")

        id_funcionario = None


if administrador is not None:

    if administrador == 1:
        st.title("Bem-vindo Administrador")
    else:
        st.title("Bem-vindo Usuário")
