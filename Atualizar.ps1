param([string]$Repositorio)
$ErrorActionPreference = 'Stop'
try {
    $savedRepo = Join-Path $PSScriptRoot 'repository.txt'
    if (!$Repositorio -and (Test-Path -LiteralPath $savedRepo)) {
        $Repositorio = (Get-Content -LiteralPath $savedRepo -Raw).Trim()
    }
    if (!$Repositorio) { $Repositorio = Read-Host 'Repositorio GitHub (usuario/repositorio)' }
    $Repositorio = $Repositorio -replace '^https://github.com/', '' -replace '\.git$', ''
    if ($Repositorio -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') { throw 'Repositorio invalido.' }
    $headers = @{ 'User-Agent' = 'Slayers2Macro-Updater'; 'Accept' = 'application/vnd.github+json' }
    # Repositórios privados exigem gh autenticado. O token nunca é salvo ou exibido.
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $token = & gh auth token 2>$null
        if ($LASTEXITCODE -eq 0 -and $token) { $headers.Authorization = "Bearer $token" }
    }
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repositorio/releases/latest" -Headers $headers
    $asset = @($release.assets | Where-Object name -EQ 'Slayers2Macro.zip')
    $checksum = @($release.assets | Where-Object name -EQ 'Slayers2Macro.zip.sha256')
    if ($asset.Count -ne 1 -or $checksum.Count -ne 1) { throw 'A versao publicada nao possui os arquivos esperados.' }
    $install = Join-Path $PSScriptRoot '.install'
    New-Item -ItemType Directory -Path $install -Force | Out-Null
    $releaseDir = Join-Path $install ([string]$release.id)
    $exe = Join-Path $releaseDir 'Slayers2Macro.exe'
    if (!(Test-Path -LiteralPath $exe)) {
        $stage = Join-Path $install ('staging-' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $stage | Out-Null
        $zip = Join-Path $stage 'release.zip'
        $hashFile = Join-Path $stage 'release.sha256'
        $downloadHeaders = $headers.Clone(); $downloadHeaders.Accept = 'application/octet-stream'
        Invoke-WebRequest -UseBasicParsing -Uri $asset[0].url -Headers $downloadHeaders -OutFile $zip
        Invoke-WebRequest -UseBasicParsing -Uri $checksum[0].url -Headers $downloadHeaders -OutFile $hashFile
        $expected = (Get-Content -LiteralPath $hashFile -Raw).Trim()
        if ($expected -notmatch '^[a-fA-F0-9]{64}$' -or (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash -ne $expected) {
            throw 'Download incompleto ou checksum incorreto. A instalacao anterior foi preservada.'
        }
        Add-Type -AssemblyName System.IO.Compression.FileSystem
        $archive = [IO.Compression.ZipFile]::OpenRead($zip)
        try {
            $root = [IO.Path]::GetFullPath($releaseDir) + [IO.Path]::DirectorySeparatorChar
            foreach ($entry in $archive.Entries) {
                $target = [IO.Path]::GetFullPath((Join-Path $releaseDir $entry.FullName))
                if (!$target.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) { throw 'Caminho invalido no ZIP.' }
            }
        } finally { $archive.Dispose() }
        Expand-Archive -LiteralPath $zip -DestinationPath $releaseDir
        if (!(Test-Path -LiteralPath $exe)) { throw 'Executavel ausente na versao baixada.' }
        # Recupera dados apenas da instalação anterior deste mesmo atualizador.
        $stateFile = Join-Path $install 'current.txt'
        if (Test-Path -LiteralPath $stateFile) {
            $previousId = (Get-Content -LiteralPath $stateFile -Raw).Trim()
            if ($previousId -match '^\d+$') {
                $previous = Join-Path $install $previousId
                foreach ($name in @('config.json','historico')) {
                    $dataPath = Join-Path $previous $name
                    if (Test-Path -LiteralPath $dataPath) { Copy-Item -LiteralPath $dataPath -Destination $releaseDir -Recurse }
                }
            }
        }
    }
    Set-Content -LiteralPath $savedRepo -Value $Repositorio -Encoding ASCII
    Set-Content -LiteralPath (Join-Path $install 'current.txt') -Value ([string]$release.id) -Encoding ASCII
    Write-Host "Versao pronta: $($release.tag_name). Feche o macro anterior antes de abrir esta versao."
    if ((Read-Host 'Abrir agora? (S/N)') -match '^[sS]$') { Start-Process -FilePath $exe -WindowStyle Hidden }
} catch {
    Write-Host ('Nao foi possivel atualizar: ' + $_.Exception.Message)
    Write-Host 'Confirme o repositorio e se existe uma Release. Para repositorio privado, autentique gh auth login.'
    exit 1
}
