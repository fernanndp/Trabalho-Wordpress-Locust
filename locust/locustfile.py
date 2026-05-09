import os
from locust import HttpUser, task, between


CENARIO = os.getenv("CENARIO", "hibrido").lower()

# URLs testadas:
# - imagem_1mb: GET direto no arquivo de imagem de aproximadamente 1 MB
# - texto_400kb: GET no post com aproximadamente 400 KB de texto
# - imagem_300kb: GET direto no arquivo de imagem de aproximadamente 300 KB

ROTAS = {
    "imagem_1mb": os.getenv(
        "URL_IMAGEM_1MB",
        "/wp-content/uploads/2026/05/imagem_1mb.png"
    ),
    "texto_400kb": os.getenv(
        "URL_TEXTO_400KB",
        "/post-texto-400kb/"
    ),
    "imagem_300kb": os.getenv(
        "URL_IMAGEM_300KB",
        "/wp-content/uploads/2026/05/imagem_300kb.png"
    ),
}

WP_HEADERS = {
    "Host": os.getenv("WP_HOST_HEADER", "localhost:8080")
}


class WordpressUser(HttpUser):
    wait_time = between(1, 3)

    def get_ok(self, rota, nome):
        with self.client.get(
            rota,
            name=nome,
            headers=WP_HEADERS,
            allow_redirects=False,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                location = response.headers.get("Location", "")
                response.failure(
                    f"HTTP {response.status_code}. Location: {location}"
                )

    def acessar_imagem_1mb(self):
        self.get_ok(
            ROTAS["imagem_1mb"],
            "imagem_1mb"
        )

    def acessar_texto_400kb(self):
        self.get_ok(
            ROTAS["texto_400kb"],
            "texto_400kb"
        )

    def acessar_imagem_300kb(self):
        self.get_ok(
            ROTAS["imagem_300kb"],
            "imagem_300kb"
        )

    def acessar_hibrido(self):
        self.get_ok(
            ROTAS["imagem_1mb"],
            "hibrido_01_imagem_1mb"
        )

        self.get_ok(
            ROTAS["texto_400kb"],
            "hibrido_02_texto_400kb"
        )

        self.get_ok(
            ROTAS["imagem_300kb"],
            "hibrido_03_imagem_300kb"
        )

    @task
    def executar_cenario(self):
        if CENARIO == "imagem_1mb":
            self.acessar_imagem_1mb()

        elif CENARIO == "texto_400kb":
            self.acessar_texto_400kb()

        elif CENARIO == "imagem_300kb":
            self.acessar_imagem_300kb()

        elif CENARIO == "hibrido":
            self.acessar_hibrido()

        else:
            self.acessar_hibrido()