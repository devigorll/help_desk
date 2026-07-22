# 🎧 Help Desk

> Status do Projeto: ⚠️ Em desenvolvimento

O **Help Desk** é um sistema para gerenciamento de chamados e suporte técnico. O foco principal do desenvolvimento no momento está na criação da estrutura da aplicação, integração com o banco de dados SQL Server e desenvolvimento da interface web utilizando Streamlit.

---

## 🛠️ Tecnologias e Ferramentas Utilizadas

* **Linguagens:** Python & SQL (SQL Server)
* **Interface / Dashboard:** Streamlit
* **Gerenciamento de Ambientes:** Virtualenv (`venv`)
* **Banco de Dados:** SQL Server

---

## 📁 Estrutura do Projeto

```text
help_desk/
│
├── data/                  # Arquivos e bases de dados locais
├── notebooks/             # Testes e scripts em Jupyter Notebook
│   └── 01_insercao_faker.ipynb
├── scripts/               # Scripts SQL auxiliares
│   ├── 01_criando_banco.sql
│   └── 02_scripts_auxiliares.sql
├── src/                   # Código-fonte principal da aplicação
│   ├── img/               # Imagens utilizadas na interface
│   ├── app.py             # Arquivo principal da aplicação Streamlit
│   └── funcoes.py         # Funções de integração com o banco de dados
│
├── .gitignore             # Arquivos ignorados pelo Git
├── README.md              # Documentação do projeto
├── requirements.txt       # Dependências do projeto
└── venv/                  # Ambiente virtual Python
```

---

## 🚀 Como Executar o Projeto

Certifique-se de estar com o ambiente virtual ativado.

Instale as dependências do projeto:

```bash
pip install -r requirements.txt
```

Acesse a pasta do código-fonte e execute a aplicação:

```bash
cd src
streamlit run app.py
```

---

## 👤 Autor

Desenvolvido por **Igor Cruz**.