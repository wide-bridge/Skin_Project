param(
    [string]$PythonExe = "D:\anaconda3\envs\skin_vlm\python.exe",
    [string]$TrainScript = "D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\scripts\train_frontal_classifier.py",
    [string]$OutputDir = "D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed",
    [string]$ConfigPath = "",
    [string]$TaskName = "SkinDiagnosisTrainBackground"
)

$ErrorActionPreference = "Stop"

# Some Windows sessions can contain both PATH and Path. PowerShell/.NET treats
# those as duplicate environment keys. Clean this process before generating the
# scheduled runner.
$env:PATH = $null
[Environment]::SetEnvironmentVariable(
    "Path",
    "D:\anaconda3\envs\skin_vlm;D:\anaconda3\envs\skin_vlm\Scripts;D:\anaconda3\condabin;D:\anaconda3\Library\bin;D:\anaconda3\Scripts;D:\anaconda3;$env:SystemRoot\system32;$env:SystemRoot;$env:SystemRoot\System32\Wbem",
    "Process"
)

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Force -Path "C:\tmp" | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$stdoutPath = Join-Path $OutputDir ("train_bg_" + $timestamp + ".out.log")
$stderrPath = Join-Path $OutputDir ("train_bg_" + $timestamp + ".err.log")
$pidPath = Join-Path $OutputDir "train_background.pid"
$metaPath = Join-Path $OutputDir "train_background_meta.json"
$runnerPath = "C:\tmp\skin_diag_train.cmd"
$configLine = ""
if ($ConfigPath) {
    if (-not (Test-Path -LiteralPath $ConfigPath)) {
        throw "ConfigPath does not exist: $ConfigPath"
    }
    $configLine = "set `"SKIN_DIAGNOSIS_CONFIG=$ConfigPath`""
}

$runner = @"
@echo off
cd /d D:\vibe_coding\codex\Skin_Project
set "PATH=D:\anaconda3\envs\skin_vlm;D:\anaconda3\envs\skin_vlm\Scripts;D:\anaconda3\condabin;D:\anaconda3\Library\bin;D:\anaconda3\Scripts;D:\anaconda3;%SystemRoot%\system32;%SystemRoot%;%SystemRoot%\System32\Wbem"
set "PYTHONIOENCODING=utf-8"
$configLine
"$PythonExe" "$TrainScript" 1>>"$stdoutPath" 2>>"$stderrPath"
"@

Set-Content -Path $runnerPath -Value $runner -Encoding ASCII

& "C:\Windows\System32\cmd.exe" /d /c "schtasks /Delete /TN $TaskName /F >nul 2>nul" | Out-Null
& "C:\Windows\System32\schtasks.exe" /Create /TN $TaskName /SC ONCE /ST 23:59 /TR $runnerPath /F | Out-Null
& "C:\Windows\System32\schtasks.exe" /Run /TN $TaskName | Out-Null

Set-Content -Path $pidPath -Value "SCHEDULED_TASK" -Encoding ascii

$pathKeys = [System.Environment]::GetEnvironmentVariables("Process").GetEnumerator() |
    Where-Object { ([string]$_.Key) -match "^(Path|PATH)$" } |
    ForEach-Object { [string]$_.Key }

$meta = @{
    pid = "SCHEDULED_TASK"
    started_at = (Get-Date).ToString("s")
    stdout_log = $stdoutPath
    stderr_log = $stderrPath
    python_exe = $PythonExe
    train_script = $TrainScript
    config_path = $ConfigPath
    launcher = "schtasks -> short cmd runner"
    task_name = $TaskName
    runner_cmd = $runnerPath
    env_fix = "cleared duplicate uppercase PATH before schtasks"
    path_keys_before_launch = @($pathKeys)
} | ConvertTo-Json -Depth 4

Set-Content -Path $metaPath -Value $meta -Encoding UTF8

Write-Output ("STARTED_TASK=" + $TaskName)
Write-Output ("RUNNER_CMD=" + $runnerPath)
Write-Output ("STDOUT_LOG=" + $stdoutPath)
Write-Output ("STDERR_LOG=" + $stderrPath)
