import csv
import glob
import os
import re


def numero(valor):
    try:
        return float(str(valor).replace(",", "."))
    except:
        return 0.0


def extrair_usuarios(caminho):
    nome = os.path.basename(caminho)
    match = re.search(r"_u(\d+)_stats\.csv", nome)
    if match:
        return int(match.group(1))
    return 0


arquivos = sorted(
    glob.glob("resultados/calibracao/*_stats.csv"),
    key=extrair_usuarios
)

if not arquivos:
    print("Nenhum arquivo de calibracao encontrado.")
    print("Verifique se os CSVs estao em resultados/calibracao.")
    raise SystemExit


print("\nRESULTADO DA CALIBRACAO")
print("-" * 95)
print(f"{'Usuarios':>10} | {'Reqs':>8} | {'Falhas':>8} | {'% Falha':>8} | {'Tempo medio ms':>15} | {'RPS':>10}")
print("-" * 95)

for caminho in arquivos:
    usuarios = extrair_usuarios(caminho)

    with open(caminho, "r", encoding="utf-8") as f:
        linhas = list(csv.DictReader(f))

    agregado = None

    for linha in linhas:
        if linha.get("Name") == "Aggregated":
            agregado = linha
            break

    if agregado is None:
        agregado = linhas[-1]

    reqs = numero(agregado.get("Request Count", 0))
    falhas = numero(agregado.get("Failure Count", 0))
    tempo_medio = numero(agregado.get("Average Response Time", 0))
    rps = numero(agregado.get("Requests/s", 0))

    taxa_falha = (falhas / reqs * 100) if reqs > 0 else 0

    print(
        f"{usuarios:>10} | "
        f"{int(reqs):>8} | "
        f"{int(falhas):>8} | "
        f"{taxa_falha:>7.2f}% | "
        f"{tempo_medio:>15.2f} | "
        f"{rps:>10.2f}"
    )

print("-" * 95)

print("\nComo escolher:")
print("Carga leve  = um valor baixo/intermediario com 0% de falha.")
print("Carga media = um valor maior que a leve, ainda com 0% de falha.")
print("Carga pesada = maior valor possivel com ate 10% de falha.")