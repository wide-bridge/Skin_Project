param(
    [string]$OutputDir = "D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed"
)

$ErrorActionPreference = "Stop"

$pidPath = Join-Path $OutputDir "train_background.pid"
$metaPath = Join-Path $OutputDir "train_background_meta.json"

if (-not (Test-Path -LiteralPath $pidPath)) {
    Write-Output "NO_PID_FILE"
    exit 0
}

$pidValue = Get-Content -Path $pidPath -Raw
$marker = $pidValue.Trim()

if ($marker -eq "SCHEDULED_TASK") {
    $meta = $null
    if (Test-Path -LiteralPath $metaPath) {
        $meta = Get-Content -Path $metaPath -Raw | ConvertFrom-Json
    }

    if ($meta -and $meta.task_name) {
        $taskInfo = & "C:\Windows\System32\schtasks.exe" /Query /TN $meta.task_name /FO LIST /V 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Output ("SCHEDULED_TASK_FOUND=" + $meta.task_name)
            $taskInfo
        } else {
            Write-Output ("SCHEDULED_TASK_MISSING=" + $meta.task_name)
        }
    } else {
        Write-Output "SCHEDULED_TASK_NO_META"
    }
} else {
    $targetPid = [int]$marker
    $proc = Get-Process -Id $targetPid -ErrorAction SilentlyContinue

    if ($proc) {
        Write-Output ("RUNNING_PID=" + $targetPid)
    } else {
        Write-Output ("NOT_RUNNING_PID=" + $targetPid)
    }
}

if (Test-Path -LiteralPath $metaPath) {
    Get-Content -Path $metaPath -Raw
}
