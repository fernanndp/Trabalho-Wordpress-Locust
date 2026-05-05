$cargas = @(
    @{ Nome = "leve"; Usuarios = 50; Spawn = 10 },
    @{ Nome = "media"; Usuarios = 150; Spawn = 30 },
    @{ Nome = "pesada"; Usuarios = 260; Spawn = 50 }
)

$cenarios = @(
    "imagem_1mb",
    "texto_400kb",
    "imagem_300kb",
    "hibrido"
)

$instancias = @(1, 2, 3)

New-Item -ItemType Directory -Force -Path ".\resultados\finais" | Out-Null

foreach ($instancia in $instancias) {

    Write-Host ""
    Write-Host "======================================================"
    Write-Host "SUBINDO AMBIENTE COM $instancia INSTANCIA(S) WORDPRESS"
    Write-Host "======================================================"

    docker compose up -d --scale wordpress=$instancia mysql wordpress nginx

    Write-Host "Aguardando WordPress estabilizar..."
    Start-Sleep -Seconds 30

    Write-Host "Reiniciando Nginx para reconhecer as instancias..."
    docker compose restart nginx

    Start-Sleep -Seconds 15

    foreach ($cenario in $cenarios) {
        foreach ($carga in $cargas) {

            $nomeCarga = $carga.Nome
            $usuarios = $carga.Usuarios
            $spawn = $carga.Spawn

            $nomeTeste = "i${instancia}_${nomeCarga}_${cenario}"
            $prefix = "/mnt/resultados/finais/$nomeTeste"

            Write-Host ""
            Write-Host "------------------------------------------------------"
            Write-Host "Teste: $nomeTeste"
            Write-Host "Instancias WordPress: $instancia"
            Write-Host "Cenario: $cenario"
            Write-Host "Carga: $nomeCarga"
            Write-Host "Usuarios: $usuarios"
            Write-Host "Spawn rate: $spawn"
            Write-Host "------------------------------------------------------"

            docker compose run --rm `
                -e CENARIO=$cenario `
                -e WP_HOST_HEADER=localhost:8080 `
                locust `
                -f locustfile.py `
                --host http://nginx `
                --headless `
                --users $usuarios `
                --spawn-rate $spawn `
                --run-time 2m `
                --csv $prefix `
                --html "${prefix}.html" `
                --only-summary

            Write-Host "Pausa entre testes..."
            Start-Sleep -Seconds 15
        }
    }
}

Write-Host ""
Write-Host "======================================================"
Write-Host "TODOS OS 36 TESTES FORAM EXECUTADOS"
Write-Host "Resultados salvos em: resultados\finais"
Write-Host "======================================================"