# Trabalho 3 — Testes de Carga com Locust, WordPress e Nginx

Este projeto realiza testes de carga em uma aplicação WordPress utilizando **Locust** como gerador de carga e **Nginx** como balanceador entre múltiplas instâncias do WordPress.

O objetivo é avaliar o comportamento da aplicação variando:

- quantidade de usuários virtuais;
- quantidade de instâncias do WordPress;
- tipo de conteúdo acessado;
- tempo médio de resposta;
- P95;
- taxa de erro.

---

## Arquitetura

```text
Locust → Nginx → WordPress → MySQL
```

| Serviço | Função |
|---|---|
| Locust | Gera carga de usuários virtuais |
| Nginx | Balanceia as requisições entre as instâncias do WordPress |
| WordPress | Aplicação web testada |
| MySQL | Banco de dados utilizado pelo WordPress |

---

## Estrutura do Projeto

```text
TRABALHO3-LOCUSTWORDPRESS/
│
├── arquivos_teste/
│   ├── gerar_arquivos_teste.py
│   ├── imagem_1mb.png
│   ├── imagem_300kb.png
│   └── texto_400kb.txt
│
├── locust/
│   └── locustfile.py
│
├── resultados/
│   ├── finais/
│   ├── graficos/
│   ├── resumo_resultados.csv
│   └── resumo_resultados.xlsx
│
├── scripts/
│   ├── execucao/
│   │   └── testes.ps1
│   │
│   └── graficos/
│       └── gerar_graficos.py
│
├── .gitignore
├── docker-compose.yml
├── nginx.conf
└── README.md
```

---

## Descrição das Pastas

### `arquivos_teste/`

Contém os arquivos utilizados nos cenários de teste.

| Arquivo | Descrição |
|---|---|
| `imagem_1mb.png` | Imagem com aproximadamente 1 MB |
| `imagem_300kb.png` | Imagem com aproximadamente 300 KB |
| `texto_400kb.txt` | Texto com aproximadamente 400 KB |
| `gerar_arquivos_teste.py` | Script usado para gerar os arquivos de teste |

---

### `locust/`

Contém o arquivo principal do Locust:

```text
locust/locustfile.py
```

Esse arquivo define os cenários executados pelos usuários virtuais.

---

### `scripts/execucao/`

Contém o script responsável por executar os testes finais.

| Arquivo | Descrição |
|---|---|
| `testes.ps1` | Executa os 36 testes finais combinando cenários, cargas e instâncias |

---

### `scripts/graficos/`

Contém o script responsável por consolidar os resultados e gerar os gráficos.

| Arquivo | Descrição |
|---|---|
| `gerar_graficos.py` | Gera a tabela consolidada e os gráficos finais |

---

### `resultados/`

Contém os arquivos gerados após a execução dos testes.

```text
resultados/
├── finais/
├── graficos/
├── resumo_resultados.csv
└── resumo_resultados.xlsx
```

---

## Cenários de Teste

| Cenário | Descrição |
|---|---|
| `imagem_1mb` | GET direto no arquivo de imagem com aproximadamente 1 MB |
| `texto_400kb` | GET no post do WordPress com aproximadamente 400 KB de texto |
| `imagem_300kb` | GET direto no arquivo de imagem com aproximadamente 300 KB |
| `hibrido` | Executa os três acessos no mesmo fluxo: imagem 1 MB, texto 400 KB e imagem 300 KB |

No cenário híbrido, cada usuário virtual executa:

```text
GET imagem 1 MB
GET texto 400 KB
GET imagem 300 KB
```

Esse cenário representa o caso mais exigente, pois combina os três tipos de conteúdo em um mesmo fluxo.

---

## Cargas Utilizadas

Foram adotadas três cargas proporcionais:

| Carga | Usuários virtuais | Critério |
|---|---:|---|
| Leve | 100 | Deve executar sem falhas |
| Média | 200 | Deve executar sem falhas |
| Pesada | 290 | Deve gerar estresse real, mas sem ultrapassar 10% de erro |

A carga pesada foi definida como **290 usuários virtuais**, pois apresentou falha real durante a calibração, indicando estresse da aplicação, mas permaneceu abaixo do limite máximo de **10% de erro**.

A carga de **295 usuários** foi descartada por ultrapassar o limite de 10% de falha.

---

## Matriz de Testes

Os testes finais combinam:

| Variável | Valores |
|---|---|
| Cenários | `imagem_1mb`, `texto_400kb`, `imagem_300kb`, `hibrido` |
| Cargas | leve, média e pesada |
| Usuários por carga | 100, 200 e 290 |
| Instâncias WordPress | 1, 2 e 3 |

Total:

```text
4 cenários × 3 cargas × 3 instâncias = 36 testes
```

---

## Nomenclatura dos Resultados Brutos

Os resultados brutos dos testes finais ficam em:

```text
resultados/finais/
```

Cada teste segue o padrão:

```text
i{instancias}_{carga}_{cenario}_stats.csv
i{instancias}_{carga}_{cenario}.html
```

Exemplos:

```text
i1_leve_imagem_1mb_stats.csv
i1_media_texto_400kb_stats.csv
i2_pesada_hibrido_stats.csv
i3_pesada_imagem_300kb_stats.csv
```

Significado:

| Parte do nome | Significado |
|---|---|
| `i1`, `i2`, `i3` | Quantidade de instâncias do WordPress |
| `leve`, `media`, `pesada` | Tipo de carga aplicada |
| `imagem_1mb` | Cenário da imagem de aproximadamente 1 MB |
| `texto_400kb` | Cenário do texto de aproximadamente 400 KB |
| `imagem_300kb` | Cenário da imagem de aproximadamente 300 KB |
| `hibrido` | Cenário com os três acessos no mesmo fluxo |
| `_stats.csv` | Arquivo principal com as métricas do Locust |
| `.html` | Relatório visual individual gerado pelo Locust |

Exemplo:

```text
i3_pesada_hibrido_stats.csv
```

Representa:

```text
3 instâncias do WordPress
carga pesada
cenário híbrido
arquivo CSV com métricas principais
```

---

## Tabela Consolidada

A tabela consolidada fica em:

```text
resultados/resumo_resultados.csv
resultados/resumo_resultados.xlsx
```

Ela reúne os 36 testes finais em uma única base.

Principais colunas:

| Coluna | Significado |
|---|---|
| `arquivo` | Nome do arquivo bruto de origem |
| `cenario` | Nome técnico do cenário |
| `cenario_nome` | Nome amigável do cenário |
| `instancias` | Quantidade de instâncias do WordPress |
| `carga` | Tipo de carga: leve, média ou pesada |
| `usuarios` | Quantidade de usuários virtuais |
| `request_count` | Total de requisições |
| `failure_count` | Total de falhas |
| `taxa_falha_%` | Taxa de erro em porcentagem |
| `tempo_medio_ms` | Tempo médio de resposta em milissegundos |
| `p95_ms` | Percentil 95 do tempo de resposta |
| `rps` | Requisições por segundo |

A taxa de erro é calculada por:

```text
taxa de erro = falhas / requisições × 100
```

---

## Gráficos Gerados

Os gráficos finais ficam em:

```text
resultados/graficos/
```

Foram gerados gráficos para três métricas principais:

| Métrica | Descrição |
|---|---|
| Tempo médio | Média do tempo de resposta das requisições |
| P95 | Tempo abaixo do qual 95% das requisições foram respondidas |
| Taxa de erro | Percentual de falhas em relação ao total de requisições |

Não são gerados gráficos de RPS. O RPS permanece apenas na tabela consolidada como métrica auxiliar.

---

## Nomenclatura dos Gráficos

Os gráficos seguem o padrão:

```text
{numero}_{metrica}_por_{variavel}_{cenario}.png
```

Exemplos:

```text
01_tempo_medio_por_usuarios_imagem_1mb.png
02_p95_por_usuarios_imagem_1mb.png
03_taxa_erro_por_usuarios_imagem_1mb.png
```

Significado:

| Parte do nome | Significado |
|---|---|
| `01`, `02`, `03` | Ordem do gráfico |
| `tempo_medio` | Gráfico de tempo médio de resposta |
| `p95` | Gráfico do percentil 95 |
| `taxa_erro` | Gráfico da taxa de erro |
| `por_usuarios` | Comparação por quantidade de usuários |
| `por_instancias` | Comparação por quantidade de instâncias |
| `imagem_1mb`, `texto_400kb`, `imagem_300kb`, `hibrido` | Cenário analisado |

---

## Gráficos por Número de Usuários

Esses gráficos mostram como cada cenário se comporta quando a quantidade de usuários aumenta.

Arquivos esperados:

```text
01_tempo_medio_por_usuarios_imagem_1mb.png
02_p95_por_usuarios_imagem_1mb.png
03_taxa_erro_por_usuarios_imagem_1mb.png

04_tempo_medio_por_usuarios_texto_400kb.png
05_p95_por_usuarios_texto_400kb.png
06_taxa_erro_por_usuarios_texto_400kb.png

07_tempo_medio_por_usuarios_imagem_300kb.png
08_p95_por_usuarios_imagem_300kb.png
09_taxa_erro_por_usuarios_imagem_300kb.png

10_tempo_medio_por_usuarios_hibrido.png
11_p95_por_usuarios_hibrido.png
12_taxa_erro_por_usuarios_hibrido.png
```

Esses gráficos comparam:

```text
leve = 100 usuários
média = 200 usuários
pesada = 290 usuários
```

---

## Gráficos por Número de Instâncias

Esses gráficos mostram como cada cenário se comporta quando a quantidade de instâncias do WordPress varia.

Arquivos esperados:

```text
13_tempo_medio_por_instancias_imagem_1mb.png
14_p95_por_instancias_imagem_1mb.png
15_taxa_erro_por_instancias_imagem_1mb.png

16_tempo_medio_por_instancias_texto_400kb.png
17_p95_por_instancias_texto_400kb.png
18_taxa_erro_por_instancias_texto_400kb.png

19_tempo_medio_por_instancias_imagem_300kb.png
20_p95_por_instancias_imagem_300kb.png
21_taxa_erro_por_instancias_imagem_300kb.png
```

Esses gráficos comparam:

```text
1 instância do WordPress
2 instâncias do WordPress
3 instâncias do WordPress
```

---

## Quantidade Total de Gráficos

O total esperado é:

```text
4 cenários × 3 métricas por usuários = 12 gráficos
3 cenários individuais × 3 métricas por instâncias = 9 gráficos

Total = 21 gráficos
```

Os gráficos por instâncias são gerados apenas para os cenários individuais:

```text
imagem_1mb
texto_400kb
imagem_300kb
```

O cenário híbrido é analisado nos gráficos por usuários, pois ele já combina os três acessos em um mesmo fluxo.

---

## Autora

Trabalho desenvolvido para a disciplina de Computação Distribuída, com foco na realização de testes de carga em múltiplas instâncias do WordPress utilizando Locust e Nginx.