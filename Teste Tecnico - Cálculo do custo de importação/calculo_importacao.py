"""Parte 2 - Cálculo do custo de importação.

Rode com:  python calculo_importacao.py
Usa apenas a biblioteca padrão (Fraction para evitar erro de ponto flutuante;
o arredondamento a 2 casas só acontece no fim de cada produto).
"""
from fractions import Fraction as F
from math import floor
from collections import defaultdict

# ----------------------------------------------------------------------------
# DADOS (R$) -> (saldo_ini_V, saldo_ini_T, compras_V, compras_T, saldo_fin_V, saldo_fin_T)
# ----------------------------------------------------------------------------
MPS = {
    "M1": (100, 0, 1000, 0, 200, 0),
    "M2": (0, 300, 0, 2000, 0, 500),
    "M3": (0, 100, 0, 200, 0, 500),
    "M4": (400, 0, 0, 1000, 200, 200),
    "M5": (0, 0, 0, 300, 0, 0),
    "R1": (0, 0, 500, 0, 100, 0),
}

# (produto, mp, coeficiente)
ESTRUTURA = [
    ("A1", "M1", 2), ("A1", "M2", 1),
    ("A2", "M1", 1), ("A2", "M2", 3), ("A2", "M4", 1),
    ("A3", "M2", 1), ("A3", "M3", 1),
    ("A4", "M5", 1),
    ("A5", "M1", 1),
    ("R1", "R1", 1),   # produto de revenda: é MP de si mesmo
]

# (produto, quantidade, receita líquida, CMV) - devolução = linha negativa
VENDAS = [
    ("A1", 100, 10000, 6000),
    ("A2", 50, 8000, 5000),
    ("A3", 250, 5000, 3750),
    ("A3", -50, -1000, -750),
    ("A5", 10, 250, 150),
    ("A5", -30, -750, -450),
    ("R1", 40, 1000, 350),
]


def r2(x):
    """Arredonda para 2 casas (meio para cima, afastando de zero)."""
    x = F(x) * 100
    n = floor(abs(x) + F(1, 2))
    return (n if x >= 0 else -n) / 100


def brl(x):
    s = f"{float(x):,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    # --- vendas líquidas por produto (soma devoluções) ----------------------
    qtd, rec, cmv = defaultdict(F), defaultdict(F), defaultdict(F)
    for p, q, r, c in VENDAS:
        qtd[p] += q
        rec[p] += r
        cmv[p] += c

    # --- Regra 1: consumo por origem ----------------------------------------
    consumo = {}
    for mp, (siv, sit, cv, ct, sfv, sft) in MPS.items():
        consumo[mp] = (F(siv + cv - sfv), F(sit + ct - sft))

    # --- Regra 2: consumo negativo (total, V ou T) descarta a MP inteira ----
    descartadas = {mp for mp, (v, t) in consumo.items() if v < 0 or t < 0 or v + t < 0}

    # --- Regras 3 e 4: rateio ------------------------------------------------
    # Decisão: só entra no rateio produto com quantidade líquida > 0 no ano
    # (um produto com devolução maior que a venda, como A5, teria peso negativo).
    custo_v, custo_t = defaultdict(F), defaultdict(F)
    nao_alocado = {}
    for mp, (v, t) in consumo.items():
        if mp in descartadas:
            continue
        pesos = {p: F(c) * qtd[p] for p, m, c in ESTRUTURA if m == mp and qtd[p] > 0}
        total_peso = sum(pesos.values())
        if total_peso == 0:                      # regra 4
            nao_alocado[mp] = (v, t)
            continue
        for p, w in pesos.items():
            custo_v[p] += v * w / total_peso
            custo_t[p] += t * w / total_peso

    # --- Regras 5 a 8: resultado por produto --------------------------------
    resultado = []
    for p in sorted(set(custo_v) | set(custo_t)):
        cv, ct = custo_v[p], custo_t[p]
        ctot = cv + ct
        if ctot <= 0 or cmv[p] <= 0:             # regra 5 (e guarda de CMV)
            continue
        pct = min(ctot / cmv[p], F(1))           # regra 6
        vp = rec[p] * pct                        # regra 7
        vp_v = vp * cv / ctot
        vp_r = r2(vp)
        vp_v_r = r2(vp_v)
        resultado.append(dict(
            produto=p, cv=r2(cv), ct=r2(ct), ctot=r2(ctot),
            pct=pct, vp=vp_r, vp_v=vp_v_r, vp_t=vp_r - vp_v_r,   # T = resto
            cv_raw=cv, ct_raw=ct,
        ))

    # ======================= SAÍDA ===========================================
    print("=" * 96)
    print("RESULTADO POR PRODUTO (R$)")
    print("=" * 96)
    print(f"{'Prod':<5}{'Custo V':>11}{'Custo T':>11}{'Custo Total':>13}{'% Import.':>11}"
          f"{'Venda Prop.':>13}{'Prop. V':>11}{'Prop. T':>11}")
    for r in resultado:
        print(f"{r['produto']:<5}{brl(r['cv']):>11}{brl(r['ct']):>11}{brl(r['ctot']):>13}"
              f"{float(r['pct'])*100:>10.2f}%{brl(r['vp']):>13}{brl(r['vp_v']):>11}{brl(r['vp_t']):>11}")
    print(f"{'TOTAL':<5}{brl(sum(r['cv'] for r in resultado)):>11}"
          f"{brl(sum(r['ct'] for r in resultado)):>11}{brl(sum(r['ctot'] for r in resultado)):>13}"
          f"{'':>11}{brl(sum(r['vp'] for r in resultado)):>13}"
          f"{brl(sum(r['vp_v'] for r in resultado)):>11}{brl(sum(r['vp_t'] for r in resultado)):>11}")

    # --- Conciliação ---------------------------------------------------------
    compras = (F(sum(m[2] for m in MPS.values())), F(sum(m[3] for m in MPS.values())))
    si = (F(sum(m[0] for m in MPS.values())), F(sum(m[1] for m in MPS.values())))
    sf = (F(sum(m[4] for m in MPS.values())), F(sum(m[5] for m in MPS.values())))
    bruto = (sum(v for v, _ in consumo.values()), sum(t for _, t in consumo.values()))
    desc = (sum((consumo[m][0] for m in descartadas), F(0)),
            sum((consumo[m][1] for m in descartadas), F(0)))
    elegivel = (bruto[0] - desc[0], bruto[1] - desc[1])
    naoal = (sum((v for v, _ in nao_alocado.values()), F(0)),
             sum((t for _, t in nao_alocado.values()), F(0)))
    alocado = (elegivel[0] - naoal[0], elegivel[1] - naoal[1])
    soma_prod = (sum(custo_v.values(), F(0)), sum(custo_t.values(), F(0)))
    fora = (soma_prod[0] - sum((r['cv_raw'] for r in resultado), F(0)),
            soma_prod[1] - sum((r['ct_raw'] for r in resultado), F(0)))

    def linha(nome, par, sinal=""):
        v, t = par
        print(f"{sinal:<4}{nome:<58}{brl(v + t):>11}{brl(v):>11}{brl(t):>11}")

    print()
    print("=" * 96)
    print("CONCILIAÇÃO (R$)")
    print("=" * 96)
    print(f"{'':<4}{'':<58}{'Total':>11}{'V':>11}{'T':>11}")
    linha("Compras do ano", compras)
    linha("Saldo inicial", si, "(+)")
    linha("Saldo final", sf, "(-)")
    linha("Consumo bruto (soma dos consumos, inclui negativos)",
          (compras[0] + si[0] - sf[0], compras[1] + si[1] - sf[1]), "(=)")
    linha(f"Consumo descartado pela regra 2 ({', '.join(sorted(descartadas)) or '-'})", desc, "(-)")
    linha("Consumo elegível ao rateio", elegivel, "(=)")
    linha(f"Consumo não alocado, regra 4 ({', '.join(sorted(nao_alocado)) or '-'})", naoal, "(-)")
    linha("Total alocado aos produtos", alocado, "(=)")
    linha("Custo de importação somado dos produtos no resultado",
          (soma_prod[0] - fora[0], soma_prod[1] - fora[1]), "")
    linha("Diferença (alocado a produtos fora do resultado)", fora, "")

    # verificações de fechamento
    assert bruto == (compras[0] + si[0] - sf[0], compras[1] + si[1] - sf[1])
    assert alocado == soma_prod, "rateio não fecha com o consumo"
    assert fora == (0, 0), "há custo alocado a produto fora do resultado"
    print("\nOK: todas as linhas da conciliação fecham.")


if __name__ == "__main__":
    main()
