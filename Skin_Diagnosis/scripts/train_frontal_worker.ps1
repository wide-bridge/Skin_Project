param(
    [string]$PythonExe = "D:\anaconda3\envs\skin_vlm\python.exe",
    [string]$TrainScript = "D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\scripts\train_frontal_classifier.py",
    [string]$OutputDir = "D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed",
    [string]$ConfigPath = ""
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
Set-Location "D:\vibe_coding\codex\Skin_Project"

$env:PATH = "D:\anaconda3\envs\skin_vlm;D:\anaconda3\envs\skin_vlm\Scripts;D:\anaconda3\condabin;D:\anaconda3\Library\bin;D:\anaconda3\Scripts;D:\anaconda3;$env:SystemRoot\system32;$env:SystemRoot;$env:SystemRoot\System32\Wbem"
$env:PYTHONIOENCODING = "utf-8"
if ($ConfigPath) {
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        throw "ConfigPath does not exist: $ConfigPath"
    }
    $env:SKIN_DIAGNOSIS_CONFIG = $ConfigPath
}

& $PythonExe $TrainScript
