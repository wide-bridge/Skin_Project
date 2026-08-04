param(
    [string]$OutputDir = "D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed"
)

$ErrorActionPreference = "Stop"

$pidPath = Join-Path $OutputDir "train_background.pid"

if (-not (Test-Path -LiteralPath $pidPath)) {
    Write-Output "NO_PID_FILE"
    exit 0
}

$pidValue = Get-Content -Path $pidPath -Raw
$marker = $pidValue.Trim()

if ($marker -eq "SCHEDULED_TASK") {
    $meta = $null
    if (Test-Path -LiteralPath (Join-Path $OutputDir "train_background_meta.json")) {
        $meta = Get-Content -LiteralPath (Join-Path $OutputDir "train_background_meta.json") -Raw | ConvertFrom-Json
    }

    if ($meta -and $meta.task_name) {
        & "C:\Windows\System32\schtasks.exe" /End /TN $meta.task_name 2>$null | Out-Null
        & "C:\Windows\System32\schtasks.exe" /Delete /TN $meta.task_name /F 2>$null | Out-Null
        Write-Output ("STOPPED_TASK=" + $meta.task_name)
    } else {
        Write-Output "SCHEDULED_TASK_NO_META"
    }
} else {
    $targetPid = [int]$marker
    $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue

    if ($proc) {
        Stop-Process -Id $targetPid -Force
        Write-Output ("STOPPED_PID=" + $targetPid)
    } else {
        Write-Output ("NOT_RUNNING_PID=" + $targetPid)
    }
}
