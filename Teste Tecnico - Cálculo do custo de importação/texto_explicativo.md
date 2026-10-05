# Texto explicativo

## (a) Por que as compras do ano não são iguais ao total alocado

Comprar não é consumir. Das compras de R$ 5.000, parte ficou no estoque: 5.000 + 900 (saldo inicial) − 1.700 (saldo final) = 4.200 de consumo bruto. Depois disso:

- A M3 teve consumo negativo (−200) e saiu do cálculo pela regra 2, o que leva o consumo para 4.400.
- A M5 (R$ 300) só é usada pelo A4, que não vendeu, então ficou não alocada.

4.400 − 300 = 4.100, que é o total alocado aos produtos (V 1.500 e T 2.600).

## (b) Coeficiente direto, sem o rateio

Cada produto levaria o consumo inteiro da MP vezes o coeficiente, e a soma passaria do consumo real. Na M2 (consumo 1.800), o A1 levaria 1.800, o A2 5.400 e o A3 1.800: dá 9.000 para uma MP que consumiu 1.800. O custo de importação ficaria inflado, vários produtos bateriam o teto de 100% e a conciliação não fecharia. Também ignoraria quanto cada produto vendeu. O rateio resolve isso porque divide por coeficiente × quantidade vendida e a soma sempre volta ao consumo.

## (c) Decisões em casos não previstos

- **A5:** a quantidade líquida é −20 (10 vendidas, 30 devolvidas). Peso negativo bagunçaria o rateio, então só entra produto com quantidade líquida maior que zero. O A5 fica sem custo e a M1 é dividida entre A1 e A2.
- **Devoluções:** quantidade, receita e CMV são sempre líquidos (ex.: A3 fica com 200 un., 4.000 de receita e 3.000 de CMV).
- **M3 na conciliação:** o descartado aparece com sinal negativo (−200), por isso o consumo elegível (4.400) é maior que o bruto (4.200).
- **R1:** o custo (400) passa o CMV (350), então o percentual é travado em 100% e a venda proporcionalizada fica igual à receita (1.000).
- **Arredondamento:** só no fim de cada produto, meio para cima. A parcela de terceiros é o total menos a vinculada, para V + T sempre fechar.
- **CMV líquido ≤ 0:** o produto fica fora do resultado, para evitar divisão por zero (não ocorre nestes dados).

## Exemplos para testar

Para testar, basta trocar os blocos `MPS`, `ESTRUTURA` e `VENDAS` no topo do `calculo_importacao.py` por um dos exemplos abaixo e rodar de novo. Cada linha de `MPS` é `(saldo inicial V, saldo inicial T, compras V, compras T, saldo final V, saldo final T)`.

### Exemplo 1: caso simples (nenhuma exceção)

```python
MPS = {
    "X1": (0, 0, 600, 400, 100, 0),
    "X2": (50, 50, 0, 200, 0, 50),
}

ESTRUTURA = [
    ("P1", "X1", 1), ("P1", "X2", 2),
    ("P2", "X1", 3),
]

VENDAS = [
    ("P1", 10, 2000, 1200),
    ("P2", 20, 3000, 2500),
]
```

Resultado esperado:

| Prod | Custo V | Custo T | Total | % Import. | Venda prop. | V | T |
|---|---|---|---|---|---|---|---|
| P1 | 121,43 | 257,14 | 378,57 | 31,55% | 630,95 | 202,38 | 428,57 |
| P2 | 428,57 | 342,86 | 771,43 | 30,86% | 925,71 | 514,29 | 411,42 |

Conciliação: compras 1.200 → consumo bruto 1.150 → descartado 0 → não alocado 0 → total alocado 1.150 (V 550 e T 600).

### Exemplo 2: casos de exceção

```python
MPS = {
    "Y1": (0, 0, 0, 500, 100, 0),
    "Y2": (200, 100, 300, 100, 100, 50),
    "Y3": (0, 0, 200, 0, 0, 0),
    "Y4": (0, 0, 0, 900, 0, 100),
}

ESTRUTURA = [
    ("Q1", "Y1", 1), ("Q1", "Y2", 2),
    ("Q2", "Y2", 1), ("Q2", "Y4", 1),
    ("Q3", "Y3", 1),
]

VENDAS = [
    ("Q1", 30, 3000, 2000),
    ("Q2", 10, 1000, 600),
    ("Q2", -2, -200, -120),   # devolução parcial
]
```

O que cada caso testa:
- **Y1:** consumo V de −100 e T de +500 (total positivo de 400). A MP inteira sai pela regra 2 porque uma das origens é negativa.
- **Y3:** só é usada pelo Q3, que não vendeu, então fica não alocada (regra 4).
- **Q2:** com a devolução, a quantidade líquida é 8. O custo (864,71) passa o CMV líquido (480), então o percentual trava em 100%.

Resultado esperado:

| Prod | Custo V | Custo T | Total | % Import. | Venda prop. | V | T |
|---|---|---|---|---|---|---|---|
| Q1 | 352,94 | 132,35 | 485,29 | 24,26% | 727,94 | 529,41 | 198,53 |
| Q2 | 47,06 | 817,65 | 864,71 | 100% | 800,00 | 43,54 | 756,46 |

Conciliação: compras 2.000 → consumo bruto 1.950 → descartado 400 (Y1) → consumo elegível 1.550 → não alocado 200 (Y3) → total alocado 1.350 (V 400 e T 950).
