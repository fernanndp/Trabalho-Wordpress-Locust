import os
from locust import HttpUser, task, between


CENARIO = os.getenv("CENARIO", "hibrido").lower()

POSTS = {
    "imagem_1mb": "/post-de-imagem-com-1mb/",
    "texto_400kb": "/post-texto-400kb/",
    "imagem_300kb": "/post-imagem-300kb/",
}

IMAGENS = {
    "imagem_1mb": "/wp-content/uploads/2026/05/imagem_1mb.png",
    "imagem_300kb": "/wp-content/uploads/2026/05/imagem_300kb.png",
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
                response.failure(f"HTTP {response.status_code}. Location: {location}")

    def acessar_imagem_1mb(self):
        self.get_ok(POSTS["imagem_1mb"], "imagem_1mb_01_post")
        self.get_ok(IMAGENS["imagem_1mb"], "imagem_1mb_02_arquivo")

    def acessar_texto_400kb(self):
        self.get_ok(POSTS["texto_400kb"], "texto_400kb_01_post")

    def acessar_imagem_300kb(self):
        self.get_ok(POSTS["imagem_300kb"], "imagem_300kb_01_post")
        self.get_ok(IMAGENS["imagem_300kb"], "imagem_300kb_02_arquivo")

    def acessar_hibrido(self):
        self.get_ok(POSTS["imagem_1mb"], "hibrido_01_post_imagem_1mb")
        self.get_ok(IMAGENS["imagem_1mb"], "hibrido_02_arquivo_1mb")

        self.get_ok(POSTS["texto_400kb"], "hibrido_03_texto_400kb")

        self.get_ok(POSTS["imagem_300kb"], "hibrido_04_post_imagem_300kb")
        self.get_ok(IMAGENS["imagem_300kb"], "hibrido_05_arquivo_300kb")

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