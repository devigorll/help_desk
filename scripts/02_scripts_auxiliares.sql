SELECT * FROM funcionarios_tb

INSERT INTO funcionarios_tb (nome_funcionario. )



SELECT * FROM setores_tb



SELECT * FROM funcionarios_tb



SELECT * FROM computadores_tb

ALTER TABLE computadores_tb
ADD tipo CHAR(8) NOT NULL --NOTEBOOK

UPDATE funcionarios_tb
SET nome_funcionario = 'Igor Cruz'
WHERE id_funcionario = 2

UPDATE funcionarios_tb
SET administrador = 1
WHERE id_funcionario = 2

UPDATE funcionarios_tb
SET id_setor = 2
WHERE id_funcionario = 2


SELECT * FROM setores_tb

EXEC sp_help