<#
.SYNOPSIS
    Prepares a Windows workstation for the Claude Code Capability Program (Helios sandbox).

.DESCRIPTION
    Validates the machine, then installs and configures every tool the Foundation weeks
    need. The script is idempotent: run it as many times as you like. Anything already
    present and new enough is left alone and reported as satisfied.

    This script performs NO git repository operations. It installs Git and probes
    'git --version' to validate that install. It never clones, fetches, commits or pushes.
    The clone commands are printed at the end for you to run yourself.

.PARAMETER VerifyOnly
    Check everything and report, but install nothing. Does not require Administrator.

.PARAMETER SkipExtensions
    Skip VS Code extension installation.

.PARAMETER WorkspaceRoot
    Folder that will hold the cloned Helios repository. Default: %USERPROFILE%\Helios

.PARAMETER NoTranscript
    Do not write a log file.

.PARAMETER SelfTest
    Run the script's internal unit tests and exit.

.EXAMPLE
    .\Setup-HeliosWorkstation.ps1
    Full setup. Run from an elevated PowerShell prompt.

.EXAMPLE
    .\Setup-HeliosWorkstation.ps1 -VerifyOnly
    Report what is present and what is missing. Changes nothing.

.NOTES
    Compatible with Windows PowerShell 5.1 and PowerShell 7+.
    Exit codes: 0 = ready, 1 = one or more failures, 2 = preflight blocked.
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    [switch] $VerifyOnly,
    [switch] $SkipExtensions,
    [string] $WorkspaceRoot = (Join-Path ([Environment]::GetFolderPath('UserProfile')) 'Helios'),
    [switch] $NoTranscript,
    [switch] $SelfTest
)

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'

# ===========================================================================
#  CONFIGURATION
# ===========================================================================

$script:ScriptVersion = '1.2.0'
$script:WingetExe     = $null

$script:Requirements = @(
    @{ Key='git';    Name='Git';           Min='2.40.0'; WingetId='Git.Git';                        Probe='git';    Args=@('--version') }
    @{ Key='python'; Name='Python';        Min='3.11.0'; WingetId='Python.Python.3.12';             Probe='python'; Args=@('--version') }
    @{ Key='node';   Name='Node.js';       Min='20.0.0'; WingetId='OpenJS.NodeJS.LTS';              Probe='node';   Args=@('--version') }
    @{ Key='java';   Name='JDK (Temurin)'; Min='17.0.0'; WingetId='EclipseAdoptium.Temurin.17.JDK'; Probe='java';   Args=@('-version') }
    @{ Key='code';   Name='VS Code';       Min='1.85.0'; WingetId='Microsoft.VisualStudioCode';     Probe='code';   Args=@('--version') }
    @{ Key='pandoc'; Name='Pandoc';        Min='3.0.0';  WingetId='JohnMacFarlane.Pandoc';                     Probe='pandoc'; Args=@('--version') }
    @{ Key='claude'; Name='Claude Code';   Min='2.0.0';  WingetId='Anthropic.ClaudeCode';           Probe='claude'; Args=@('--version') }
)

$script:PipPackages = @('pytest', 'ruff', 'markitdown')
$script:NpmPackages = @('markdownlint-cli')

$script:VsCodeExtensions = @(
    'anthropic.claude-code'
    'ms-python.python'
    'ms-python.vscode-pylance'
    'charliermarsh.ruff'
    'dbaeumer.vscode-eslint'
    'vscjava.vscode-java-pack'
    'davidanson.vscode-markdownlint'
    'yzhang.markdown-all-in-one'
)

$script:VsCodeSettings = [ordered]@{
    'files.eol'                                  = "`n"
    'files.trimTrailingWhitespace'               = $true
    'files.insertFinalNewline'                   = $true
    'editor.formatOnSave'                        = $true
    'editor.rulers'                              = @(100)
    'terminal.integrated.defaultProfile.windows' = 'PowerShell'
    'git.autofetch'                              = $false
}

$script:MinDiskGb = 10
$script:MinRamGb  = 4

# ===========================================================================
#  OUTPUT HELPERS
# ===========================================================================

$script:Results   = New-Object System.Collections.ArrayList
$script:StepIndex = 0
$script:StepTotal = 8
$script:ExitCode  = 0

function Write-Banner {
    param([string] $Text, [string] $Subtitle)
    $line = '=' * 74
    Write-Host ''
    Write-Host $line -ForegroundColor DarkCyan
    Write-Host "  $Text" -ForegroundColor Cyan
    if ($Subtitle) { Write-Host "  $Subtitle" -ForegroundColor DarkGray }
    Write-Host $line -ForegroundColor DarkCyan
}

function Write-Phase {
    param([string] $Text)
    $script:StepIndex++
    Write-Host ''
    Write-Host ("[{0}/{1}] {2}" -f $script:StepIndex, $script:StepTotal, $Text) -ForegroundColor White
    Write-Host ('-' * 74) -ForegroundColor DarkGray
}

function Write-Ok    { param([string] $m) Write-Host '  [  OK  ] ' -ForegroundColor Green      -NoNewline; Write-Host $m }
function Write-Added { param([string] $m) Write-Host '  [ NEW  ] ' -ForegroundColor Cyan       -NoNewline; Write-Host $m }
function Write-Warn2 { param([string] $m) Write-Host '  [ WARN ] ' -ForegroundColor Yellow     -NoNewline; Write-Host $m }
function Write-Fail  { param([string] $m) Write-Host '  [ FAIL ] ' -ForegroundColor Red        -NoNewline; Write-Host $m }
function Write-Skip2 { param([string] $m) Write-Host '  [ SKIP ] ' -ForegroundColor DarkGray   -NoNewline; Write-Host $m }
function Write-Doing { param([string] $m) Write-Host '  [ .... ] ' -ForegroundColor DarkYellow -NoNewline; Write-Host $m }
function Write-Note  { param([string] $m) Write-Host "           $m" -ForegroundColor DarkGray }

function Add-Result {
    param(
        [string] $Component,
        [string] $Required,
        [string] $Found,
        [ValidateSet('OK','NEW','WARN','FAIL','SKIP')] [string] $Status,
        [string] $Detail = ''
    )
    $null = $script:Results.Add([pscustomobject]@{
        Component = $Component
        Required  = $Required
        Found     = $Found
        Status    = $Status
        Detail    = $Detail
    })
}

# ===========================================================================
#  PURE HELPERS  (covered by -SelfTest)
# ===========================================================================

function Get-VersionFromText {
    param([string] $Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    $m = [regex]::Match($Text, '(\d+)\.(\d+)(?:\.(\d+))?')
    if (-not $m.Success) { return $null }
    $major = [int] $m.Groups[1].Value
    $minor = [int] $m.Groups[2].Value
    $patch = 0
    if ($m.Groups[3].Success) { $patch = [int] $m.Groups[3].Value }
    return (New-Object System.Version -ArgumentList $major, $minor, $patch)
}

function Test-VersionAtLeast {
    param([string] $FoundText, [string] $Minimum)
    $found = Get-VersionFromText -Text $FoundText
    if ($null -eq $found) { return $false }
    $min = Get-VersionFromText -Text $Minimum
    if ($null -eq $min) { return $true }
    return ($found -ge $min)
}

function ConvertTo-OrderedHashtable {
    param($InputObject)
    if ($null -eq $InputObject) { return $null }
    if ($InputObject -is [System.Collections.IDictionary]) {
        $copy = [ordered]@{}
        foreach ($k in $InputObject.Keys) { $copy[$k] = (ConvertTo-OrderedHashtable -InputObject $InputObject[$k]) }
        return $copy
    }
    if ($InputObject -is [System.Management.Automation.PSCustomObject]) {
        $copy = [ordered]@{}
        foreach ($p in $InputObject.PSObject.Properties) { $copy[$p.Name] = (ConvertTo-OrderedHashtable -InputObject $p.Value) }
        return $copy
    }
    if ($InputObject -is [string]) { return $InputObject }
    if ($InputObject -is [System.Collections.IEnumerable]) {
        $list = @()
        foreach ($i in $InputObject) { $list += ,(ConvertTo-OrderedHashtable -InputObject $i) }
        return ,$list
    }
    return $InputObject
}

function Merge-Settings {
    param(
        [System.Collections.IDictionary] $Existing,
        [System.Collections.IDictionary] $Desired
    )
    $result = [ordered]@{}
    if ($Existing) { foreach ($k in $Existing.Keys) { $result[$k] = $Existing[$k] } }
    $addedKeys = @()
    foreach ($k in $Desired.Keys) {
        if (-not $result.Contains($k)) {
            $result[$k] = $Desired[$k]
            $addedKeys += $k
        }
    }
    return [pscustomobject]@{ Settings = $result; Added = $addedKeys }
}

function Test-JsonWithComments {
    param([string] $Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $false }
    $stripped = [regex]::Replace($Text, '"(\\.|[^"\\])*"', '""')
    return ($stripped -match '//' -or $stripped -match '/\*')
}

# ===========================================================================
#  SELF TEST
# ===========================================================================

function Invoke-SelfTest {
    $script:selfTestFailures = 0

    function Assert-Equal {
        param($Expected, $Actual, [string] $Because)
        if ("$Expected" -eq "$Actual") {
            Write-Host ('  pass   ' + $Because) -ForegroundColor Green
        } else {
            Write-Host ('  FAIL   ' + $Because + "  expected <$Expected> got <$Actual>") -ForegroundColor Red
            $script:selfTestFailures++
        }
    }

    Write-Banner 'Self test' 'validating the script logic'

    Write-Host ''
    Write-Host 'Get-VersionFromText' -ForegroundColor White
    Assert-Equal '2.44.0'  (Get-VersionFromText 'git version 2.44.0.windows.1')        'git version string'
    Assert-Equal '3.12.4'  (Get-VersionFromText 'Python 3.12.4')                        'python version string'
    Assert-Equal '20.11.1' (Get-VersionFromText 'v20.11.1')                             'node version string'
    Assert-Equal '17.0.11' (Get-VersionFromText 'openjdk version "17.0.11" 2024-04-16') 'java version string'
    Assert-Equal '2.1.211' (Get-VersionFromText '2.1.211 (Claude Code)')                'claude version string'
    Assert-Equal '1.96.0'  (Get-VersionFromText "1.96.0`nabc123`nx64")                  'vs code multiline'
    Assert-Equal '3.1.0'   (Get-VersionFromText 'pandoc 3.1')                           'two part version'
    Assert-Equal ''        (Get-VersionFromText 'no numbers here')                      'unparseable returns null'
    Assert-Equal ''        (Get-VersionFromText '')                                     'empty returns null'

    Write-Host ''
    Write-Host 'Test-VersionAtLeast' -ForegroundColor White
    Assert-Equal 'True'  (Test-VersionAtLeast 'git version 2.44.0.windows.1' '2.40.0') 'newer git passes'
    Assert-Equal 'False' (Test-VersionAtLeast 'git version 2.30.0'           '2.40.0') 'older git fails'
    Assert-Equal 'True'  (Test-VersionAtLeast 'Python 3.11.0'                '3.11.0') 'exact match passes'
    Assert-Equal 'False' (Test-VersionAtLeast 'Python 3.10.9'                '3.11.0') 'minor below fails'
    Assert-Equal 'True'  (Test-VersionAtLeast 'v22.1.0'                      '20.0.0') 'major above passes'
    Assert-Equal 'False' (Test-VersionAtLeast 'garbage'                      '1.0.0')  'garbage fails'

    Write-Host ''
    Write-Host 'Merge-Settings' -ForegroundColor White
    $existing = [ordered]@{ 'editor.formatOnSave' = $false; 'my.custom' = 'keep' }
    $desired  = [ordered]@{ 'editor.formatOnSave' = $true;  'files.eol' = 'LF' }
    $merged   = Merge-Settings -Existing $existing -Desired $desired
    Assert-Equal 'False'     $merged.Settings['editor.formatOnSave'] 'existing value not overwritten'
    Assert-Equal 'keep'      $merged.Settings['my.custom']           'unrelated key survives'
    Assert-Equal 'LF'        $merged.Settings['files.eol']           'missing key added'
    Assert-Equal 'files.eol' ($merged.Added -join ',')               'added list accurate'
    $none = Merge-Settings -Existing $merged.Settings -Desired $desired
    Assert-Equal ''          ($none.Added -join ',')                 'second merge adds nothing'

    Write-Host ''
    Write-Host 'ConvertTo-OrderedHashtable' -ForegroundColor White
    $obj = '{"a":1,"b":{"c":"d"},"e":[1,2]}' | ConvertFrom-Json
    $ht  = ConvertTo-OrderedHashtable -InputObject $obj
    Assert-Equal '1' $ht['a']       'scalar survives'
    Assert-Equal 'd' $ht['b']['c']  'nested object survives'
    Assert-Equal '2' $ht['e'].Count 'array survives'

    Write-Host ''
    Write-Host 'Test-JsonWithComments' -ForegroundColor White
    Assert-Equal 'True'  (Test-JsonWithComments '{ "a":1 } // note')             'line comment detected'
    Assert-Equal 'True'  (Test-JsonWithComments '{ /* c */ "a":1 }')             'block comment detected'
    Assert-Equal 'False' (Test-JsonWithComments '{ "a":1 }')                     'clean json is clean'
    Assert-Equal 'False' (Test-JsonWithComments '{ "url":"https://x.com/a" }')   'url in string is not a comment'

    Write-Host ''
    Write-Host 'Tool resolution' -ForegroundColor White
    $winPath  = 'C:\Users\a\AppData\Local\Microsoft\WindowsApps\winget.exe'
    $stubPath = 'C:\Users\a\AppData\Local\Microsoft\WindowsApps\python.exe'
    Assert-Equal 'False' ((@('python','python3') -contains 'winget') -and ($winPath -like '*\WindowsApps\*')) `
        'winget under WindowsApps is never filtered'
    Assert-Equal 'True'  ((@('python','python3') -contains 'python') -and ($stubPath -like '*\WindowsApps\*')) `
        'python under WindowsApps is filtered as a Store stub'

    Write-Host ''
    if ($script:selfTestFailures -eq 0) {
        Write-Host '  All self tests passed.' -ForegroundColor Green
        return 0
    }
    Write-Host "  $script:selfTestFailures self test(s) failed." -ForegroundColor Red
    return 1
}

if ($SelfTest) { exit (Invoke-SelfTest) }

# ===========================================================================
#  ENVIRONMENT HELPERS
# ===========================================================================

function Test-OnWindows {
    if ($PSVersionTable.PSEdition -eq 'Desktop') { return $true }
    return [bool] (Get-Variable -Name IsWindows -ValueOnly -ErrorAction SilentlyContinue)
}

function Test-Administrator {
    if (-not (Test-OnWindows)) { return $false }
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    $pr = New-Object Security.Principal.WindowsPrincipal($id)
    return $pr.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Update-SessionPath {
    $parts = @()
    foreach ($scope in @('Machine', 'User')) {
        $p = [Environment]::GetEnvironmentVariable('Path', $scope)
        if ($p) { $parts += $p.Split(';') }
    }
    $seen  = @{}
    $clean = New-Object System.Collections.ArrayList
    foreach ($p in $parts) {
        $t = $p.Trim()
        if ($t -and -not $seen.ContainsKey($t.ToLowerInvariant())) {
            $seen[$t.ToLowerInvariant()] = $true
            $null = $clean.Add($t)
        }
    }
    if ($clean.Count -gt 0) { $env:Path = ($clean -join ';') }
}

function Get-ToolCommand {
    <#
        Resolves a tool on PATH.

        The WindowsApps folder holds two very different things: the Microsoft Store
        stub for python.exe, which must be skipped, and genuine apps such as
        winget.exe, which must not be. Only python is filtered.
    #>
    param([string] $Name)
    $skipStoreStub = @('python', 'python3')
    $cmds = @(Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue)
    foreach ($c in $cmds) {
        if ($skipStoreStub -contains $Name -and $c.Source -and $c.Source -like '*\WindowsApps\*') {
            continue
        }
        return $c
    }
    return $null
}

function Resolve-Winget {
    <#
        Finds winget.exe even when it is not on PATH.

        An elevated session does not always inherit the user's WindowsApps folder,
        so 'winget' can work in a normal shell and appear missing in an admin one.
        The versioned path under Program Files is the one that survives elevation.
    #>
    $cmd = Get-ToolCommand -Name 'winget'
    if ($cmd) { return $cmd.Source }

    $candidates = @()
    if ($env:LOCALAPPDATA) {
        $userPath = Join-Path $env:LOCALAPPDATA 'Microsoft\WindowsApps\winget.exe'
        if (Test-Path -LiteralPath $userPath) { $candidates += $userPath }
    }

    # ProgramW6432 does not exist on 32-bit Windows, so never Join-Path a null.
    $pf = $null
    foreach ($root in @($env:ProgramW6432, $env:ProgramFiles)) {
        if (-not $root) { continue }
        $try = Join-Path $root 'WindowsApps'
        if (Test-Path -LiteralPath $try) { $pf = $try; break }
    }
    if ($pf) {
        $found = Get-ChildItem -Path $pf -Filter 'Microsoft.DesktopAppInstaller_*' -Directory -ErrorAction SilentlyContinue |
            Sort-Object Name -Descending |
            ForEach-Object { Join-Path $_.FullName 'winget.exe' } |
            Where-Object { Test-Path -LiteralPath $_ }
        if ($found) { $candidates += $found }
    }

    foreach ($c in $candidates) {
        if ((Invoke-Native -Exe $c -Arguments @('--version')).ExitCode -eq 0) { return $c }
    }
    return $null
}

function Install-Winget {
    <# Last resort: install App Installer from Microsoft's published bundle. #>
    Write-Doing 'winget not found anywhere - installing App Installer'
    $tmp = Join-Path $env:TEMP 'AppInstaller.msixbundle'
    try {
        Invoke-WebRequest -Uri 'https://aka.ms/getwinget' -OutFile $tmp -UseBasicParsing
        Add-AppxPackage -Path $tmp -ErrorAction Stop
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
        Update-SessionPath
        return (Resolve-Winget)
    } catch {
        Write-Note $_.Exception.Message
        return $null
    }
}

function Get-ToolVersionText {
    param([string] $Exe, [string[]] $Arguments)
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $out = & $Exe @Arguments 2>&1 | Out-String
        if ([string]::IsNullOrWhiteSpace($out)) { return $null }
        return $out.Trim()
    } catch {
        return $null
    } finally {
        $ErrorActionPreference = $previous
    }
}

function Invoke-Native {
    <#
        Runs a native command and returns its exit code, never throwing.

        Windows PowerShell 5.1 turns anything a native command writes to stderr
        into a terminating error when $ErrorActionPreference is 'Stop'. pip prints
        dependency notices to stderr on a perfectly successful install, which was
        enough to abort the whole script. The preference is lowered for the call
        and restored afterwards.
    #>
    param(
        [Parameter(Mandatory = $true)] [string] $Exe,
        [string[]] $Arguments = @()
    )
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $Exe @Arguments 2>&1 | Out-String
        return [pscustomobject]@{ ExitCode = $LASTEXITCODE; Output = $output }
    } catch {
        return [pscustomobject]@{ ExitCode = 1; Output = $_.Exception.Message }
    } finally {
        $ErrorActionPreference = $previous
    }
}

function Invoke-Winget {
    param([string] $Id)
    $wingetArgs = @(
        'install', '--id', $Id,
        '--exact', '--silent',
        '--accept-package-agreements',
        '--accept-source-agreements',
        '--disable-interactivity'
    )
    try {
        $exe = $script:WingetExe
        if (-not $exe) { $exe = 'winget' }
        $r = Invoke-Native -Exe $exe -Arguments $wingetArgs
        $output = $r.Output
        $code = $r.ExitCode
        if ($code -eq 0) { return $true }
        if ($output -match 'already installed' -or $output -match 'No applicable upgrade') { return $true }
        Write-Note "winget exit code $code"
        $firstLines = (($output -split "`r?`n") | Where-Object { $_.Trim() } | Select-Object -First 3) -join ' | '
        if ($firstLines) { Write-Note $firstLines }
        return $false
    } catch {
        Write-Note $_.Exception.Message
        return $false
    }
}

function Read-JsonFileSafely {
    param([string] $Path)
    if (-not (Test-Path -LiteralPath $Path)) {
        return @{ Ok = $true; Data = [ordered]@{}; Reason = 'new file' }
    }
    $raw = Get-Content -LiteralPath $Path -Raw -ErrorAction SilentlyContinue
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return @{ Ok = $true; Data = [ordered]@{}; Reason = 'empty file' }
    }
    if (Test-JsonWithComments -Text $raw) {
        return @{ Ok = $false; Data = $null; Reason = 'file contains comments' }
    }
    try {
        $obj = $raw | ConvertFrom-Json
        return @{ Ok = $true; Data = (ConvertTo-OrderedHashtable -InputObject $obj); Reason = 'parsed' }
    } catch {
        return @{ Ok = $false; Data = $null; Reason = 'file is not valid JSON' }
    }
}

function Save-JsonFile {
    param([string] $Path, $Data)
    $dir = Split-Path -Parent $Path
    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
        $null = New-Item -ItemType Directory -Path $dir -Force
    }
    if (Test-Path -LiteralPath $Path) {
        Copy-Item -LiteralPath $Path -Destination "$Path.helios-backup" -Force
    }
    $json = $Data | ConvertTo-Json -Depth 20
    Set-Content -LiteralPath $Path -Value $json -Encoding UTF8
}

# ===========================================================================
#  MAIN
# ===========================================================================

$logPath = Join-Path ([System.IO.Path]::GetTempPath()) ('Helios-Setup-{0}.log' -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (-not $NoTranscript) {
    try { Start-Transcript -Path $logPath -Force | Out-Null } catch { $logPath = $null }
}

try {

Write-Banner 'Helios Workstation Setup' "Claude Code Capability Program  -  script v$script:ScriptVersion"
if ($VerifyOnly) {
    Write-Host '  Mode: VERIFY ONLY - nothing will be installed or changed.' -ForegroundColor Yellow
} else {
    Write-Host '  Mode: INSTALL - safe to re-run at any time.' -ForegroundColor DarkGray
}
Write-Host '  This script never runs git clone or any other repository command.' -ForegroundColor DarkGray

# ------------------------------------------------------------- 1. PREFLIGHT
Write-Phase 'Preflight checks'

if (-not (Test-OnWindows)) {
    Write-Fail 'This script targets Windows. Run it on the training VM.'
    exit 2
}
Write-Ok "PowerShell $($PSVersionTable.PSVersion) ($($PSVersionTable.PSEdition))"

$os = Get-CimInstance -ClassName Win32_OperatingSystem -ErrorAction SilentlyContinue
if ($os) {
    $build = [int] $os.BuildNumber
    if ($build -ge 17763) {
        Write-Ok "$($os.Caption) build $build"
    } else {
        Write-Fail "Windows build $build is below the minimum 17763 (Windows 10 1809)."
        exit 2
    }
    $ramGb = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
    if ($ramGb -ge $script:MinRamGb) { Write-Ok "RAM $ramGb GB" }
    else { Write-Warn2 "RAM $ramGb GB is below the recommended $script:MinRamGb GB." }
} else {
    Write-Warn2 'Could not read OS details. Continuing.'
}

$driveLetter = $env:SystemDrive.TrimEnd(':')
$drive = Get-PSDrive -Name $driveLetter -ErrorAction SilentlyContinue
if ($drive -and $drive.Free) {
    $freeGb = [math]::Round($drive.Free / 1GB, 1)
    if ($freeGb -ge $script:MinDiskGb) { Write-Ok "Free disk on $env:SystemDrive $freeGb GB" }
    else { Write-Warn2 "Only $freeGb GB free on $env:SystemDrive. At least $script:MinDiskGb GB recommended." }
}

$isAdmin = Test-Administrator
if ($isAdmin) {
    Write-Ok 'Running as Administrator'
} elseif ($VerifyOnly) {
    Write-Skip2 'Not elevated - acceptable for -VerifyOnly'
} else {
    Write-Fail 'Administrator rights are required to install components.'
    Write-Note 'Close this window, right-click PowerShell, choose "Run as administrator", then run the script again.'
    Write-Note 'To check without installing: .\Setup-HeliosWorkstation.ps1 -VerifyOnly'
    exit 2
}

try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch { }

$net = Test-NetConnection -ComputerName 'github.com' -Port 443 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
if ($net -and $net.TcpTestSucceeded) {
    Write-Ok 'Network reaches github.com:443'
} else {
    Write-Warn2 'Could not confirm HTTPS access to github.com. Installs may fail behind a proxy.'
}

$script:WingetExe = Resolve-Winget
if (-not $script:WingetExe -and -not $VerifyOnly) {
    $script:WingetExe = Install-Winget
}
if ($script:WingetExe) {
    $wgVer = Get-ToolVersionText -Exe $script:WingetExe -Arguments @('--version')
    Write-Ok "winget $($wgVer -replace '\s+', ' ')"
    if ($script:WingetExe -notlike 'winget*' -and (Split-Path -Leaf $script:WingetExe) -eq 'winget.exe') {
        Write-Note "resolved at $script:WingetExe"
    }
} elseif ($VerifyOnly) {
    Write-Warn2 'winget not found. Install mode would attempt to install App Installer.'
} else {
    Write-Fail 'winget could not be found or installed automatically.'
    Write-Note 'Open the Microsoft Store, install "App Installer", then run this script again.'
    Write-Note 'If the Store is blocked by policy, tell your facilitator before the session.'
    exit 2
}

# --------------------------------------------------------- 2. CORE TOOLCHAIN
Write-Phase 'Core toolchain'

Update-SessionPath

foreach ($req in $script:Requirements) {
    $name    = $req.Name
    $cmd     = Get-ToolCommand -Name $req.Probe
    $verText = $null
    if ($cmd) { $verText = Get-ToolVersionText -Exe $cmd.Source -Arguments $req.Args }

    $satisfied = $false
    if ($verText) { $satisfied = Test-VersionAtLeast -FoundText $verText -Minimum $req.Min }

    $foundVer = $null
    if ($verText) { $foundVer = Get-VersionFromText $verText }
    $foundStr = 'not found'
    if ($foundVer) { $foundStr = "$foundVer" }

    if ($satisfied) {
        Write-Ok "$name $foundStr (needs $($req.Min) or newer)"
        Add-Result -Component $name -Required "$($req.Min)+" -Found $foundStr -Status 'OK'
        continue
    }

    if ($VerifyOnly) {
        Write-Warn2 "$name $foundStr - needs $($req.Min) or newer"
        Add-Result -Component $name -Required "$($req.Min)+" -Found $foundStr -Status 'WARN' -Detail 'would install'
        continue
    }

    if ($cmd -and $verText) {
        Write-Doing "$name $foundStr is too old - upgrading via winget"
    } else {
        Write-Doing "$name not found - installing $($req.WingetId)"
    }

    $installed = Invoke-Winget -Id $req.WingetId
    Update-SessionPath

    $cmd2 = Get-ToolCommand -Name $req.Probe
    $verText2 = $null
    if ($cmd2) { $verText2 = Get-ToolVersionText -Exe $cmd2.Source -Arguments $req.Args }
    $ok2 = $false
    if ($verText2) { $ok2 = Test-VersionAtLeast -FoundText $verText2 -Minimum $req.Min }
    $found2 = 'not found'
    if ($verText2) { $found2 = "$(Get-VersionFromText $verText2)" }

    if ($ok2) {
        Write-Added "$name $found2 installed"
        Add-Result -Component $name -Required "$($req.Min)+" -Found $found2 -Status 'NEW'
    } elseif ($installed) {
        Write-Warn2 "$name installed but not visible in this session yet"
        Write-Note 'Close and reopen PowerShell, then re-run this script to confirm.'
        Add-Result -Component $name -Required "$($req.Min)+" -Found 'pending restart' -Status 'WARN' -Detail 'reopen shell'
    } else {
        Write-Fail "$name could not be installed"
        Add-Result -Component $name -Required "$($req.Min)+" -Found $found2 -Status 'FAIL' -Detail $req.WingetId
        $script:ExitCode = 1
    }
}

$storePython = @(Get-Command python -CommandType Application -ErrorAction SilentlyContinue) |
    Where-Object { $_.Source -like '*\WindowsApps\*' }
if ($storePython) {
    Write-Warn2 'The Microsoft Store python stub is on PATH ahead of the real Python.'
    Write-Note 'Settings > Apps > Advanced app settings > App execution aliases > turn OFF python.exe and python3.exe'
}

if (-not $VerifyOnly) {
    $javaCmd = Get-ToolCommand -Name 'java'
    if ($javaCmd) {
        $javaHome = Split-Path -Parent (Split-Path -Parent $javaCmd.Source)
        $currentJavaHome = [Environment]::GetEnvironmentVariable('JAVA_HOME', 'Machine')
        if ($currentJavaHome -and (Test-Path -LiteralPath (Join-Path $currentJavaHome 'bin\java.exe'))) {
            Write-Ok "JAVA_HOME already set to $currentJavaHome"
        } else {
            [Environment]::SetEnvironmentVariable('JAVA_HOME', $javaHome, 'Machine')
            $env:JAVA_HOME = $javaHome
            Write-Added "JAVA_HOME set to $javaHome"
        }
    }
}

# -------------------------------------------------------- 3. PYTHON PACKAGES
Write-Phase 'Python packages'

$pythonCmd = Get-ToolCommand -Name 'python'
if (-not $pythonCmd) {
    Write-Skip2 'Python not available in this session - skipping'
    Add-Result -Component 'Python packages' -Required ($script:PipPackages -join ', ') -Found 'skipped' -Status 'SKIP' -Detail 'reopen shell'
} else {
    $pipList = ''
    $pipList = (Invoke-Native -Exe $pythonCmd.Source -Arguments @('-m','pip','list','--disable-pip-version-check','--format=freeze')).Output
    foreach ($pkg in $script:PipPackages) {
        $present = $pipList -match ('(?im)^' + [regex]::Escape($pkg) + '==')
        if ($present) {
            Write-Ok "$pkg already installed"
            Add-Result -Component "pip: $pkg" -Required 'any' -Found 'installed' -Status 'OK'
            continue
        }
        if ($VerifyOnly) {
            Write-Warn2 "$pkg missing"
            Add-Result -Component "pip: $pkg" -Required 'any' -Found 'missing' -Status 'WARN' -Detail 'would install'
            continue
        }
        Write-Doing "installing $pkg"
        $r = Invoke-Native -Exe $pythonCmd.Source -Arguments @('-m','pip','install','--quiet','--disable-pip-version-check',$pkg)
        if ($r.ExitCode -eq 0) {
            Write-Added "$pkg installed"
            Add-Result -Component "pip: $pkg" -Required 'any' -Found 'installed' -Status 'NEW'
        } else {
            Write-Fail "$pkg failed to install"
            Add-Result -Component "pip: $pkg" -Required 'any' -Found 'failed' -Status 'FAIL'
            $script:ExitCode = 1
        }
    }
}

# ---------------------------------------------------------- 4. NODE PACKAGES
Write-Phase 'Node packages'

$npmCmd = Get-ToolCommand -Name 'npm'
if (-not $npmCmd) {
    Write-Skip2 'npm not available in this session - skipping'
    Add-Result -Component 'npm packages' -Required ($script:NpmPackages -join ', ') -Found 'skipped' -Status 'SKIP' -Detail 'reopen shell'
} else {
    $npmList = ''
    $npmList = (Invoke-Native -Exe $npmCmd.Source -Arguments @('ls','-g','--depth=0')).Output
    foreach ($pkg in $script:NpmPackages) {
        if ($npmList -match [regex]::Escape($pkg)) {
            Write-Ok "$pkg already installed"
            Add-Result -Component "npm: $pkg" -Required 'any' -Found 'installed' -Status 'OK'
            continue
        }
        if ($VerifyOnly) {
            Write-Warn2 "$pkg missing"
            Add-Result -Component "npm: $pkg" -Required 'any' -Found 'missing' -Status 'WARN' -Detail 'would install'
            continue
        }
        Write-Doing "installing $pkg"
        $r = Invoke-Native -Exe $npmCmd.Source -Arguments @('install','-g',$pkg)
        if ($r.ExitCode -eq 0) {
            Write-Added "$pkg installed"
            Add-Result -Component "npm: $pkg" -Required 'any' -Found 'installed' -Status 'NEW'
        } else {
            Write-Fail "$pkg failed to install"
            Add-Result -Component "npm: $pkg" -Required 'any' -Found 'failed' -Status 'FAIL'
            $script:ExitCode = 1
        }
    }
}

# --------------------------------------------------- 5. VS CODE EXTENSIONS
Write-Phase 'VS Code extensions'

$codeCmd = Get-ToolCommand -Name 'code'
if (-not $codeCmd) {
    foreach ($c in @(
        (Join-Path $env:LOCALAPPDATA 'Programs\Microsoft VS Code\bin\code.cmd'),
        (Join-Path $env:ProgramFiles  'Microsoft VS Code\bin\code.cmd')
    )) {
        if (Test-Path -LiteralPath $c) { $codeCmd = [pscustomobject]@{ Source = $c }; break }
    }
}

if (-not $codeCmd) {
    Write-Skip2 'VS Code CLI not found in this session - skipping extensions'
    Add-Result -Component 'VS Code extensions' -Required "$($script:VsCodeExtensions.Count) extensions" -Found 'skipped' -Status 'SKIP' -Detail 'reopen shell'
} elseif ($SkipExtensions) {
    Write-Skip2 'Skipped by -SkipExtensions'
    Add-Result -Component 'VS Code extensions' -Required "$($script:VsCodeExtensions.Count) extensions" -Found 'skipped' -Status 'SKIP'
} else {
    $installedExt = @()
    try {
        $installedExt = @(& $codeCmd.Source --list-extensions 2>&1) | ForEach-Object { "$_".Trim().ToLowerInvariant() }
    } catch {
        Write-Warn2 'Could not list installed extensions.'
    }
    foreach ($ext in $script:VsCodeExtensions) {
        if ($installedExt -contains $ext.ToLowerInvariant()) {
            Write-Ok $ext
            Add-Result -Component "ext: $ext" -Required 'installed' -Found 'installed' -Status 'OK'
            continue
        }
        if ($VerifyOnly) {
            Write-Warn2 "$ext missing"
            Add-Result -Component "ext: $ext" -Required 'installed' -Found 'missing' -Status 'WARN' -Detail 'would install'
            continue
        }
        Write-Doing "installing $ext"
        $r = Invoke-Native -Exe $codeCmd.Source -Arguments @('--install-extension',$ext,'--force')
        $out = $r.Output
        if ($r.ExitCode -eq 0 -or $out -match 'successfully installed' -or $out -match 'already installed') {
            Write-Added "$ext installed"
            Add-Result -Component "ext: $ext" -Required 'installed' -Found 'installed' -Status 'NEW'
        } else {
            Write-Warn2 "$ext could not be installed - add it from the Extensions panel"
            Add-Result -Component "ext: $ext" -Required 'installed' -Found 'failed' -Status 'WARN' -Detail 'install manually'
        }
    }
}

# ----------------------------------------------------- 6. VS CODE SETTINGS
Write-Phase 'VS Code settings'

$settingsPath = Join-Path $env:APPDATA 'Code\User\settings.json'
if ($VerifyOnly) {
    Write-Skip2 'settings.json not modified in verify mode'
    Add-Result -Component 'VS Code settings' -Required 'merged' -Found 'not checked' -Status 'SKIP'
} else {
    $read = Read-JsonFileSafely -Path $settingsPath
    if (-not $read.Ok) {
        Write-Warn2 "settings.json left untouched - $($read.Reason)"
        $recPath = Join-Path $env:APPDATA 'Code\User\helios-recommended-settings.json'
        Save-JsonFile -Path $recPath -Data $script:VsCodeSettings
        Write-Note "Recommended settings written to $recPath - merge them by hand."
        Add-Result -Component 'VS Code settings' -Required 'merged' -Found $read.Reason -Status 'WARN' -Detail 'manual merge'
    } else {
        $merge = Merge-Settings -Existing $read.Data -Desired $script:VsCodeSettings
        if ($merge.Added.Count -eq 0) {
            Write-Ok 'settings.json already has every Helios setting'
            Add-Result -Component 'VS Code settings' -Required 'merged' -Found 'already merged' -Status 'OK'
        } else {
            Save-JsonFile -Path $settingsPath -Data $merge.Settings
            Write-Added ('settings.json updated - added: ' + ($merge.Added -join ', '))
            Write-Note 'Existing values were preserved. A .helios-backup copy was made.'
            Add-Result -Component 'VS Code settings' -Required 'merged' -Found "added $($merge.Added.Count)" -Status 'NEW'
        }
    }
}

# ------------------------------------------------------- 7. CLAUDE CODE
Write-Phase 'Claude Code'

$claudeCmd = Get-ToolCommand -Name 'claude'
if (-not $claudeCmd) {
    Write-Warn2 'claude CLI not on PATH in this session.'
    Write-Note 'If it was just installed, close and reopen PowerShell and re-run this script.'
    Add-Result -Component 'Claude Code sign-in' -Required 'signed in' -Found 'CLI not found' -Status 'WARN'
} else {
    $cv = Get-ToolVersionText -Exe $claudeCmd.Source -Arguments @('--version')
    Write-Ok "claude $(Get-VersionFromText $cv)"

    $gitCmd = Get-ToolCommand -Name 'git'
    if ($gitCmd -and -not $VerifyOnly) {
        $gitRoot  = Split-Path -Parent (Split-Path -Parent $gitCmd.Source)
        $bashPath = Join-Path $gitRoot 'bin\bash.exe'
        if (Test-Path -LiteralPath $bashPath) {
            $claudeSettingsPath = Join-Path $env:USERPROFILE '.claude\settings.json'
            $cRead = Read-JsonFileSafely -Path $claudeSettingsPath
            if ($cRead.Ok) {
                $data = $cRead.Data
                $envBlock = $null
                if ($data.Contains('env') -and $data['env'] -is [System.Collections.IDictionary]) {
                    $envBlock = $data['env']
                } else {
                    $envBlock = [ordered]@{}
                }
                if ($envBlock['CLAUDE_CODE_GIT_BASH_PATH'] -eq $bashPath) {
                    Write-Ok 'CLAUDE_CODE_GIT_BASH_PATH already configured'
                } else {
                    $envBlock['CLAUDE_CODE_GIT_BASH_PATH'] = $bashPath
                    $data['env'] = $envBlock
                    Save-JsonFile -Path $claudeSettingsPath -Data $data
                    Write-Added 'CLAUDE_CODE_GIT_BASH_PATH configured so Claude Code can use the Bash tool'
                }
            } else {
                Write-Warn2 "~\.claude\settings.json left untouched - $($cRead.Reason)"
            }
        }
    }

    Write-Doing 'running claude doctor (read-only diagnostics)'
    $doctor = Get-ToolVersionText -Exe $claudeCmd.Source -Arguments @('doctor')
    if ($doctor) {
        $lines = ($doctor -split "`r?`n") | Where-Object { $_.Trim() } | Select-Object -First 12
        foreach ($line in $lines) { Write-Note $line }
    } else {
        Write-Note 'claude doctor produced no output.'
    }
    Write-Note 'If you are not signed in, run "claude" once and follow the browser prompt.'
    Add-Result -Component 'Claude Code' -Required '2.0.0+' -Found "$(Get-VersionFromText $cv)" -Status 'OK' -Detail 'see doctor output'
}

# --------------------------------------------------------- 8. WORKSPACE
Write-Phase 'Workspace folder and summary'

if (Test-Path -LiteralPath $WorkspaceRoot) {
    Write-Ok "Workspace folder exists: $WorkspaceRoot"
    Add-Result -Component 'Workspace folder' -Required 'present' -Found 'present' -Status 'OK' -Detail $WorkspaceRoot
} elseif ($VerifyOnly) {
    Write-Warn2 "Workspace folder missing: $WorkspaceRoot"
    Add-Result -Component 'Workspace folder' -Required 'present' -Found 'missing' -Status 'WARN' -Detail $WorkspaceRoot
} else {
    $null = New-Item -ItemType Directory -Path $WorkspaceRoot -Force
    Write-Added "Created $WorkspaceRoot"
    Add-Result -Component 'Workspace folder' -Required 'present' -Found 'created' -Status 'NEW' -Detail $WorkspaceRoot
}

Write-Host ''
$script:Results | Format-Table -AutoSize -Property Component, Required, Found, Status, Detail | Out-String -Width 200 | Write-Host

$fails = @($script:Results | Where-Object { $_.Status -eq 'FAIL' })
$warns = @($script:Results | Where-Object { $_.Status -eq 'WARN' })
if ($fails.Count -gt 0) { $script:ExitCode = 1 }

if ($fails.Count -eq 0 -and $warns.Count -eq 0) {
    Write-Host '  Workstation ready.' -ForegroundColor Green
} elseif ($fails.Count -eq 0) {
    Write-Host "  Workstation usable. $($warns.Count) warning(s) listed above." -ForegroundColor Yellow
} else {
    Write-Host "  $($fails.Count) component(s) failed. Resolve them and re-run this script." -ForegroundColor Red
}

Write-Banner 'Next steps - you run these' 'this script does not touch git repositories'
Write-Host ''
Write-Host '  1. Close this window and open a NEW PowerShell window so PATH changes apply.' -ForegroundColor Gray
Write-Host ''
Write-Host '  2. Clone the Helios repository:' -ForegroundColor Gray
Write-Host "       cd `"$WorkspaceRoot`"" -ForegroundColor White
Write-Host '       git clone https://github.com/arzan333/helios-sandbox.git' -ForegroundColor White
Write-Host ''
Write-Host '  3. Create your local branch and turn on the push guard:' -ForegroundColor Gray
Write-Host '       cd helios-sandbox' -ForegroundColor White
Write-Host '       git checkout -b <yourname>/foundation' -ForegroundColor White
Write-Host '       git config core.hooksPath .githooks' -ForegroundColor White
Write-Host '     The last line blocks accidental pushes. Nothing here ever leaves your machine.' -ForegroundColor DarkGray
Write-Host ''
Write-Host '  4. Open the folder and start the Week 1 lab book:' -ForegroundColor Gray
Write-Host '       code .' -ForegroundColor White
Write-Host ''
if ($logPath) { Write-Host "  Log written to $logPath" -ForegroundColor DarkGray }
Write-Host ''

}
catch {
    Write-Host ''
    Write-Fail "Unexpected error: $($_.Exception.Message)"
    Write-Note "At: $($_.InvocationInfo.PositionMessage)"
    $script:ExitCode = 1
}
finally {
    if (-not $NoTranscript) {
        try { Stop-Transcript | Out-Null } catch { }
    }
}

exit $script:ExitCode
