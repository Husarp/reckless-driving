# Builds build\RecklessDrivingSetup.exe (and the program folder build\dist\RecklessDriving).
#   1. check app\version.py matches the game's own GAME_VERSION, so the two can never drift
#   2. RecklessDriving.exe (PyInstaller, installer\game.spec)
#   3. self-test: the built exe starts HIDDEN and checks the game boots, the embedded fonts are
#      available offline and localStorage is writable (skip with -NoSelfTest)
#   4. RecklessDrivingSetup.exe = the setup program with the program folder zipped inside it
# No admin needed, at build time or install time. Run from any folder:
#   & "<project folder>\scripts\build.ps1"
param([switch]$NoSelfTest)
$ErrorActionPreference = "Continue"   # (PyInstaller writes progress to stderr; failures checked below)
$Root = Split-Path -Parent $PSScriptRoot
$Py = "$Root\.venv\Scripts\python.exe"
$Build = "$Root\build"
Set-Location $Root

if (-not (Test-Path $Py)) { throw "No virtualenv at $Py - create it with: python -m venv .venv" }

# 1. version agreement. A packaged build claiming a different version than the game shows in its
# own menu is exactly the kind of quiet drift this project keeps getting bitten by.
$appVersion = (Select-String -Path "$Root\app\version.py" -Pattern 'VERSION\s*=\s*"([^"]+)"').Matches[0].Groups[1].Value
$gameVersion = (Select-String -Path "$Root\carCrash.html" -Pattern "GAME_VERSION\s*=\s*'([^']+)'").Matches[0].Groups[1].Value
if ($appVersion -ne $gameVersion) {
    throw "Version mismatch: app\version.py says $appVersion, carCrash.html says $gameVersion"
}
Write-Output "Building $appVersion"

# The game must not need the network for its fonts once packaged.
if (Select-String -Path "$Root\carCrash.html" -Pattern "fonts\.(googleapis|gstatic)\.com" -Quiet) {
    throw "carCrash.html still references Google Fonts - run: python tools\embed_fonts.py"
}

# Clear the build stamp before anything in build\ is touched. If the build then fails partway,
# the dashboard sees no stamp at all rather than last run's version sitting next to this run's
# half-replaced files.
Remove-Item "$Build\BUILT.json" -ErrorAction SilentlyContinue

# 2. the game
& $Py -m PyInstaller --noconfirm --log-level WARN --distpath "$Build\dist" --workpath "$Build\work" installer\game.spec
if ($LASTEXITCODE) { throw "Building the game failed" }

# 3. self-test
if (-not $NoSelfTest) {
    $report = "$Build\selftest.txt"
    Remove-Item $report -ErrorAction SilentlyContinue
    Start-Process "$Build\dist\RecklessDriving\RecklessDriving.exe" -ArgumentList "--selftest", "`"$report`"" -Wait
    $result = (Get-Content $report -Raw -ErrorAction SilentlyContinue)
    if (-not $result -or -not $result.StartsWith("OK")) { throw "Self-test failed:`n$result" }
    Write-Output "Self-test: $($result.Trim())"
}

# 4. the installer, with the program folder zipped inside it
$zip = "$Build\payload.zip"
Remove-Item $zip -ErrorAction SilentlyContinue
Compress-Archive -Path "$Build\dist\RecklessDriving\*" -DestinationPath $zip -CompressionLevel Optimal -ErrorAction Stop

& $Py -m PyInstaller --noconfirm --log-level WARN --onefile --noconsole --name RecklessDrivingSetup `
    --icon "$Root\assets\recklessdriving.ico" --paths "$Root\app" `
    --add-data "$zip;." --add-data "$Root\assets\recklessdriving.ico;." `
    --distpath $Build --workpath "$Build\work-setup" --specpath "$Build\work-setup" installer\setup.py
if ($LASTEXITCODE) { throw "Building the installer failed" }

$size = "{0:N0}" -f ((Get-Item "$Build\RecklessDrivingSetup.exe").Length / 1MB)
Write-Output "Built $Build\RecklessDrivingSetup.exe ($size MB)"

# 5. build stamp for the dev-status dashboard. It can see build\ and when the files were made,
# but not WHICH version made them - this records that. Last statement in the script on purpose:
# every failure above is a throw, so reaching this line means the build genuinely succeeded.
$built = [ordered]@{
    version   = $appVersion
    builtAt   = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    artifacts = @([ordered]@{ name = "RecklessDrivingSetup.exe"; kind = "Windows" })
}
# WriteAllText, not Out-File: .NET writes UTF-8 with no BOM, which strict JSON readers need.
[System.IO.File]::WriteAllText("$Build\BUILT.json", ($built | ConvertTo-Json -Depth 3))
Write-Output "Wrote $Build\BUILT.json ($appVersion)"
