select *
from public.entradas

select *
from public.participantes

CREATE TABLE participantes (
 id INT PRIMARY KEY,
 projeto_id INT NOT NULL,
 codigo_participante VARCHAR(20) NOT NULL,
 nome VARCHAR(100) NOT NULL,
 empresa_vinculada CHAR(1) -- 'S' ou 'N'
);
CREATE TABLE entradas (
 id INT PRIMARY KEY,
 projeto_id INT NOT NULL,
 codigo_participante VARCHAR(20) NOT NULL,
 valor NUMERIC(18,2) NOT NULL -- devolução vem negativa
);
INSERT INTO participantes VALUES
 (1, 10, 'F001', 'Acme GmbH', 'S'),
 (2, 10, 'F002', 'Beta Ltda', 'N'),
 (3, 10, 'F001', 'ACME GMBH', 'S'),
 (4, 10, 'F003', 'Gamma Inc', 'N'),
 (5, 10, 'F003', 'Gamma Inc.', 'S'),
 (6, 20, 'F002', 'Beta Ltda', 'S');
INSERT INTO entradas VALUES
 (1, 10, 'F001', 1000.00),
 (2, 10, 'F001', 500.00),
 (3, 10, 'F002', 300.00),
 (4, 10, 'F003', 200.00),
 (5, 10, 'F004', 50.00),
 (6, 20, 'F002', 999.00),
 (7, 10, 'F002', -100.00);

 -- Codigo para a Consulta

WITH cadastro AS (
    -- uma linha por (projeto, código): vale a de menor id
    SELECT DISTINCT ON (projeto_id, codigo_participante)
           projeto_id,
           codigo_participante,
           empresa_vinculada
    FROM participantes
    WHERE projeto_id = 10
    ORDER BY projeto_id, codigo_participante, id
)
SELECT
    CASE
        WHEN c.codigo_participante IS NULL THEN 'Sem cadastro'
        WHEN c.empresa_vinculada = 'S'     THEN 'Vinculada'
        ELSE                                    'Terceiro'
    END                AS grupo,
    COUNT(*)           AS qtd_registros,
    SUM(e.valor)       AS total
FROM entradas e
LEFT JOIN cadastro c
       ON  c.projeto_id          = e.projeto_id
       AND c.codigo_participante = e.codigo_participante
WHERE e.projeto_id = 10
GROUP BY 1
ORDER BY 1;

--Pergunta escrita (responda em 2 ou 3 linhas): o que daria errado numa consulta que só fizesse JOIN
--participantes ON codigo_participante e depois somasse os valores?

--Um JOIN participantes ON codigo_participante simples teria três problemas. Primeiro, as entradas de F001 e F003 seriam duplicadas por causa das linhas repetidas no cadastro, inflando os totais (F001 passaria de 1.500 para 3.000). Segundo, sem o projeto_id no join, a entrada F002 do projeto 20 casaria com o cadastro do projeto 10 (e vice-versa), misturando empresas diferentes. Terceiro, o INNER JOIN descartaria a F004 (R$ 50,00), então a soma final não bateria com o total real das entradas.
