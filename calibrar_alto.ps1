$candidatos = @(510, 520, 530, 540)

New-Item -ItemType Directory -Force -Path ".\resultados\calibracao" | Out-Null

Write-Host "Garantindo ambiente com 1 instancia de WordPress..."
docker compose up -d --scale wordpress=1 mysql wordpress nginx

Start-Sleep -Seconds 20

Write-Host "Reiniciando nginx..."
docker compose restart nginx
Start-Sleep -Seconds 10

foreach ($u in $candidatos) {
    $spawn = [Math]::Min($u, 50)
    $prefix = "/mnt/resultados/calibracao/cal_i1_hibrido_u$u"

    Write-Host ""
    Write-Host "========================================"
    Write-Host "Calibrando carga alta com $u usuarios virtuais"
    Write-Host "Instancias WordPress: 1"
    Write-Host "Cenario: hibrido"
    Write-Host "Spawn rate: $spawn"
    Write-Host "========================================"

    docker compose run --rm -e CENARIO=hibrido -e WP_HOST_HEADER=localhost:8080 locust `
        -f locustfile.py `
        --host http://nginx `
        --headless `
        --users $u `
        --spawn-rate $spawn `
        --run-time 1m `
        --csv $prefix `
        --html "${prefix}.html" `
        --only-summary

    Write-Host "Pausa entre testes..."
    Start-Sleep -Seconds 15
}