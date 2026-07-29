import pandas as pd
import pyodbc


# Conectando ao banco SQL Server
def conecta_banco():
    try:
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=helpdesk_db;"
            "Trusted_Connection=yes;"
        )
        return conn
    except pyodbc.Error as e:
        print(f"Erro ao conectar ao banco: {e}")
        return None


def consulta_funcionarios():
    conn = conecta_banco()

    if conn is None:
        return False, "Não foi possível conectar ao banco."

    cursor = None
    try:
        cursor = conn.cursor()

        query = """
        SELECT
            id_funcionario,
            nome_funcionario,
            id_setor,
            id_computador,
            administrador
        FROM funcionarios_tb
        """

        cursor.execute(query)
        resultado = cursor.fetchall()

        funcionarios = []
        for row in resultado:
            funcionarios.append(
                {
                    "id_funcionario": row[0],
                    "nome_funcionario": row[1],
                    "id_setor": row[2],
                    "id_computador": row[3],
                    "administrador": row[4],
                }
            )

        return True, funcionarios

    except pyodbc.Error as e:
        return False, f"Erro ao consultar funcionarios:\n{e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def consulta_detalhes_funcionario(id_funcionario):
    conn = conecta_banco()

    if conn is None:
        return False, "Não foi possível conectar ao banco."

    cursor = None
    try:
        cursor = conn.cursor()

        query = """
        SELECT 
            f.id_setor, 
            s.nome_setor, 
            f.id_computador, 
            c.nome_computador
        FROM funcionarios_tb f
        INNER JOIN setores_tb s ON f.id_setor = s.id_setor
        INNER JOIN computadores_tb c ON f.id_computador = c.id_computador
        WHERE f.id_funcionario = ?
        """

        cursor.execute(query, (id_funcionario,))
        row = cursor.fetchone()

        if row:
            detalhes = {
                "id_setor": row[0],
                "nome_setor": row[1],
                "id_computador": row[2],
                "nome_computador": row[3],
            }
            return True, detalhes
        else:
            return False, "Funcionário não encontrado."

    except pyodbc.Error as e:
        return False, f"Erro ao consultar detalhes do funcionário:\n{e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def inserir_chamado(
    id_funcionario,
    titulo,
    descricao,
    categoria,
    grau_urgencia,
    id_setor,
    id_computador,
):
    conn = conecta_banco()

    if conn is None:
        return False, "Não foi possível conectar ao banco."

    cursor = None
    try:
        cursor = conn.cursor()

        query = """
        INSERT INTO chamados_tb (
            id_funcionario,
            status,
            titulo,
            decricao,
            categoria,
            grau_urgencia,
            id_setor,
            id_computador,
            id_tecnico,
            data_abertura,
            data_fechamento
        )
        VALUES (?, 'Aberto', ?, ?, ?, ?, ?, ?, NULL, GETDATE(), NULL)
        """

        cursor.execute(
            query,
            (
                id_funcionario,
                titulo,
                descricao,
                categoria,
                grau_urgencia,
                id_setor,
                id_computador,
            ),
        )

        conn.commit()
        return True, "Chamado aberto com sucesso!"

    except pyodbc.Error as e:
        return False, f"Erro ao inserir chamado:\n{e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def consulta_chamados_abertos():
    conn = conecta_banco()

    if conn is None:
        return False, "Não foi possível conectar ao banco."

    cursor = None
    try:
        cursor = conn.cursor()

        query = """
        SELECT 
            ch.id_chamado,
            f.nome_funcionario,
            ch.titulo,
            ch.decricao,
            ch.categoria,
            ch.grau_urgencia,
            s.nome_setor,
            c.nome_computador,
            ch.data_abertura
        FROM chamados_tb ch
        INNER JOIN funcionarios_tb f ON ch.id_funcionario = f.id_funcionario
        INNER JOIN setores_tb s ON ch.id_setor = s.id_setor
        INNER JOIN computadores_tb c ON ch.id_computador = c.id_computador
        WHERE ch.status = 'Aberto'
        """

        cursor.execute(query)
        resultado = cursor.fetchall()

        chamados = []
        for row in resultado:
            chamados.append(
                {
                    "id_chamado": row[0],
                    "nome_funcionario": row[1],
                    "titulo": row[2],
                    "descricao": row[3],
                    "categoria": row[4],
                    "grau_urgencia": row[5],
                    "nome_setor": row[6],
                    "nome_computador": row[7],
                    "data_abertura": row[8],
                }
            )

        return True, chamados

    except pyodbc.Error as e:
        return False, f"Erro ao consultar chamados abertos:\n{e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def fechar_chamado(id_chamado, id_tecnico):
    conn = conecta_banco()

    if conn is None:
        return False, "Não foi possível conectar ao banco."

    cursor = None
    try:
        cursor = conn.cursor()

        query = """
        UPDATE chamados_tb
        SET status = 'Fechado',
            id_tecnico = ?,
            data_fechamento = GETDATE()
        WHERE id_chamado = ?
        """

        cursor.execute(query, (id_tecnico, id_chamado))
        conn.commit()

        return True, f"Chamado #{id_chamado} fechado com sucesso!"

    except pyodbc.Error as e:
        return False, f"Erro ao fechar chamado:\n{e}"

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def consulta_todos_chamados():
    """Retorna todos os chamados em formato pandas DataFrame para alimentar os gráficos do Dashboard no Streamlit."""
    conn = conecta_banco()

    if conn is None:
        return False, "Não foi possível conectar ao banco de dados."

    try:
        query = """
        SELECT 
            c.id_chamado,
            c.titulo,
            c.decricao AS descricao,
            c.categoria,
            c.grau_urgencia,
            c.status,
            c.data_abertura,
            c.data_fechamento,
            f.nome_funcionario AS nome_solicitante,
            t.nome_funcionario AS nome_tecnico
        FROM chamados_tb c
        INNER JOIN funcionarios_tb f ON c.id_funcionario = f.id_funcionario
        LEFT JOIN funcionarios_tb t ON c.id_tecnico = t.id_funcionario
        """

        # Utiliza o pandas para ler diretamente a query da conexão pyodbc
        df_chamados = pd.read_sql_query(query, conn)

        return True, df_chamados

    except Exception as e:
        return False, f"Erro ao consultar dados estatísticos: {e}"

    finally:
        if conn:
            conn.close()