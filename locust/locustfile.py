import os
from locust import HttpUser, task, between


# Cenários disponíveis:
# imagem_1mb
# texto_400kb
# imagem_300kb
# hibrido

CENARIO = os.getenv("CENARIO", "hibrido").lower()

ROTAS = {
    "imagem_1mb": "/post-de-imagem-com-1mb/",
    "texto_400kb": "/post-texto-400kb/",
    "imagem_300kb": "/post-imagem-300kb/",
}

# Importante:
# O Locust acessa o Nginx pelo host interno "http://nginx",
# mas informa ao WordPress que o host público é localhost:8080.
# Isso evita redirecionamento para localhost dentro do container do Locust.
WP_HEADERS = {
    "Host": os.getenv("WP_HOST_HEADER", "localhost:8080")
}


class WordpressUser(HttpUser):
    wait_time = between(1, 3)

    def get_wordpress(self, rota, nome):
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
        self.get_wordpress(
            ROTAS["imagem_1mb"],
            "normal_imagem_1mb"
        )

    def acessar_texto_400kb(self):
        self.get_wordpress(
            ROTAS["texto_400kb"],
            "normal_texto_400kb"
        )

    def acessar_imagem_300kb(self):
        self.get_wordpress(
            ROTAS["imagem_300kb"],
            "normal_imagem_300kb"
        )

    def acessar_hibrido(self):
        self.get_wordpress(
            ROTAS["imagem_1mb"],
            "hibrido_01_imagem_1mb"
        )

        self.get_wordpress(
            ROTAS["texto_400kb"],
            "hibrido_02_texto_400kb"
        )

        self.get_wordpress(
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