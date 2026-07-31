import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

import funcoes as fn

# Configurando título da página do Streamlit
st.set_page_config(
    page_title="Help Desk",
    page_icon="💻",
    layout="wide"
)

# Estilo global dos gráficos
sns.set_theme(style="whitegrid")

# Inicialização das variáveis de sessão de autenticação
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = None

# Sidebar - Login / Seleção de Funcionário
st.sidebar.title("Login")

# Se NINGUÉM estiver logado, exibe a interface de verificação de senha
if st.session_state["usuario_logado"] is None:
    st.sidebar.markdown("Selecione o usuário e digite sua senha:")

    sucesso_func, funcionarios = fn.consulta_funcionarios()

    if sucesso_func and funcionarios:
        funcionario_selecionado = st.sidebar.selectbox(
            "Selecione o funcionário",
            options=funcionarios,
            format_func=lambda funcionario: funcionario["nome_funcionario"]
        )

        senha_digitada = st.sidebar.text_input("Senha", type="password")

        if st.sidebar.button("🔑 Entrar", use_container_width=True):
            if senha_digitada == funcionario_selecionado["senha"]:
                st.session_state["usuario_logado"] = funcionario_selecionado
                st.sidebar.success("Login realizado!")
                st.rerun()
            else:
                st.sidebar.error("❌ Senha incorreta!")
    else:
        if not sucesso_func:
            st.sidebar.error(f"Erro ao buscar funcionários: {funcionarios}")
        else:
            st.sidebar.warning("Nenhum funcionário cadastrado no sistema.")

# Se JÁ ESTIVER LOGADO, exibe as opções do usuário logado
else:
    funcionario_selecionado = st.session_state["usuario_logado"]
    st.sidebar.markdown(f"**Usuário:** {funcionario_selecionado['nome_funcionario']}")
    
    if st.sidebar.button("🚪 Sair", use_container_width=True):
        st.session_state["usuario_logado"] = None
        st.rerun()

# Define as variáveis do usuário corrente para o restando da aplicação
if st.session_state["usuario_logado"]:
    funcionario_selecionado = st.session_state["usuario_logado"]
    administrador = funcionario_selecionado["administrador"]
    id_funcionario_logado = funcionario_selecionado["id_funcionario"]
else:
    funcionario_selecionado = None
    administrador = None
    id_funcionario_logado = None

# Conteúdo Principal
if funcionario_selecionado:
    st.title(f"Bem-vindo, {funcionario_selecionado['nome_funcionario']}")

    # Busca detalhes de setor e computador do funcionário selecionado
    sucesso_det, detalhes = fn.consulta_detalhes_funcionario(id_funcionario_logado)

    # Organização das Abas
    if administrador == 1 or administrador is True:
        tab1, tab2, tab3 = st.tabs([
            "🆕 Abrir chamado",
            "✅ Fechar chamado",
            "📊 Dashboard & Estatísticas"
        ])
    else:
        tab1, tab2 = st.tabs([
            "🆕 Abrir chamado",
            "🔒 Área Restrita"
        ])

    # --- ABA 1: ABRIR CHAMADO ---
    with tab1:
        st.header("Abertura de Chamado")

        lista_categorias = ["Selecione...", "Hardware", "Software / Sistemas", "Redes / Internet", "Acessos e Permissões", "Outros"]
        lista_urgencia = ["Selecione...", "🟢 Baixa", "🟡 Média", "🔴 Alta", "🚨 Crítica"]

        with st.form(key="form_novo_chamado", clear_on_submit=True):
            st.subheader("📂 Formulário de Solicitação")

            col1, col2 = st.columns(2)

            with col1:
                st.text_input("Funcionário", value=funcionario_selecionado['nome_funcionario'], disabled=True)
                st.text_input("Setor", value=detalhes['nome_setor'] if sucesso_det else "Não localizado", disabled=True)
                categoria = st.selectbox("Categoria", lista_categorias)

            with col2:
                st.text_input("Computador", value=detalhes['nome_computador'] if sucesso_det else "Não localizado", disabled=True)
                urgencia = st.selectbox("Grau de Urgência", lista_urgencia)

            titulo = st.text_input("Título", placeholder="Ex: Monitor não liga, Erro ao acessar sistema...")

            descricao = st.text_area(
                "Descrição", 
                max_chars=200, 
                help="Descreva o problema em até 200 caracteres.",
                placeholder="Detalhe o ocorrido..."
            )

            submeter = st.form_submit_button("🚀 Abrir Chamado", use_container_width=True)

            if submeter:
                if categoria == "Selecione..." or urgencia == "Selecione..." or not titulo.strip() or not descricao.strip():
                    st.error("⚠️ Por favor, preencha todos os campos obrigatórios antes de enviar!")
                elif not sucesso_det:
                    st.error("Erro ao obter dados de Setor e Computador vinculados ao usuário.")
                else:
                    sucesso_ins, msg = fn.inserir_chamado(
                        id_funcionario=id_funcionario_logado,
                        titulo=titulo,
                        descricao=descricao,
                        categoria=categoria,
                        grau_urgencia=urgencia,
                        id_setor=detalhes['id_setor'],
                        id_computador=detalhes['id_computador']
                    )

                    if sucesso_ins:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"Erro ao registrar chamado: {msg}")

    # --- ABA 2: FECHAR CHAMADO ---
    with tab2:
        if administrador == 1 or administrador is True:
            st.header("Painel do Administrador - Fechamento de Chamados")

            sucesso_chamados, chamados_abertos = fn.consulta_chamados_abertos()

            if sucesso_chamados and chamados_abertos:
                st.subheader("Chamados em Aberto")
                
                df_chamados = pd.DataFrame(chamados_abertos)
                st.dataframe(df_chamados, use_container_width=True)

                st.divider()

                st.subheader("🔒 Encerrar Chamado")
                
                opcoes_chamados = {c["id_chamado"]: f"#{c['id_chamado']} - {c['titulo']} ({c['nome_funcionario']})" for c in chamados_abertos}

                id_chamado_selecionado = st.selectbox(
                    "Selecione o chamado para fechar",
                    options=list(opcoes_chamados.keys()),
                    format_func=lambda x: opcoes_chamados[x]
                )

                if st.button("✅ Confirmar Fechamento", use_container_width=True):
                    sucesso_fechar, msg_fechar = fn.fechar_chamado(
                        id_chamado=id_chamado_selecionado,
                        id_tecnico=id_funcionario_logado
                    )

                    if sucesso_fechar:
                        st.success(msg_fechar)
                        st.rerun()
                    else:
                        st.error(msg_fechar)

            elif sucesso_chamados and not chamados_abertos:
                st.info("Nenhum chamado aberto no momento.")
            else:
                st.error(f"Erro ao consultar chamados: {chamados_abertos}")

        else:
            st.warning("Esta aba é restrita apenas para administradores.")

    # --- ABA 3: DASHBOARD & ESTATÍSTICAS (APENAS ADMIN) ---
    if administrador == 1 or administrador is True:
        with tab3:
            st.header("📊 Painel Estatístico & Indicadores (KPIs)")

            sucesso_est, df_todos_chamados = fn.consulta_todos_chamados()

            if sucesso_est and not df_todos_chamados.empty:
                
                # Conversão segura de datas
                if 'data_abertura' in df_todos_chamados.columns:
                    df_todos_chamados['data_abertura'] = pd.to_datetime(df_todos_chamados['data_abertura'])
                if 'data_fechamento' in df_todos_chamados.columns:
                    df_todos_chamados['data_fechamento'] = pd.to_datetime(df_todos_chamados['data_fechamento'])

                # --- 1. CARDS / MÉTRICAS PRINCIPAIS ---
                total_chamados = len(df_todos_chamados)
                total_fechados = len(df_todos_chamados[df_todos_chamados['status'] == 'Fechado']) if 'status' in df_todos_chamados.columns else 0
                total_abertos = total_chamados - total_fechados

                hoje = date.today()
                if 'data_fechamento' in df_todos_chamados.columns and total_fechados > 0:
                    fechados_hoje = len(df_todos_chamados[df_todos_chamados['data_fechamento'].dt.date == hoje])
                else:
                    fechados_hoje = 0

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Registrado", total_chamados)
                m2.metric("Em Aberto", total_abertos)
                m3.metric("Total Resolvidos", total_fechados)
                m4.metric("Resolvidos Hoje", fechados_hoje)

                st.divider()

                # --- 2. GRÁFICOS CATEGORIA E URGÊNCIA ---
                col_graf1, col_graf2 = st.columns(2)

                with col_graf1:
                    st.subheader("📌 Chamados por Categoria")
                    if 'categoria' in df_todos_chamados.columns and not df_todos_chamados['categoria'].dropna().empty:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        order_cat = df_todos_chamados['categoria'].value_counts().index
                        
                        sns.countplot(
                            data=df_todos_chamados, 
                            y='categoria', 
                            order=order_cat, 
                            hue='categoria', 
                            palette='viridis', 
                            legend=False, 
                            ax=ax
                        )
                        ax.set_xlabel("Quantidade")
                        ax.set_ylabel("")
                        st.pyplot(fig)
                    else:
                        st.info("Sem dados de categoria registrados.")

                with col_graf2:
                    st.subheader("🚦 Chamados por Graus de Urgência")
                    if 'grau_urgencia' in df_todos_chamados.columns and not df_todos_chamados['grau_urgencia'].dropna().empty:
                        fig, ax = plt.subplots(figsize=(6, 4))
                        order_urg = df_todos_chamados['grau_urgencia'].value_counts().index
                        
                        sns.countplot(
                            data=df_todos_chamados, 
                            x='grau_urgencia', 
                            order=order_urg, 
                            hue='grau_urgencia', 
                            palette='rocket', 
                            legend=False, 
                            ax=ax
                        )
                        ax.set_xlabel("")
                        ax.set_ylabel("Quantidade")
                        plt.xticks(rotation=15)
                        st.pyplot(fig)
                    else:
                        st.info("Sem dados de urgência registrados.")

                st.divider()

                # --- 3. RANKING DE TÉCNICOS ---
                st.subheader("🏆 Ranking de Técnicos (Chamados Fechados)")
                
                if 'nome_tecnico' in df_todos_chamados.columns:
                    df_resolvidos = df_todos_chamados[
                        (df_todos_chamados['status'] == 'Fechado') & 
                        (df_todos_chamados['nome_tecnico'].notna())
                    ]
                    
                    if not df_resolvidos.empty:
                        fig, ax = plt.subplots(figsize=(10, 3.5))
                        
                        ranking_tecnicos = (
                            df_resolvidos.groupby('nome_tecnico')
                            .size()
                            .reset_index(name='quantidade')
                            .sort_values(by='quantidade', ascending=False)
                        )
                        
                        sns.barplot(
                            data=ranking_tecnicos, 
                            x='quantidade', 
                            y='nome_tecnico', 
                            hue='nome_tecnico', 
                            palette='magma', 
                            legend=False, 
                            ax=ax
                        )
                        ax.set_xlabel("Atendimentos Concluídos")
                        ax.set_ylabel("Técnico")
                        
                        max_val = ranking_tecnicos['quantidade'].max()
                        for i, v in enumerate(ranking_tecnicos['quantidade']):
                            ax.text(v + (max_val * 0.01 + 0.1), i, str(v), va='center', fontweight='bold')
                            
                        st.pyplot(fig)
                    else:
                        st.info("Nenhum chamado foi resolvido por técnicos ainda.")

            elif sucesso_est and df_todos_chamados.empty:
                st.info("Ainda não existem chamados registrados na base de dados.")
            else:
                st.error("Erro ao carregar dados para o Dashboard.")

else:
    st.info("Por favor, selecione seu usuário e insira a senha na barra lateral para continuar.")