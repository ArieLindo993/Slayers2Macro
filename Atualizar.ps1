param([string]$Repositorio, [switch]$NaoAbrir, [switch]$Voltar, [switch]$Iniciar)
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
function Get-InstalledExe([string]$Id, [string]$Base) {
    if ($Id -notmatch '^\d+$') { throw 'Identificador de versao invalido.' }
    $candidate = Join-Path (Join-Path $Base $Id) 'Slayers2Macro.exe'
    if (!(Test-Path -LiteralPath $candidate)) { throw 'Esta versao nao esta instalada.' }
    return $candidate
}
try {
    Write-Host 'Preparando o atualizador...'
    $install = Join-Path $PSScriptRoot '.install'
    $stateFile = Join-Path $install 'current.txt'
    $previousFile = Join-Path $install 'previous.txt'
    $sharedData = Join-Path $env:LOCALAPPDATA 'FishingMacro'
    if (Get-Process -Name Slayers2Macro -ErrorAction SilentlyContinue) { throw 'Feche o macro antes de iniciar, atualizar ou voltar de versao.' }
    if (Test-Path -LiteralPath $stateFile) {
        $installedId = (Get-Content -LiteralPath $stateFile -Raw).Trim()
        if ($installedId -match '^\d+$') {
            $oldHistory = Join-Path (Join-Path $install $installedId) 'historico'
            if (Test-Path -LiteralPath $oldHistory) {
                $sharedHistory = Join-Path $sharedData 'historico'
                New-Item -ItemType Directory -Path $sharedHistory -Force | Out-Null
                foreach ($record in (Get-ChildItem -LiteralPath $oldHistory -File)) {
                    $dest = Join-Path $sharedHistory $record.Name
                    if ($record.Extension -in @('.json','.csv') -and (!(Test-Path -LiteralPath $dest) -or $record.LastWriteTimeUtc -gt (Get-Item -LiteralPath $dest).LastWriteTimeUtc)) {
                        Copy-Item -LiteralPath $record.FullName -Destination $dest -Force
                    }
                }
            }
        }
    }
    if ($Voltar -or $Iniciar) {
        if (!(Test-Path -LiteralPath $stateFile)) { throw 'Instale uma versao com Atualizar.cmd primeiro.' }
        $currentId = (Get-Content -LiteralPath $stateFile -Raw).Trim()
        $exe = Get-InstalledExe $currentId $install
        if ($Voltar) {
            if (!(Test-Path -LiteralPath $previousFile)) { throw 'Ainda nao existe uma versao anterior instalada.' }
            $previousId = (Get-Content -LiteralPath $previousFile -Raw).Trim()
            $exe = Get-InstalledExe $previousId $install
            # Compatibilidade com versões antigas que liam os dados junto do exe.
            foreach ($name in @('config.json','historico')) {
                $dataPath = Join-Path $sharedData $name
                if (Test-Path -LiteralPath $dataPath) {
                    $dest = Join-Path (Split-Path $exe) $name
                    if (Test-Path -LiteralPath $dataPath -PathType Container) {
                        New-Item -ItemType Directory -Path $dest -Force | Out-Null
                        Get-ChildItem -LiteralPath $dataPath -File | Copy-Item -Destination $dest -Force
                    } else { Copy-Item -LiteralPath $dataPath -Destination $dest -Force }
                }
            }
            Set-Content -LiteralPath $previousFile -Value $currentId -Encoding ASCII
            Set-Content -LiteralPath $stateFile -Value $previousId -Encoding ASCII
            Write-Host 'Versao anterior restaurada. Dados locais preservados. Use Iniciar.cmd para abri-la.'
        }
        if (!$NaoAbrir) { Start-Process -FilePath $exe -WindowStyle Hidden }
        exit 0
    }
    $savedRepo = Join-Path $PSScriptRoot 'repository.txt'
    if (!$Repositorio -and (Test-Path -LiteralPath $savedRepo)) {
        $Repositorio = (Get-Content -LiteralPath $savedRepo -Raw).Trim()
    }
    if (!$Repositorio) { $Repositorio = 'ArieLindo993/Slayers2Macro' }
    $Repositorio = $Repositorio -replace '^https://github.com/', '' -replace '\.git$', ''
    if ($Repositorio -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') { throw 'Repositorio invalido.' }
    $headers = @{ 'User-Agent' = 'Slayers2Macro-Updater'; 'Accept' = 'application/vnd.github+json' }
    # Repositórios privados exigem gh autenticado. O token nunca é salvo ou exibido.
    if (Get-Command gh -ErrorAction SilentlyContinue) {
        $token = & gh auth token 2>$null
        if ($LASTEXITCODE -eq 0 -and $token) { $headers.Authorization = "Bearer $token" }
    }
    Write-Host 'Consultando a versao mais recente no GitHub...'
    $release = Invoke-RestMethod -Uri "https://api.github.com/repos/$Repositorio/releases/latest" -Headers $headers -TimeoutSec 30
    $asset = @($release.assets | Where-Object name -EQ 'Slayers2Macro.zip')
    $checksum = @($release.assets | Where-Object name -EQ 'Slayers2Macro.zip.sha256')
    if ($asset.Count -ne 1 -or $checksum.Count -ne 1) { throw 'A versao publicada nao possui os arquivos esperados.' }
    New-Item -ItemType Directory -Path $install -Force | Out-Null
    $releaseDir = Join-Path $install ([string]$release.id)
    $exe = Join-Path $releaseDir 'Slayers2Macro.exe'
    if (!(Test-Path -LiteralPath $exe)) {
        $stage = Join-Path $install ('staging-' + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $stage | Out-Null
        $zip = Join-Path $stage 'release.zip'
        $hashFile = Join-Path $stage 'release.sha256'
        $downloadHeaders = $headers.Clone(); $downloadHeaders.Accept = 'application/octet-stream'
        $sizeMB = [math]::Round($asset[0].size / 1MB, 1)
        Write-Host "Baixando $($release.tag_name) ($sizeMB MB). Aguarde; esta etapa pode levar alguns minutos."
        Invoke-WebRequest -UseBasicParsing -Uri $asset[0].url -Headers $downloadHeaders -OutFile $zip -TimeoutSec 180
        Write-Host 'Download concluido. Verificando a integridade do arquivo...'
        Invoke-WebRequest -UseBasicParsing -Uri $checksum[0].url -Headers $downloadHeaders -OutFile $hashFile -TimeoutSec 60
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
        Write-Host 'Extraindo os arquivos. Aguarde a mensagem de conclusao...'
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
    if (Test-Path -LiteralPath $stateFile) {
        $oldId = (Get-Content -LiteralPath $stateFile -Raw).Trim()
        if ($oldId -match '^\d+$' -and $oldId -ne [string]$release.id) {
            Set-Content -LiteralPath $previousFile -Value $oldId -Encoding ASCII
        }
    }
    Set-Content -LiteralPath (Join-Path $install 'current.txt') -Value ([string]$release.id) -Encoding ASCII
    Write-Host "Versao pronta: $($release.tag_name). Feche o macro anterior antes de abrir esta versao."
    if (!$NaoAbrir -and (Read-Host 'Abrir agora? (S/N)') -match '^[sS]$') { Start-Process -FilePath $exe -WindowStyle Hidden }
} catch {
    Write-Host ('Nao foi possivel atualizar: ' + $_.Exception.Message)
    Write-Host 'Confirme o repositorio e se existe uma Release. Para repositorio privado, autentique gh auth login.'
    exit 1
}
