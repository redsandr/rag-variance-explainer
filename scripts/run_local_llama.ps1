$ErrorActionPreference = 'Stop'

$docker = (Get-Command docker -ErrorAction SilentlyContinue).Source
if (-not $docker) {
    $docker = 'C:\Program Files\Docker\Docker\resources\bin\docker.exe'
}
if (-not (Test-Path -LiteralPath $docker)) {
    throw 'Docker CLI not found. Start Docker Desktop and install its CLI first.'
}
$env:PATH = "$(Split-Path -Parent $docker);$env:PATH"

$modelDirectory = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..\models')).Path
$model = Join-Path $modelDirectory 'qwen2.5-7b-instruct-q4_k_m.gguf'
if (-not (Test-Path -LiteralPath $model)) {
    throw "GGUF model not found: $model"
}

& $docker run --rm -d --name rve-llama --gpus all `
    --mount "type=bind,source=$modelDirectory,target=/models,readonly" `
    -p 127.0.0.1:8080:8080 `
    ghcr.io/ggml-org/llama.cpp:server-cuda `
    -m /models/qwen2.5-7b-instruct-q4_k_m.gguf `
    --alias rve-local --n-gpu-layers 10 --ctx-size 8192 `
    --batch-size 32 --parallel 1 --host 0.0.0.0 --port 8080

if ($LASTEXITCODE -ne 0) {
    throw 'llama-server container failed to start. Check Docker Desktop and its error output.'
}

Write-Output 'Container started. Check: docker logs rve-llama; then http://127.0.0.1:8080/v1/models'
