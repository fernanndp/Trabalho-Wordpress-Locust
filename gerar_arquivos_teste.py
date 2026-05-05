from pathlib import Path
from PIL import Image

PASTA = Path("arquivos_teste")
PASTA.mkdir(exist_ok=True)


def gerar_png_com_tamanho(caminho, tamanho_bytes, cor):
    img = Image.new("RGB", (800, 600), cor)
    img.save(caminho, "PNG")

    tamanho_atual = caminho.stat().st_size

    if tamanho_atual > tamanho_bytes:
        raise ValueError(
            f"O arquivo {caminho} ficou maior que o alvo. "
            f"Atual: {tamanho_atual}, alvo: {tamanho_bytes}"
        )

    falta = tamanho_bytes - tamanho_atual

    with open(caminho, "ab") as f:
        f.write(b"\0" * falta)

    print(f"{caminho} gerado com {caminho.stat().st_size} bytes")


def gerar_texto_400kb(caminho):
    alvo = 400 * 1024

    paragrafo = (
        "Este é um texto utilizado para teste de carga no WordPress. "
        "O objetivo é criar uma postagem com aproximadamente 400 KB de conteúdo textual, "
        "permitindo avaliar o impacto do tamanho do conteúdo HTML no tempo de resposta da aplicação. "
    )

    conteudo = ""

    while len(conteudo.encode("utf-8")) < alvo:
        conteudo += paragrafo + "\n\n"

    conteudo = conteudo.encode("utf-8")[:alvo].decode("utf-8", errors="ignore")

    caminho.write_text(conteudo, encoding="utf-8")

    print(f"{caminho} gerado com {caminho.stat().st_size} bytes")


gerar_png_com_tamanho(
    PASTA / "imagem_1mb.png",
    1024 * 1024,
    (40, 90, 160)
)

gerar_png_com_tamanho(
    PASTA / "imagem_300kb.png",
    300 * 1024,
    (160, 90, 40)
)

gerar_texto_400kb(PASTA / "texto_400kb.txt")