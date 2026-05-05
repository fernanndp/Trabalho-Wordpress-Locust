import os
import re
import glob
import pandas as pd
import matplotlib.pyplot as plt


PASTA_RESULTADOS = "resultados/finais"
PASTA_GRAFICOS = "resultados/graficos"

ORDEM_CARGAS = ["leve", "media", "pesada"]
USUARIOS_POR_CARGA = {
    "leve": 50,
    "media": 150,
    "pesada": 260,
}

NOMES_CENARIOS = {
    "imagem_1mb": "Imagem 1 MB",
    "texto_400kb": "Texto 400 KB",
    "imagem_300kb": "Imagem 300 KB",
    "hibrido": "Híbrido",
}

CENARIOS_NORMAIS = ["imagem_1mb", "texto_400kb", "imagem_300kb"]
TODOS_CENARIOS = ["imagem_1mb", "texto_400kb", "imagem_300kb", "hibrido"]


def numero(valor):
    try:
        return float(str(valor).replace(",", "."))
    except Exception:
        return 0.0


def ler_agregado(caminho):
    df = pd.read_csv(caminho)

    if "Name" in df.columns:
        linha = df[df["Name"] == "Aggregated"]
        if not linha.empty:
            return linha.iloc[0]

    return df.iloc[-1]


def extrair_metadados(nome_arquivo):
    padrao = r"i(?P<instancias>\d+)_(?P<carga>leve|media|pesada)_(?P<cenario>.+)_stats\.csv"
    match = re.match(padrao, nome_arquivo)

    if not match:
        return None

    return {
        "instancias": int(match.group("instancias")),
        "carga": match.group("carga"),
        "cenario": match.group("cenario"),
    }


def consolidar_resultados():
    arquivos = glob.glob(os.path.join(PASTA_RESULTADOS, "*_stats.csv"))
    registros = []

    for caminho in arquivos:
        nome = os.path.basename(caminho)
        meta = extrair_metadados(nome)

        if meta is None:
            print(f"Ignorando arquivo com nome fora do padrão: {nome}")
            continue

        linha = ler_agregado(caminho)

        reqs = numero(linha.get("Request Count", 0))
        falhas = numero(linha.get("Failure Count", 0))
        taxa_falha = (falhas / reqs * 100) if reqs > 0 else 0

        registros.append({
            "arquivo": nome,
            "cenario": meta["cenario"],
            "cenario_nome": NOMES_CENARIOS.get(meta["cenario"], meta["cenario"]),
            "instancias": meta["instancias"],
            "carga": meta["carga"],
            "usuarios": USUARIOS_POR_CARGA[meta["carga"]],
            "request_count": reqs,
            "failure_count": falhas,
            "taxa_falha_%": taxa_falha,
            "tempo_medio_ms": numero(linha.get("Average Response Time", 0)),
            "tempo_mediano_ms": numero(linha.get("Median Response Time", 0)),
            "p95_ms": numero(linha.get("95%", 0)),
            "min_ms": numero(linha.get("Min Response Time", 0)),
            "max_ms": numero(linha.get("Max Response Time", 0)),
            "rps": numero(linha.get("Requests/s", 0)),
            "failures_s": numero(linha.get("Failures/s", 0)),
        })

    df = pd.DataFrame(registros)

    if df.empty:
        raise RuntimeError("Nenhum resultado foi consolidado. Verifique a pasta resultados/finais.")

    df["ordem_carga"] = df["carga"].map({c: i for i, c in enumerate(ORDEM_CARGAS)})

    df = df.sort_values(
        by=["cenario", "instancias", "ordem_carga"]
    ).reset_index(drop=True)

    os.makedirs(PASTA_GRAFICOS, exist_ok=True)

    saida_csv = os.path.join("resultados", "resumo_resultados.csv")
    saida_excel = os.path.join("resultados", "resumo_resultados.xlsx")

    df.to_csv(saida_csv, index=False, encoding="utf-8-sig")
    df.to_excel(saida_excel, index=False)

    print(f"Resumo CSV salvo em: {saida_csv}")
    print(f"Resumo Excel salvo em: {saida_excel}")
    print(f"Total de testes consolidados: {len(df)}")

    return df


def salvar_grafico(nome):
    caminho = os.path.join(PASTA_GRAFICOS, nome)
    plt.tight_layout()
    plt.savefig(caminho, dpi=200)
    plt.close()
    print(f"Gráfico salvo: {caminho}")


def grafico_por_usuarios(df, cenario, metrica, titulo_metrica, eixo_y, nome_arquivo):
    dados = df[df["cenario"] == cenario].copy()

    plt.figure(figsize=(9, 5))

    for instancia in sorted(dados["instancias"].unique()):
        temp = dados[dados["instancias"] == instancia].sort_values("usuarios")

        plt.plot(
            temp["usuarios"],
            temp[metrica],
            marker="o",
            label=f"{instancia} instância(s)"
        )

    plt.title(f"{titulo_metrica} por usuários — {NOMES_CENARIOS[cenario]}")
    plt.xlabel("Número de usuários")
    plt.ylabel(eixo_y)
    plt.xticks([50, 200, 520])
    plt.grid(True, alpha=0.3)
    plt.legend()
    salvar_grafico(nome_arquivo)


def grafico_por_instancias(df, cenario, metrica, titulo_metrica, eixo_y, nome_arquivo):
    dados = df[df["cenario"] == cenario].copy()

    plt.figure(figsize=(9, 5))

    for carga in ORDEM_CARGAS:
        temp = dados[dados["carga"] == carga].sort_values("instancias")
        usuarios = USUARIOS_POR_CARGA[carga]

        plt.plot(
            temp["instancias"],
            temp[metrica],
            marker="o",
            label=f"{carga} ({usuarios} usuários)"
        )

    plt.title(f"{titulo_metrica} por instâncias — {NOMES_CENARIOS[cenario]}")
    plt.xlabel("Número de instâncias do WordPress")
    plt.ylabel(eixo_y)
    plt.xticks([1, 2, 3])
    plt.grid(True, alpha=0.3)
    plt.legend()
    salvar_grafico(nome_arquivo)


def gerar_14_graficos(df):
    contador = 1

    # 8 gráficos:
    # Para os 4 cenários: tempo médio e P95 por número de usuários.
    for cenario in TODOS_CENARIOS:
        grafico_por_usuarios(
            df,
            cenario,
            "tempo_medio_ms",
            "Tempo médio de resposta",
            "Tempo médio de resposta (ms)",
            f"{contador:02d}_tempo_medio_por_usuarios_{cenario}.png"
        )
        contador += 1

        grafico_por_usuarios(
            df,
            cenario,
            "p95_ms",
            "P95 do tempo de resposta",
            "P95 (ms)",
            f"{contador:02d}_p95_por_usuarios_{cenario}.png"
        )
        contador += 1

    # 6 gráficos:
    # Para os 3 cenários normais: tempo médio e P95 por número de instâncias.
    for cenario in CENARIOS_NORMAIS:
        grafico_por_instancias(
            df,
            cenario,
            "tempo_medio_ms",
            "Tempo médio de resposta",
            "Tempo médio de resposta (ms)",
            f"{contador:02d}_tempo_medio_por_instancias_{cenario}.png"
        )
        contador += 1

        grafico_por_instancias(
            df,
            cenario,
            "p95_ms",
            "P95 do tempo de resposta",
            "P95 (ms)",
            f"{contador:02d}_p95_por_instancias_{cenario}.png"
        )
        contador += 1

    print(f"\nTotal de gráficos gerados: {contador - 1}")


def validar_resultados(df):
    print("\nVALIDAÇÃO DOS TESTES")
    print("-" * 80)

    total = len(df)
    print(f"Total de testes encontrados: {total}")

    if total == 36:
        print("OK: Foram encontrados os 36 testes esperados.")
    else:
        print("ATENÇÃO: O total esperado era 36. Verifique se algum teste faltou.")

    print("\nFalhas por teste:")
    colunas = [
        "cenario_nome",
        "instancias",
        "carga",
        "usuarios",
        "request_count",
        "failure_count",
        "taxa_falha_%",
        "tempo_medio_ms",
        "p95_ms",
        "rps",
    ]

    print(df[colunas].to_string(index=False))

    problemas_leve_media = df[
        (df["carga"].isin(["leve", "media"])) &
        (df["taxa_falha_%"] > 0)
    ]

    problemas_pesada = df[
        (df["carga"] == "pesada") &
        (df["taxa_falha_%"] > 10)
    ]

    print("\nCHECAGEM DAS REGRAS")
    print("-" * 80)

    if problemas_leve_media.empty:
        print("OK: cargas leve e média ficaram com 0% de falha.")
    else:
        print("ATENÇÃO: alguns testes leves/médios tiveram falha:")
        print(problemas_leve_media[colunas].to_string(index=False))

    if problemas_pesada.empty:
        print("OK: carga pesada ficou dentro do limite de até 10% de falha.")
    else:
        print("ATENÇÃO: alguns testes pesados passaram de 10% de falha:")
        print(problemas_pesada[colunas].to_string(index=False))


def main():
    df = consolidar_resultados()
    validar_resultados(df)
    gerar_14_graficos(df)

    print("\nArquivos principais gerados:")
    print("1. resultados/resumo_resultados.csv")
    print("2. resultados/resumo_resultados.xlsx")
    print("3. resultados/graficos/*.png")


if __name__ == "__main__":
    main()