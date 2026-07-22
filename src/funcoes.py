import pyodbc 
import requests

# Conectando ao banco 
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

conecta_banco()

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
            administrador
        FROM funcionarios_tb
        """

        cursor.execute(query)

        resultado = cursor.fetchall()

        funcionarios = []

        for row in resultado:
            funcionarios.append({
                "id_funcionario": row[0],
                "nome_funcionario": row[1],
                "administrador": row[2]
            })

        return True, funcionarios

    except pyodbc.Error as e:

        return False, f"Erro ao consultar funcionarios:\n{e}"

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()