# Biblioteca de instalação do FGM. Não executa o setup do ReShade.
# Compatível com Windows PowerShell 5.1 e PowerShell 7.

$Script:FgmUtf8 = New-Object System.Text.UTF8Encoding $false

function Get-FgmArray($Value) {
    if ($null -eq $Value) { return @() }
    if ($Value -is [string]) { return @($Value) }
    if ($Value -is [System.Collections.IEnumerable]) {
        $items = New-Object System.Collections.Generic.List[object]
        foreach ($item in $Value) { $items.Add($item) }
        return $items.ToArray()
    }
    return @($Value)
}

function ConvertTo-FgmList($Value) {
    $items = New-Object System.Collections.Generic.List[object]
    foreach ($item in (Get-FgmArray $Value)) { $items.Add($item) }
    return ,$items
}

function Add-FgmObject($List, $Item) {
    if ($Item -is [System.Collections.IDictionary]) {
        $Item = New-Object psobject -Property $Item
    }
    $null = $List.Add($Item)
}

function Join-FgmPath([string]$Base, [string]$Relative) {
    $path = $Base
    $parts = $Relative -replace '\\', '/' -split '/'
    foreach ($part in $parts) {
        if ($part) { $path = Join-Path $path $part }
    }
    return $path
}

function Get-FgmSha256([string]$Path) {
    return (Get-FileHash -Algorithm SHA256 -Path $Path).Hash.ToLowerInvariant()
}

function Get-FgmSha256Bytes([byte[]]$Bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($Bytes)
    } finally {
        $sha.Dispose()
    }
    return (($hash | ForEach-Object { $_.ToString('x2') }) -join '')
}

function Write-FgmText([string]$Path, [string]$Text) {
    $parent = Split-Path $Path -Parent
    if ($parent -and -not (Test-Path $parent)) {
        New-Item -ItemType Directory -Path $parent | Out-Null
    }
    [System.IO.File]::WriteAllText($Path, $Text, $Script:FgmUtf8)
}

function Read-FgmText([string]$Path) {
    return [System.IO.File]::ReadAllText($Path)
}

function Write-FgmJson([string]$Path, $Object) {
    $json = $Object | ConvertTo-Json -Depth 8
    Write-FgmText $Path ($json + "`n")
}

function Read-FgmJson([string]$Path) {
    if (-not (Test-Path $Path)) { return $null }
    return (Read-FgmText $Path) | ConvertFrom-Json
}

function Get-FgmFiveMRoot([string]$Explicit) {
    if ($Explicit) {
        $root = $Explicit
    } else {
        if (-not $env:LOCALAPPDATA) {
            throw "FiveM não encontrado: a variável LOCALAPPDATA não existe. Nada foi criado."
        }
        $root = Join-Path $env:LOCALAPPDATA "FiveM/FiveM.app"
    }
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        throw "FiveM não está instalado em $root. Nada foi criado."
    }
    $citizen = Join-Path $root "CitizenFX.ini"
    $exe = Join-Path $root "FiveM.exe"
    if (-not (Test-Path -LiteralPath $citizen) -and -not (Test-Path -LiteralPath $exe)) {
        throw "A pasta $root não parece uma instalação do FiveM (falta CitizenFX.ini ou FiveM.exe). Nada foi criado."
    }
    return [System.IO.Path]::GetFullPath($root)
}

function Get-FgmEditionDir([string]$PackageRoot, [string]$Edition) {
    $name = $Edition.ToLowerInvariant()
    $title = $name.Substring(0, 1).ToUpperInvariant() + $name.Substring(1)
    foreach ($candidate in @($name, $title)) {
        $dir = Join-Path $PackageRoot $candidate
        if (Test-Path -LiteralPath (Join-Path $dir "manifest.json")) { return $dir }
    }
    throw "Edição '$Edition' não encontrada em $PackageRoot."
}

function Resolve-FgmPackageFile([string]$Destination, [string]$Plugins) {
    $prefix = "{fivem_plugins}/"
    if (-not $Destination.StartsWith($prefix)) {
        throw "Destino fora da pasta plugins: $Destination"
    }
    $relative = $Destination.Substring($prefix.Length)
    if ($relative -match '(^|/)\.\.(/|$)') { throw "Caminho inválido no manifesto: $Destination" }
    $leaf = Split-Path ($relative -replace '/', [System.IO.Path]::DirectorySeparatorChar) -Leaf
    $blocked = @("CitizenFX.ini", "update.rpf", "GTA5.exe", "FiveM.exe")
    if ($blocked -contains $leaf -or $leaf.ToLowerInvariant().EndsWith(".exe")) {
        throw "O instalador recusou o arquivo protegido $leaf."
    }
    $path = Join-FgmPath $Plugins $relative
    $full = [System.IO.Path]::GetFullPath($path)
    $base = [System.IO.Path]::GetFullPath($Plugins)
    if (-not $base.EndsWith([System.IO.Path]::DirectorySeparatorChar)) {
        $base = $base + [System.IO.Path]::DirectorySeparatorChar
    }
    if (-not $full.StartsWith($base, [System.StringComparison]::OrdinalIgnoreCase) -and $full -ne $base.TrimEnd([System.IO.Path]::DirectorySeparatorChar)) {
        throw "Destino escapa da pasta plugins: $full"
    }
    return @{ relative = ($relative -replace '\\', '/'); path = $full }
}

function Test-FgmReShadeBinary([string]$Path) {
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $ascii = [System.Text.Encoding]::ASCII.GetString($bytes)
    return $ascii.Contains("ReShade")
}

function Get-FgmReShadeVersion([string]$Path) {
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    $text = [System.Text.Encoding]::Unicode.GetString($bytes)
    $match = [regex]::Match($text, "FileVersion\u0000+([0-9]+\.[0-9]+\.[0-9]+)")
    if ($match.Success) { return $match.Groups[1].Value }
    return $null
}

function Test-FgmVersionAtLeast([string]$Version, [string]$Minimum) {
    $left = $Version.Split(".")
    $right = $Minimum.Split(".")
    for ($i = 0; $i -lt 3; $i++) {
        $a = 0
        $b = 0
        if ($i -lt $left.Length) { $a = [int]$left[$i] }
        if ($i -lt $right.Length) { $b = [int]$right[$i] }
        if ($a -gt $b) { return $true }
        if ($a -lt $b) { return $false }
    }
    return $true
}

function Expand-FgmRawDeflate([byte[]]$Payload) {
    Add-Type -AssemblyName System.IO.Compression
    $inputStream = New-Object System.IO.MemoryStream(,$Payload)
    try {
        $deflate = New-Object System.IO.Compression.DeflateStream($inputStream, [System.IO.Compression.CompressionMode]::Decompress)
        try {
            $output = New-Object System.IO.MemoryStream
            try {
                $deflate.CopyTo($output)
                return ,$output.ToArray()
            } finally { $output.Dispose() }
        } finally { $deflate.Dispose() }
    } finally { $inputStream.Dispose() }
}

function Expand-FgmReShade64([string]$SetupPath, $Meta) {
    $data = [System.IO.File]::ReadAllBytes($SetupPath)
    $pos = 0
    while ($pos -lt ($data.Length - 30)) {
        $found = -1
        for ($i = $pos; $i -lt ($data.Length - 3); $i++) {
            if ($data[$i] -eq 0x50 -and $data[$i + 1] -eq 0x4B -and $data[$i + 2] -eq 0x03 -and $data[$i + 3] -eq 0x04) {
                $found = $i
                break
            }
        }
        if ($found -lt 0) { break }
        $comp = [System.BitConverter]::ToInt32($data, $found + 18)
        $uncomp = [System.BitConverter]::ToInt32($data, $found + 22)
        $nameLen = [System.BitConverter]::ToUInt16($data, $found + 26)
        $extraLen = [System.BitConverter]::ToUInt16($data, $found + 28)
        $nameStart = $found + 30
        if (($nameStart + $nameLen) -gt $data.Length) { break }
        $name = [System.Text.Encoding]::ASCII.GetString($data, $nameStart, $nameLen)
        $start = $nameStart + $nameLen + $extraLen
        if ($comp -lt 0 -or ($start + $comp) -gt $data.Length) { break }
        $pos = $start + [Math]::Max($comp, 1)
        if ($name -ne $Meta.dll_entry -or $uncomp -le 0) { continue }
        $payload = New-Object byte[] $comp
        [System.Array]::Copy($data, $start, $payload, 0, $comp)
        $raw = Expand-FgmRawDeflate $payload
        if ($raw.Length -ne [int]$Meta.dll_size) {
            throw "O ReShade oficial veio com tamanho inesperado ($($raw.Length)). Nada foi instalado no FiveM."
        }
        $sha = Get-FgmSha256Bytes $raw
        if ($sha -ne $Meta.dll_sha256) {
            throw "O hash do ReShade64.dll não confere com o arquivo oficial. Nada foi instalado no FiveM."
        }
        $pe = [System.BitConverter]::ToInt32($raw, 0x3C)
        $machine = [System.BitConverter]::ToUInt16($raw, $pe + 4)
        if ($machine -ne 0x8664) {
            throw "O módulo extraído do ReShade não é a DLL x64. Nada foi instalado no FiveM."
        }
        return ,$raw
    }
    throw "Não encontrei ReShade64.dll dentro do instalador oficial. Nada foi instalado no FiveM."
}

function Get-FgmOfficialRuntime([string]$CacheRoot, [string]$ScriptRoot) {
    $metaPath = Join-Path $ScriptRoot "reshade-official.json"
    if (-not (Test-Path $metaPath)) { throw "Descritor oficial do ReShade ausente: $metaPath" }
    $meta = Read-FgmJson $metaPath
    if (-not (Test-Path $CacheRoot)) { New-Item -ItemType Directory -Path $CacheRoot | Out-Null }
    $setup = Join-Path $CacheRoot "ReShade_Setup_$($meta.version).exe"
    $dll = Join-Path $CacheRoot "ReShade64.dll"
    $needs = $true
    if ((Test-Path $setup) -and (Test-Path $dll)) {
        if ((Get-FgmSha256 $setup) -eq $meta.setup_sha256 -and (Get-FgmSha256 $dll) -eq $meta.dll_sha256) {
            $needs = $false
        }
    }
    if ($needs) {
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("fgm-reshade-" + [guid]::NewGuid().ToString("N") + ".exe")
        try {
            $headers = @{ Referer = $meta.setup_referer }
            Invoke-WebRequest -Uri $meta.setup_url -Headers $headers -OutFile $tmp -UseBasicParsing
            $setupHash = Get-FgmSha256 $tmp
            if ($setupHash -ne $meta.setup_sha256) {
                throw "O download do ReShade não confere com o hash oficial. Nada foi instalado no FiveM."
            }
            $raw = Expand-FgmReShade64 $tmp $meta
            [System.IO.File]::WriteAllBytes($dll, $raw)
            Copy-Item -LiteralPath $tmp -Destination $setup -Force
        } catch {
            if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Force }
            throw
        } finally {
            if (Test-Path $tmp) { Remove-Item -LiteralPath $tmp -Force }
        }
    }
    return $dll
}

function Set-FgmIniKey([string]$Text, [string]$Section, [string]$Key, [string]$Value) {
    $lines = @()
    if ($Text) { $lines = [regex]::Split($Text, "\r?\n") }
    $result = New-Object System.Collections.Generic.List[string]
    $sectionFound = $false
    $keySet = $false
    $inSection = $false
    foreach ($line in $lines) {
        $trim = $line.Trim()
        if ($trim.StartsWith("[") -and $trim.EndsWith("]")) {
            if ($inSection -and -not $keySet) {
                $result.Add("$Key=$Value")
                $keySet = $true
            }
            $inSection = ($trim.Substring(1, $trim.Length - 2) -eq $Section)
            if ($inSection) { $sectionFound = $true }
            $result.Add($line)
            continue
        }
        if ($inSection -and $trim -match "^$([regex]::Escape($Key))=") {
            $result.Add("$Key=$Value")
            $keySet = $true
            continue
        }
        $result.Add($line)
    }
    if ($inSection -and -not $keySet) {
        $result.Add("$Key=$Value")
        $keySet = $true
    }
    if (-not $sectionFound) {
        if ($result.Count -gt 0 -and $result[$result.Count - 1] -ne "") { $result.Add("") }
        $result.Add("[$Section]")
        $result.Add("$Key=$Value")
    }
    return (($result.ToArray() -join "`r`n").TrimEnd() + "`r`n")
}

function Ensure-FgmSearchPath([string]$Text, [string]$Key, [string]$Needed) {
    $lines = [regex]::Split($Text, "\r?\n")
    $inGeneral = $false
    $found = $false
    $result = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        $trim = $line.Trim()
        if ($trim.StartsWith("[") -and $trim.EndsWith("]")) {
            $inGeneral = ($trim -eq "[GENERAL]")
        }
        if ($inGeneral -and $trim.StartsWith("$Key=")) {
            $found = $true
            $current = $trim.Substring($Key.Length + 1)
            if ($current -notlike "*reshade-shaders*") {
                if ($current) { $line = "$Key=$current;$Needed" } else { $line = "$Key=$Needed" }
            }
        }
        $result.Add($line)
    }
    if (-not $found) {
        return Set-FgmIniKey (($result.ToArray() -join "`r`n")) "GENERAL" $Key $Needed
    }
    return (($result.ToArray() -join "`r`n").TrimEnd() + "`r`n")
}

function Get-FgmStatePath([string]$Root) { return (Join-Path $Root "FGM-state.json") }

function Read-FgmState([string]$Root) { return Read-FgmJson (Get-FgmStatePath $Root) }

function Save-FgmState([string]$Root, $State) { Write-FgmJson (Get-FgmStatePath $Root) $State }

function Find-FgmRecord($Records, [string]$Relative) {
    foreach ($item in (Get-FgmArray $Records)) {
        if ($item.relative -eq $Relative) { return $item }
    }
    return $null
}

function Copy-FgmBackup([string]$Source, [string]$Root, [string]$BackupId, [string]$Relative) {
    $dest = Join-FgmPath (Join-Path $Root "FGM-Backup/$BackupId/files") $Relative
    $parent = Split-Path $dest -Parent
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    Copy-Item -LiteralPath $Source -Destination $dest -Force
    return @{
        relative = $Relative
        backup = ("FGM-Backup/$BackupId/files/$Relative" -replace '\\', '/')
        sha256 = (Get-FgmSha256 $Source)
    }
}

function Restore-FgmOriginal([string]$Root, $Original) {
    $from = Join-FgmPath $Root $Original.backup
    $to = Join-FgmPath (Join-Path $Root "plugins") $Original.relative
    $parent = Split-Path $to -Parent
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    Copy-Item -LiteralPath $from -Destination $to -Force
}

function New-FgmState([string]$Root, [string]$Edition, [string]$Version, [string]$BackupId, $Files, $Originals, $Runtime) {
    return @{
        schema = 1
        product = "FGM"
        version = $Version
        edition = $Edition
        installed_at = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss'Z'")
        fivem_root = $Root
        backup_id = $BackupId
        files = (Get-FgmArray $Files)
        originals = (Get-FgmArray $Originals)
        runtime = $Runtime
    }
}

function Install-FgmPackageFiles([string]$EditionDir, $Manifest, [string]$Plugins, [string]$Root, [string]$BackupId, $State) {
    $files = New-Object System.Collections.Generic.List[object]
    $originals = New-Object System.Collections.Generic.List[object]
    if ($State) {
        foreach ($item in (Get-FgmArray $State.originals)) { Add-FgmObject $originals $item }
    }
    $checked = @()
    foreach ($entry in (Get-FgmArray $Manifest.files)) {
        $source = Join-FgmPath $EditionDir $entry.source
        if (-not (Test-Path -LiteralPath $source)) { throw "Arquivo do pacote ausente: $($entry.source)" }
        $hash = Get-FgmSha256 $source
        if ($hash -ne $entry.sha256) {
            throw "Hash inválido em $($entry.source). O pacote está incompleto ou alterado. Nada mais será copiado."
        }
        $dest = Resolve-FgmPackageFile $entry.destination $Plugins
        $checked += @{ entry = $entry; source = $source; dest = $dest; hash = $hash }
    }
    if (-not (Test-Path $Plugins)) { New-Item -ItemType Directory -Path $Plugins | Out-Null }
    foreach ($item in $checked) {
        $existed = Test-Path -LiteralPath $item.dest.path
        $managed = $false
        if ($State) {
            $prior = Find-FgmRecord $State.files $item.dest.relative
            if ($prior -and $prior.kind -eq "package") { $managed = $true }
        }
        if ($existed -and -not $managed -and -not (Find-FgmRecord $originals $item.dest.relative)) {
            Add-FgmObject $originals (Copy-FgmBackup $item.dest.path $Root $BackupId $item.dest.relative)
        }
        $parent = Split-Path $item.dest.path -Parent
        if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
        Copy-Item -LiteralPath $item.source -Destination $item.dest.path -Force
        $action = "created"
        if ($existed) { $action = "replaced" }
        Add-FgmObject $files @{
            relative = $item.dest.relative
            sha256 = $item.hash
            action = $action
            kind = "package"
        }
    }
    return @{ files = $files.ToArray(); originals = $originals.ToArray() }
}

function Remove-FgmDroppedFiles($OldState, $NewFiles, [string]$Root) {
    $keep = @{}
    foreach ($item in $NewFiles) { $keep[$item.relative] = $true }
    foreach ($item in (Get-FgmArray $OldState.files)) {
        if ($item.kind -ne "package") { continue }
        if ($keep.ContainsKey($item.relative)) { continue }
        $original = Find-FgmRecord $OldState.originals $item.relative
        $path = Join-FgmPath (Join-Path $Root "plugins") $item.relative
        if ($original) {
            Restore-FgmOriginal $Root $original
        } elseif (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }
}

function Update-FgmPresetIni([string]$Plugins, [string]$PresetName, [string]$Root, [string]$BackupId, $State, $Originals) {
    $Originals = ConvertTo-FgmList $Originals
    $iniPath = Join-Path $Plugins "ReShade.ini"
    $relative = "ReShade.ini"
    $existed = Test-Path -LiteralPath $iniPath
    $text = ""
    if ($existed) { $text = Read-FgmText $iniPath }
    $managed = $false
    if ($State) {
        $prior = Find-FgmRecord $State.files $relative
        if ($prior) { $managed = $true }
    }
    if ($existed -and -not $managed -and -not (Find-FgmRecord $Originals $relative)) {
        Add-FgmObject $Originals (Copy-FgmBackup $iniPath $Root $BackupId $relative)
    }
    if (-not $text) {
        $text = "[GENERAL]`r`nPresetPath=.\$PresetName`r`nEffectSearchPaths=.\reshade-shaders\Shaders\**`r`nTextureSearchPaths=.\reshade-shaders\Textures\**`r`n"
    } else {
        $text = Set-FgmIniKey $text "GENERAL" "PresetPath" ".\$PresetName"
        $text = Ensure-FgmSearchPath $text "EffectSearchPaths" ".\reshade-shaders\Shaders\**"
        $text = Ensure-FgmSearchPath $text "TextureSearchPaths" ".\reshade-shaders\Textures\**"
    }
    Write-FgmText $iniPath $text
    $action = "created"
    if ($existed) { $action = "replaced" }
    return @{
        relative = $relative
        sha256 = (Get-FgmSha256 $iniPath)
        action = $action
        kind = "ini"
        originals = $Originals
    }
}

function Install-FgmRuntime([string]$Plugins, [string]$Root, [string]$BackupId, $State, $Originals, [string]$RuntimeDll, [string]$ScriptRoot, [string]$PackageRoot, [string]$MinVersion) {
    $Originals = ConvertTo-FgmList $Originals
    if (-not (Test-Path $Plugins)) { New-Item -ItemType Directory -Path $Plugins | Out-Null }
    $dxgi = Join-Path $Plugins "dxgi.dll"
    $d3d = Join-Path $Plugins "d3d11.dll"
    $runtime = $null
    if (Test-Path -LiteralPath $dxgi) {
        if (-not (Test-FgmReShadeBinary $dxgi)) {
            throw "Existe dxgi.dll em plugins e ele não é ReShade. O FGM não substitui esse arquivo e não contorna bloqueio. Nada foi alterado nos shaders."
        }
        $version = Get-FgmReShadeVersion $dxgi
        $outdated = $version -and -not (Test-FgmVersionAtLeast $version $MinVersion)
        if ($outdated) {
            if (-not (Find-FgmRecord $Originals "dxgi.dll")) {
                Add-FgmObject $Originals (Copy-FgmBackup $dxgi $Root $BackupId "dxgi.dll")
            }
            $runtime = @{ action = "replaced"; relative = "dxgi.dll"; version = $MinVersion }
        } else {
            $runtime = @{ action = "reused"; relative = "dxgi.dll"; version = $version }
        }
    } elseif ((Test-Path -LiteralPath $d3d) -and (Test-FgmReShadeBinary $d3d)) {
        $runtime = @{ action = "reused"; relative = "d3d11.dll"; version = (Get-FgmReShadeVersion $d3d) }
    } else {
        $runtime = @{ action = "created"; relative = "dxgi.dll"; version = "6.8.0" }
    }
    $createdLicense = $false
    if ($runtime.action -ne "reused") {
        $source = $RuntimeDll
        if (-not $source) {
            $cache = Join-Path ([System.IO.Path]::GetTempPath()) "fgm-reshade-cache"
            $source = Get-FgmOfficialRuntime $cache $ScriptRoot
        }
        $license = Join-Path (Split-Path $ScriptRoot -Parent) "licenses/ReShade-BSD-3-Clause.txt"
        if (-not (Test-Path $license)) { $license = Join-Path $PackageRoot "licenses/ReShade-BSD-3-Clause.txt" }
        if (-not (Test-Path $license)) { throw "Texto da licença do ReShade ausente. A DLL não será deixada sem o aviso." }
        Copy-Item -LiteralPath $source -Destination $dxgi -Force
        $licenseDest = Join-Path $Plugins "ReShade-BSD-3-Clause.txt"
        if (-not (Test-Path $licenseDest)) {
            Copy-Item -LiteralPath $license -Destination $licenseDest -Force
            $createdLicense = $true
        }
    }
    $files = @()
    if ($runtime.action -ne "reused") {
        $files += @{
            relative = "dxgi.dll"
            sha256 = (Get-FgmSha256 $dxgi)
            action = $runtime.action
            kind = "runtime"
        }
        if ($createdLicense) {
            $licenseDest = Join-Path $Plugins "ReShade-BSD-3-Clause.txt"
            $files += @{
                relative = "ReShade-BSD-3-Clause.txt"
                sha256 = (Get-FgmSha256 $licenseDest)
                action = "created"
                kind = "license"
            }
        }
    }
    return @{ runtime = $runtime; files = $files; originals = $Originals }
}

function Resolve-FgmEditionName([string]$Edition) {
    if (-not $Edition) { return "" }
    $name = $Edition.ToLowerInvariant()
    if ($name -eq "quality") { return "ultra" }
    if ($name -eq "performance") { return "low" }
    return $name
}

function Get-FgmGraphicsFile([string]$PackageRoot, [string]$ScriptRoot) {
    $candidates = @(
        (Join-Path $PackageRoot "graphics.json"),
        (Join-Path $ScriptRoot "graphics.json")
    )
    $parent = Split-Path $ScriptRoot -Parent
    if ($parent) { $candidates += (Join-Path $parent "src/settings/graphics.json") }
    foreach ($candidate in $candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) { return $candidate }
    }
    return $null
}

function Resolve-FgmSettingsXml([string]$Explicit) {
    if ($Explicit) {
        if (Test-Path -LiteralPath $Explicit) { return ([System.IO.Path]::GetFullPath($Explicit)) }
        return $null
    }
    $candidates = New-Object System.Collections.Generic.List[string]
    $docs = [Environment]::GetFolderPath("MyDocuments")
    if ($docs) { $candidates.Add((Join-Path $docs "Rockstar Games\GTA V\settings.xml")) }
    if ($env:USERPROFILE) {
        $candidates.Add((Join-Path $env:USERPROFILE "Documents\Rockstar Games\GTA V\settings.xml"))
        $candidates.Add((Join-Path $env:USERPROFILE "OneDrive\Documents\Rockstar Games\GTA V\settings.xml"))
    }
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) { return ([System.IO.Path]::GetFullPath($candidate)) }
    }
    return $null
}

function Test-FgmSettingsAllowed([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    $leaf = [System.IO.Path]::GetFileName($full)
    if ($leaf -ne "settings.xml") {
        throw "O FGM só altera settings.xml do GTA. Recusou $leaf."
    }
    foreach ($blocked in @("CitizenFX.ini", "FiveM.exe", "GTA5.exe", "update.rpf")) {
        if ($full.ToLowerInvariant().EndsWith($blocked.ToLowerInvariant())) {
            throw "O FGM recusou o arquivo protegido $blocked."
        }
    }
    return $full
}

function Set-FgmGraphicsKeys([string]$Text, $Pairs) {
    $lines = [regex]::Split($Text, "\r?\n")
    $result = New-Object System.Collections.Generic.List[string]
    $changed = New-Object System.Collections.Generic.List[string]
    $names = @($Pairs.PSObject.Properties.Name)
    foreach ($line in $lines) {
        $updated = $line
        foreach ($key in $names) {
            $matchKey = "<" + [regex]::Escape([string]$key) + "\b"
            if ($updated -match $matchKey -and $updated -match 'value="[^"]*"') {
                $value = [string]$Pairs.$key
                $next = [regex]::Replace($updated, 'value="[^"]*"', ('value="' + $value + '"'), 1)
                if ($next -ne $updated) {
                    $updated = $next
                    if (-not $changed.Contains([string]$key)) { $changed.Add([string]$key) }
                }
            }
        }
        $result.Add($updated)
    }
    return @{ text = (($result.ToArray() -join "`r`n")); changed = $changed.ToArray() }
}

function Backup-FgmSettings([string]$Source, [string]$Root, [string]$BackupId) {
    $dest = Join-Path $Root ("FGM-Backup/" + $BackupId + "/game-settings.xml")
    $parent = Split-Path $dest -Parent
    if (-not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent | Out-Null }
    Copy-Item -LiteralPath $Source -Destination $dest -Force
    return ("FGM-Backup/" + $BackupId + "/game-settings.xml")
}

function Update-FgmGraphics([string]$Edition, [string]$Root, [string]$BackupId, [string]$PackageRoot, [string]$ScriptRoot, [string]$SettingsXml, $State) {
    $metaPath = Get-FgmGraphicsFile $PackageRoot $ScriptRoot
    if (-not $metaPath) {
        return @{ applied = $false; reason = "graphics.json ausente"; path = ""; backup = ""; keys = @() }
    }
    $doc = Read-FgmJson $metaPath
    $profile = $doc.profiles.$Edition
    if (-not $profile) { throw "Perfil gráfico ausente: $Edition" }
    $target = $null
    if ($SettingsXml) {
        $target = Resolve-FgmSettingsXml $SettingsXml
    } elseif ($State -and $State.settings -and $State.settings.path -and (Test-Path -LiteralPath ([string]$State.settings.path))) {
        $target = [string]$State.settings.path
    } else {
        $target = Resolve-FgmSettingsXml ""
    }
    if (-not $target) {
        return @{ applied = $false; reason = "settings.xml ausente"; path = ""; backup = ""; keys = @() }
    }
    $target = Test-FgmSettingsAllowed $target
    $backupRel = ""
    if ($State -and $State.settings -and $State.settings.applied -and $State.settings.backup) {
        $backupRel = [string]$State.settings.backup
    } else {
        $backupRel = Backup-FgmSettings $target $Root $BackupId
    }
    $updated = Set-FgmGraphicsKeys (Read-FgmText $target) $profile.apply
    if (@($updated.changed).Count -eq 0) {
        return @{ applied = $false; reason = "nenhuma chave encontrada"; path = $target; backup = ""; keys = @() }
    }
    Write-FgmText $target $updated.text
    return @{ applied = $true; reason = "ok"; path = $target; backup = $backupRel; keys = @($updated.changed) }
}

function Restore-FgmGraphics($State, [string]$Root) {
    if (-not $State.settings -or -not $State.settings.applied) { return }
    $backup = Join-FgmPath $Root ([string]$State.settings.backup)
    $target = [string]$State.settings.path
    if ((Test-Path -LiteralPath $backup) -and $target) {
        Copy-Item -LiteralPath $backup -Destination $target -Force
    }
}

function Write-FgmSettingsLine($Settings) {
    if ($Settings.applied) {
        Write-Output ("FGM settings ok keys=" + ((@($Settings.keys) | Where-Object { $_ }) -join ","))
    } else {
        Write-Output ("FGM settings skip reason=" + [string]$Settings.reason)
    }
}

function Invoke-FgmFreshInstall([string]$Edition, [string]$Root, [string]$PackageRoot, [string]$RuntimeDll, [string]$ScriptRoot, [string]$SettingsXml) {
    $citizen = Join-Path $Root "CitizenFX.ini"
    $citizenBefore = $null
    if (Test-Path $citizen) { $citizenBefore = Get-FgmSha256 $citizen }
    $editionDir = Get-FgmEditionDir $PackageRoot $Edition
    $manifest = Read-FgmJson (Join-Path $editionDir "manifest.json")
    if ($manifest.kind -ne "client-local") { throw "O manifesto não é um pacote local." }
    $plugins = Join-Path $Root "plugins"
    $dxgi = Join-Path $plugins "dxgi.dll"
    $minVersion = [string]$manifest.min_reshade
    if (-not $minVersion) { $minVersion = "5.0.0" }
    if ((Test-Path $dxgi) -and -not (Test-FgmReShadeBinary $dxgi)) {
        throw "Existe dxgi.dll em plugins e ele não é ReShade. O FGM não substitui esse arquivo. Nada foi instalado."
    }
    $needsRuntime = $true
    if ((Test-Path $dxgi) -and (Test-FgmReShadeBinary $dxgi)) {
        $existingVersion = Get-FgmReShadeVersion $dxgi
        $tooOld = $existingVersion -and -not (Test-FgmVersionAtLeast $existingVersion $minVersion)
        if (-not $tooOld) { $needsRuntime = $false }
    } elseif ((Test-Path (Join-Path $plugins "d3d11.dll")) -and (Test-FgmReShadeBinary (Join-Path $plugins "d3d11.dll"))) {
        $needsRuntime = $false
    }
    if ($needsRuntime -and -not $RuntimeDll) {
        $cache = Join-Path ([System.IO.Path]::GetTempPath()) "fgm-reshade-cache"
        $RuntimeDll = Get-FgmOfficialRuntime $cache $ScriptRoot
    }
    $backupId = [DateTime]::UtcNow.ToString("yyyyMMdd-HHmmss-fff")
    $installed = Install-FgmPackageFiles $editionDir $manifest $plugins $Root $backupId $null
    $runtime = Install-FgmRuntime $plugins $Root $backupId $null $installed.originals $RuntimeDll $ScriptRoot $PackageRoot $minVersion
    $ini = Update-FgmPresetIni $plugins $manifest.preset $Root $backupId $null $runtime.originals
    $all = New-Object System.Collections.Generic.List[object]
    foreach ($item in $installed.files) { Add-FgmObject $all $item }
    foreach ($item in $runtime.files) { Add-FgmObject $all $item }
    Add-FgmObject $all @{ relative = $ini.relative; sha256 = $ini.sha256; action = $ini.action; kind = $ini.kind }
    $settings = Update-FgmGraphics $Edition $Root $backupId $PackageRoot $ScriptRoot $SettingsXml $null
    $state = New-FgmState $Root $Edition $manifest.version $backupId $all.ToArray() $ini.originals $runtime.runtime
    $state["settings"] = $settings
    Save-FgmState $Root $state
    if ($citizenBefore -and (Get-FgmSha256 $citizen) -ne $citizenBefore) {
        throw "CitizenFX.ini foi modificado. Isso não é permitido."
    }
    Write-FgmSettingsLine $settings
    Write-Output "FGM install ok edition=$Edition"
}

function Invoke-FgmRepair([string]$Root, [string]$PackageRoot, [string]$RuntimeDll, [string]$ScriptRoot, [string]$SettingsXml) {
    $state = Read-FgmState $Root
    if (-not $state) { throw "Não há instalação do FGM para reparar." }
    $editionDir = Get-FgmEditionDir $PackageRoot $state.edition
    $manifest = Read-FgmJson (Join-Path $editionDir "manifest.json")
    $plugins = Join-Path $Root "plugins"
    $installed = Install-FgmPackageFiles $editionDir $manifest $plugins $Root $state.backup_id $state
    $ini = Update-FgmPresetIni $plugins $manifest.preset $Root $state.backup_id $state $installed.originals
    $all = New-Object System.Collections.Generic.List[object]
    foreach ($item in $installed.files) { Add-FgmObject $all $item }
    foreach ($item in (Get-FgmArray $state.files)) {
        if ($item.kind -eq "runtime" -or $item.kind -eq "license") { Add-FgmObject $all $item }
    }
    $runtimeRecord = $state.runtime
    $dxgi = Join-Path $plugins "dxgi.dll"
    if ($runtimeRecord -and $runtimeRecord.action -eq "created" -and -not (Test-Path $dxgi)) {
        $again = Install-FgmRuntime $plugins $Root $state.backup_id $state $ini.originals $RuntimeDll $ScriptRoot $PackageRoot $manifest.min_reshade
        $runtimeRecord = $again.runtime
        $all = New-Object System.Collections.Generic.List[object]
        foreach ($item in $installed.files) { Add-FgmObject $all $item }
        foreach ($item in $again.files) { Add-FgmObject $all $item }
    }
    Add-FgmObject $all @{ relative = $ini.relative; sha256 = $ini.sha256; action = $ini.action; kind = "ini" }
    $settings = Update-FgmGraphics $state.edition $Root $state.backup_id $PackageRoot $ScriptRoot $SettingsXml $state
    $state.files = $all.ToArray()
    $state.originals = (Get-FgmArray $ini.originals)
    $state.version = $manifest.version
    $state.runtime = $runtimeRecord
    $state.settings = $settings
    $state.installed_at = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss'Z'")
    Save-FgmState $Root $state
    Write-FgmSettingsLine $settings
    Write-Output "FGM repair ok edition=$($state.edition)"
}

function Invoke-FgmSwitch([string]$Edition, [string]$Root, [string]$PackageRoot, [string]$RuntimeDll, [string]$ScriptRoot, [string]$SettingsXml) {
    $state = Read-FgmState $Root
    if (-not $state) { throw "Não há FGM instalado para trocar de edição." }
    if ($state.edition -eq $Edition) {
        Invoke-FgmRepair $Root $PackageRoot $RuntimeDll $ScriptRoot $SettingsXml
        return
    }
    $editionDir = Get-FgmEditionDir $PackageRoot $Edition
    $manifest = Read-FgmJson (Join-Path $editionDir "manifest.json")
    $plugins = Join-Path $Root "plugins"
    $installed = Install-FgmPackageFiles $editionDir $manifest $plugins $Root $state.backup_id $state
    Remove-FgmDroppedFiles $state $installed.files $Root
    $ini = Update-FgmPresetIni $plugins $manifest.preset $Root $state.backup_id $state $installed.originals
    $all = New-Object System.Collections.Generic.List[object]
    foreach ($item in $installed.files) { Add-FgmObject $all $item }
    foreach ($item in (Get-FgmArray $state.files)) {
        if ($item.kind -eq "runtime" -or $item.kind -eq "license") { Add-FgmObject $all $item }
    }
    Add-FgmObject $all @{ relative = $ini.relative; sha256 = $ini.sha256; action = $ini.action; kind = "ini" }
    $settings = Update-FgmGraphics $Edition $Root $state.backup_id $PackageRoot $ScriptRoot $SettingsXml $state
    $state.edition = $Edition
    $state.version = $manifest.version
    $state.files = $all.ToArray()
    $state.originals = (Get-FgmArray $ini.originals)
    $state.settings = $settings
    $state.installed_at = [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ss'Z'")
    Save-FgmState $Root $state
    Write-FgmSettingsLine $settings
    Write-Output "FGM switch ok edition=$Edition"
}

function Invoke-FgmUninstall([string]$Root) {
    $state = Read-FgmState $Root
    if (-not $state) { throw "Não há instalação do FGM para remover." }
    Restore-FgmGraphics $state $Root
    $plugins = Join-Path $Root "plugins"
    $items = @(Get-FgmArray $state.files)
    for ($i = $items.Length - 1; $i -ge 0; $i--) {
        $item = $items[$i]
        if ($item.action -eq "reused") { continue }
        $original = Find-FgmRecord $state.originals $item.relative
        $path = Join-FgmPath $plugins $item.relative
        if ($original) {
            Restore-FgmOriginal $Root $original
        } elseif (Test-Path -LiteralPath $path) {
            Remove-Item -LiteralPath $path -Force
        }
    }
    Remove-Item -LiteralPath (Get-FgmStatePath $Root) -Force
    Write-Output "FGM uninstall ok"
}

function Invoke-FgmCommand([string]$Command, [string]$Edition, [string]$FiveMRoot, [string]$PackageRoot, [string]$RuntimeDll, [string]$ScriptRoot, [string]$SettingsXml) {
    if (-not $PackageRoot) { $PackageRoot = $ScriptRoot }
    $Edition = Resolve-FgmEditionName $Edition
    if ($Command -eq "uninstall") {
        $root = Get-FgmFiveMRoot $FiveMRoot
        Invoke-FgmUninstall $root
        return
    }
    if ($Command -eq "repair") {
        $root = Get-FgmFiveMRoot $FiveMRoot
        Invoke-FgmRepair $root $PackageRoot $RuntimeDll $ScriptRoot $SettingsXml
        return
    }
    if (-not $Edition) { throw "Informe a edição: ultra, high, medium ou low." }
    $root = Get-FgmFiveMRoot $FiveMRoot
    $state = Read-FgmState $root
    if ($Command -eq "switch" -or ($state -and $state.edition -ne $Edition)) {
        if (-not $state) { throw "Não há FGM instalado para trocar de edição." }
        Invoke-FgmSwitch $Edition $root $PackageRoot $RuntimeDll $ScriptRoot $SettingsXml
        return
    }
    if ($state -and $state.edition -eq $Edition) {
        Invoke-FgmRepair $root $PackageRoot $RuntimeDll $ScriptRoot $SettingsXml
        return
    }
    Invoke-FgmFreshInstall $Edition $root $PackageRoot $RuntimeDll $ScriptRoot $SettingsXml
}
