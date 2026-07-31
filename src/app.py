import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

import funcoes as fn


# Essa bomba aqui pra gambiarra do rótulo X na horizobntal
import altair as alt

st.set_page_config(
    page_title="Help Desk",
    page_icon="💻",
    layout="wide"
)

# Estilo gloal dos gráficos
sns.set_theme(style="whitegrid")

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

# Se JÁ ESTIVER LOGFADO, exibe as opções do usuário logado
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

    # ---------------------------------------------------------------------- ABA 01: ABRIR CHAMADO -------------------------------------------------------------------
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


    # ---------------------------------------------------------------------- ABA 02: FECHAR CHAMADO -------------------------------------------------------------------

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



    # ---------------------------------------------------------------------- ABA 03: GRÁFICO E ESTATÍSTICAS -------------------------------------------------------------------


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

                # Métricas e KPIs 
                total_chamados = len(df_todos_chamados)
                
                if 'status' in df_todos_chamados.columns:
                    total_fechados = len(df_todos_chamados[df_todos_chamados['status'] == 'Fechado'])
                    total_abertos = len(df_todos_chamados[df_todos_chamados['status'] != 'Fechado'])
                else:
                    total_fechados = 0
                    total_abertos = total_chamados

                taxa_resolucao = (total_fechados / total_chamados * 100) if total_chamados > 0 else 0

                hoje = date.today()
                if 'data_fechamento' in df_todos_chamados.columns and total_fechados > 0:
                    fechados_hoje = len(df_todos_chamados[df_todos_chamados['data_fechamento'].dt.date == hoje])
                    
                    # Cálculo de Tempo Médio de Resolução (SLA em Dias)
                    df_resolvidos_tempo = df_todos_chamados.dropna(subset=['data_abertura', 'data_fechamento'])
                    if not df_resolvidos_tempo.empty:
                        dias_resolucao = (df_resolvidos_tempo['data_fechamento'] - df_resolvidos_tempo['data_abertura']).dt.total_seconds() / (24 * 3600)
                        tempo_medio_dias = round(dias_resolucao.mean(), 1)
                    else:
                        tempo_medio_dias = 0
                else:
                    fechados_hoje = 0
                    tempo_medio_dias = 0

                # Blocos onde ficam as KPIs
                st.subheader("📌 Visão Geral de Desempenho")
                kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

                kpi1.metric(" Total Chamados", total_chamados)
                kpi2.metric("⏳ Em Aberto", total_abertos)
                kpi3.metric("✅ Resolvidos", total_fechados)
                kpi4.metric("📈 Taxa de Resolução", f"{taxa_resolucao:.1f}%")
                kpi5.metric("⏱️ SLA Médio", f"{tempo_medio_dias} dias")

                st.divider()

                col_graf1, col_graf2 = st.columns(2)

                # Gráfico 1: Chamados por Categoria (Colunas Verticais + Rótulos Horizontais)
                with col_graf1:
                    with st.container(border=True):
                        st.subheader("📂 Chamados por Categoria")
                        if 'categoria' in df_todos_chamados.columns and not df_todos_chamados['categoria'].dropna().empty:
                            df_cat = df_todos_chamados['categoria'].value_counts().reset_index()
                            df_cat.columns = ['Categoria', 'Quantidade']

                            chart_cat = alt.Chart(df_cat).mark_bar(color="#4C78A8").encode(
                                x=alt.X('Categoria:N', axis=alt.Axis(labelAngle=0, labelLimit=200), title="Categoria"),
                                y=alt.Y('Quantidade:Q', title="Quantidade")
                            ).properties(height=320)

                            st.altair_chart(chart_cat, use_container_width=True)
                        else:
                            st.info("Sem dados de categoria registrados.")

                # Gráfico 2: Chamados por Grau de Urgência (Colunas Verticais + Rótulos Horizontais)
                with col_graf2:
                    with st.container(border=True):
                        st.subheader("🚨 Graus de Urgência")
                        if 'grau_urgencia' in df_todos_chamados.columns and not df_todos_chamados['grau_urgencia'].dropna().empty:
                            df_urg = df_todos_chamados['grau_urgencia'].value_counts().reset_index()
                            df_urg.columns = ['Urgência', 'Quantidade']

                            chart_urg = alt.Chart(df_urg).mark_bar(color="#E15759").encode(
                                x=alt.X('Urgência:N', axis=alt.Axis(labelAngle=0, labelLimit=200), title="Urgência"),
                                y=alt.Y('Quantidade:Q', title="Quantidade")
                            ).properties(height=320)

                            st.altair_chart(chart_urg, use_container_width=True)
                        else:
                            st.info("Sem dados de urgência registrados.")

                st.write("")


                col_graf3, col_graf4 = st.columns([1.2, 0.8])

                with col_graf3:
                    with st.container(border=True):
                        st.subheader("🏆 Ranking de Atendimento por Técnico")
                        
                        if 'nome_tecnico' in df_todos_chamados.columns:
                            df_resolvidos = df_todos_chamados[
                                (df_todos_chamados['status'] == 'Fechado') & 
                                (df_todos_chamados['nome_tecnico'].notna())
                            ]
                            
                            if not df_resolvidos.empty:
                                ranking_tecnicos = (
                                    df_resolvidos.groupby('nome_tecnico')
                                    .size()
                                    .reset_index(name='Concluídos')
                                    .sort_values(by='Concluídos', ascending=False)
                                )
                                
                                st.bar_chart(ranking_tecnicos.set_index('nome_tecnico'), color="#59A14F", horizontal=True, use_container_width=True)
                            else:
                                st.info("Nenhum chamado foi encerrado por técnicos ainda.")
                        else:
                            st.info("Coluna de técnico não identificada na base.")

                with col_graf4:
                    with st.container(border=True):
                        st.subheader("📊 Status Atual")
                        
                        df_status = pd.DataFrame({
                            'Status': ['Em Aberto', 'Fechado'],
                            'Total': [total_abertos, total_fechados]
                        })
                        
                        st.dataframe(
                            df_status,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Status": st.column_config.TextColumn("Status"),
                                "Total": st.column_config.ProgressColumn(
                                    "Volume",
                                    format="%d",
                                    min_value=0,
                                    max_value=max(total_chamados, 1)
                                )
                            }
                        )

            elif sucesso_est and df_todos_chamados.empty:
                st.info("Ainda não existem chamados registrados na base de dados.")
            else:
                st.error("Erro ao carregar dados para o Dashboard.")

else:
    st.info("Por favor, selecione seu usuário e insira a senha na barra lateral para continuar.")