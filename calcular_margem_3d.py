"""
Calculadora de margem para os candidatos descobertos no dia.

Diferente do descobrir_produtos_3d.py, ESTE script não roda sozinho no
agendamento — você roda na mão quando quiser avaliar os candidatos do dia,
porque ele precisa que você digite quanto vai gastar de filamento e por
quanto pretende vender.

COMO USAR:
    python3 calcular_margem_3d.py
Ele pega o candidatos_AAAA-MM-DD.csv mais recente automaticamente.
"""

import csv
import glob
import os

TAXAS_PLATAFORMA = {
    "ml": 0.14,
    "shopee": 0.18,
    "loja_propria": 0.03,  # ex: taxa de gateway de pagamento
}


def calcular_margem(custo_producao, preco_venda, plataforma):
    taxa = TAXAS_PLATAFORMA.get(plataforma.lower(), 0.15)
    receita_liquida = preco_venda * (1 - taxa)
    lucro = receita_liquida - custo_producao
    margem_pct = (lucro / preco_venda) * 100 if preco_venda > 0 else 0
    return round(lucro, 2), round(margem_pct, 1)


def custo_producao_3d(peso_g, custo_filamento_kg, horas_impressao, custo_hora_energia):
    custo_filamento = (peso_g / 1000) * custo_filamento_kg
    custo_energia = horas_impressao * custo_hora_energia
    return round(custo_filamento + custo_energia, 2)


def arquivo_mais_recente():
    arquivos = sorted(glob.glob('candidatos_*.csv'))
    return arquivos[-1] if arquivos else None


def main():
    arquivo = arquivo_mais_recente()
    if not arquivo:
        print("Nenhum candidatos_AAAA-MM-DD.csv encontrado.")
        print("Rode primeiro: python3 descobrir_produtos_3d.py")
        return

    print(f"Usando: {arquivo}\n")
    with open(arquivo, newline='', encoding='utf-8') as f:
        candidatos = list(csv.DictReader(f))

    print(f"{len(candidatos)} candidatos encontrados. Para cada um, digite os")
    print("dados de impressão (ou 's' pra pular).\n")

    resultados = []
    custo_filamento_kg = float(input("Preço do seu filamento por kg (R$): ").strip().replace(',', '.'))
    custo_hora_energia = float(input("Custo estimado de energia por hora de impressão (R$, padrão 0.80): ").strip().replace(',', '.') or "0.80")

    for i, c in enumerate(candidatos):
        print(f"\n[{i+1}/{len(candidatos)}] {c['termo']} (sinal: {c['tipo_sinal']})")
        resposta = input("  Peso estimado da peça em gramas (ou 's' pra pular): ").strip()
        if resposta.lower() == 's':
            continue
        peso_g = float(resposta.replace(',', '.'))
        horas = float(input("  Horas de impressão estimadas: ").strip().replace(',', '.'))
        preco_venda = float(input("  Preço de venda pretendido (R$): ").strip().replace(',', '.'))
        plataforma = input("  Plataforma (ml/shopee/loja_propria): ").strip() or "shopee"

        custo = custo_producao_3d(peso_g, custo_filamento_kg, horas, custo_hora_energia)
        lucro, margem_pct = calcular_margem(custo, preco_venda, plataforma)

        resultados.append({
            'termo': c['termo'],
            'plataforma': plataforma,
            'custo_producao': custo,
            'preco_venda': preco_venda,
            'lucro_estimado': lucro,
            'margem_pct': margem_pct,
        })

    if not resultados:
        print("\nNenhum produto avaliado.")
        return

    resultados.sort(key=lambda x: x['margem_pct'], reverse=True)

    print("\n" + "=" * 70)
    print("RANKING POR MARGEM")
    print("=" * 70)
    for r in resultados:
        print(f"{r['margem_pct']:>5.1f}% margem | {r['termo']:<35} | "
              f"lucro R${r['lucro_estimado']} | venda R${r['preco_venda']} | {r['plataforma']}")

    saida = arquivo.replace('candidatos_', 'margem_')
    with open(saida, 'w', newline='', encoding='utf-8') as f:
        campos = ['termo', 'plataforma', 'custo_producao', 'preco_venda', 'lucro_estimado', 'margem_pct']
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        escritor.writerows(resultados)
    print(f"\nSalvo em {saida}")


if __name__ == '__main__':
    main()
