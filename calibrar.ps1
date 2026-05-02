$candidatos = @(10, 25, 50, 75, 100, 150, 200, 300, 400)

New-Item -ItemType Directory -Force -Path ".\resultados\calibracao" | Out-Null

Write-Host "Subindo ambiente com 1 instancia de WordPress..."
docker compose up -d --scale wordpress=1 mysql wordpress nginx

Start-Sleep -Seconds 20

Write-Host "Reiniciando nginx..."
docker compose restart nginx

Start-Sleep -Seconds 10

foreach ($u in $candidatos) {
    $spawn = [Math]::Min($u, 20)
    $prefix = "/mnt/resultados/calibracao/cal_i1_hibrido_u$u"

    Write-Host ""
    Write-Host "========================================"
    Write-Host "Calibrando com $u usuarios virtuais"
    Write-Host "Spawn rate: $spawn"
    Write-Host "Cenario: hibrido"
    Write-Host "========================================"

    docker compose run --rm -e CENARIO=hibrido locust `
        -f locustfile.py `
        --host http://nginx `
        --headless `
        --users $u `
        --spawn-rate $spawn `
        --run-time 1m `
        --csv $prefix `
        --html "${prefix}.html" `
        --only-summary
}