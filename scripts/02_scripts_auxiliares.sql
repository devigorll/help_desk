CREATE DATABASE helpdesk_db


CREATE TABLE computadores_tb (
	id_computador INT IDENTITY(1,1) NOT NULL,
	nome_computador VARCHAR(10) NOT NULL,
	sistema_operacional VARCHAR(20) NOT NULL,
	fabricante VARCHAR(20) NOT NULL,

	CONSTRAINT PK_COMPUTADORES_TB PRIMARY KEY (id_computador)

)

GO

CREATE TABLE setores_tb (
	id_setor INT IDENTITY(1,1) NOT NULL,
	nome_setor VARCHAR(40) NOT NULL,

	CONSTRAINT PK_SETORES_TB PRIMARY KEY (id_setor)
)

GO

CREATE TABLE funcionarios_tb (
	id_funcionario INT IDENTITY(1,1) NOT NULL,
	nome_funcionario VARCHAR(50) NOT NULL,
	id_setor INT NOT NULL,
	id_computador INT NOT NULL,
	administrador BIT NOT NULL DEFAULT 0,

	CONSTRAINT PK_FUNCIONARIOS_TB PRIMARY KEY (id_funcionario),

	CONSTRAINT FK_FUNCIONARIOS__SETOR FOREIGN KEY (id_setor) REFERENCES setores_tb(id_setor),
	CONSTRAINT FK_FUNCIONARIOS__COMPUTADORES FOREIGN KEY (id_computador)REFERENCES computadores_tb(id_computador)
)

GO

CREATE TABLE chamados_tb (
	id_chamado INT IDENTITY(1,1) NOT NULL,
	id_funcionario INT NOT NULL,
	status VARCHAR(20) NOT NULL,
	titulo VARCHAR(30) NOT NULL,
	decricao VARCHAR(100) NOT NULL,
	categoria VARCHAR(20) NOT NULL,
	grau_urgencia VARCHAR(20) NOT NULL,
	id_setor INT NOT NULL,
	id_computador INT NOT NULL,
	id_tecnico INT NOT NULL,
	data_abertura DATETIME NOT NULL,
	data_fechamento DATETIME NOT NULL,

	CONSTRAINT PK_CHAMADOS_TB PRIMARY KEY (id_chamado),

	CONSTRAINT FK_CHAMADOS__FUNCIONARIO FOREIGN KEY (id_funcionario) REFERENCES funcionarios_tb(id_funcionario),
	CONSTRAINT FK_CHAMADOS__SETOR FOREIGN KEY (id_setor) REFERENCES setores_tb(id_setor),
	CONSTRAINT FK_CHAMADOS__TECNICO FOREIGN KEY (id_tecnico) REFERENCES funcionarios_tb(id_funcionario),

)

-- TB COMPUTADORES

-- ID PC
-- NOME PC
-- SISTEMA 
-- FABRICANTE

-------------------

-- TB SETORES

-- ID SETOR
-- SETOR

-------------------

-- TB FUNCIONARIOS

-- ID FUNCIONARIOS
-- NOME FUNCIONARIO
-- ID SETOR
-- ID PC
-- ADMINSTRADOR (BOLEANO)

------------------

-- TB CHAMADOS

-- ID CHAMADO
-- ID FUNCIONARIO
-- STATUS
-- TITULO
-- DESCRICAO
-- CATEGORIA
-- GRAU DE URGENCIA
-- ID SETOR
-- ID PC
-- ID TECNICO
-- DATA DE ABERTURA
-- DATA FECHAMENTO

