param(
    [string]$TrainingRoot = "D:\vibe_coding\codex\DocTalk\Derma_AI\face_derma_data\face_derma_data\Training",
    [string]$ValidationRoot = "D:\vibe_coding\codex\DocTalk\Derma_AI\face_derma_data\face_derma_data\Validation",
    [string]$OutputDir = "D:\vibe_coding\codex\Skin_Project\Skin_Diagnosis\data\processed",
    [string]$ReferenceManifest = "D:\vibe_coding\codex\Skin_Project\Skin_diagnosis_proj\data\processed\image_manifest.csv",
    [double]$TrainRatio = 0.8,
    [switch]$IncludeSideView
)

$ErrorActionPreference = "Stop"

function Get-FieldValue {
    param(
        [string]$RawText,
        [string]$FieldName
    )

    $pattern = '"{0}"\s*:\s*"([^"]+)"' -f [regex]::Escape($FieldName)
    $match = [regex]::Match($RawText, $pattern)
    if ($match.Success) {
        return $match.Groups[1].Value
    }

    return ""
}

function Get-ReferenceLookup {
    param([string]$ManifestPath)

    $lookup = @{}
    if (-not (Test-Path -LiteralPath $ManifestPath)) {
        return $lookup
    }

    $rows = Import-Csv -Path $ManifestPath
    foreach ($row in $rows) {
        if (-not $row.image_path) {
            continue
        }

        $lookup[$row.image_path] = [PSCustomObject]@{
            canonical_label = $row.canonical_label
            source_label = $row.source_label
            view = $row.view
        }
    }

    return $lookup
}

function Add-DatasetRecords {
    param(
        [string]$DatasetRoot,
        [string]$SourcePrefix,
        [string]$LabelPrefix,
        [string]$SplitName,
        [System.Collections.Generic.List[object]]$Records,
        [hashtable]$ReferenceLookup,
        [switch]$IncludeSideView
    )

    $sourceRoot = Join-Path $DatasetRoot "source_data"
    $labelRoot = Join-Path $DatasetRoot "label_data"

    if (-not (Test-Path -LiteralPath $sourceRoot)) {
        throw "Missing source_data directory: $sourceRoot"
    }

    if (-not (Test-Path -LiteralPath $labelRoot)) {
        throw "Missing label_data directory: $labelRoot"
    }

    $sourceDirs = Get-ChildItem -Path $sourceRoot -Directory | Where-Object {
        $_.Name -like ($SourcePrefix + "_*")
    }

    foreach ($sourceDir in $sourceDirs) {
        $parts = $sourceDir.Name.Split("_")
        if ($parts.Count -lt 3) {
            continue
        }

        $rawView = $parts[-1]
        $sourceLabel = ($parts[1..($parts.Count - 2)] -join "_")
        $labelDirName = "{0}_{1}_{2}" -f $LabelPrefix, $sourceLabel, $rawView
        $labelDir = Join-Path $labelRoot $labelDirName

        if (-not (Test-Path -LiteralPath $labelDir)) {
            Write-Warning "Missing matching label directory: $labelDir"
            continue
        }

        $images = Get-ChildItem -Path $sourceDir.FullName -File -Filter *.png
        foreach ($image in $images) {
            $imageId = [System.IO.Path]::GetFileNameWithoutExtension($image.Name)
            $labelPath = Join-Path $labelDir ($imageId + ".json")
            $labelExists = Test-Path -LiteralPath $labelPath

            $reference = $null
            if ($ReferenceLookup.ContainsKey($image.FullName)) {
                $reference = $ReferenceLookup[$image.FullName]
            }

            $canonicalLabel = if ($reference) { $reference.canonical_label } else { "unknown" }
            $normalizedView = if ($reference) { $reference.view } else { $rawView }

            if (-not $IncludeSideView -and $normalizedView -ne "frontal") {
                continue
            }

            $ageRange = ""
            $diagnosisNameRaw = ""
            $hasLesionAreaPath = $false

            if ($labelExists) {
                $raw = Get-Content -Path $labelPath -Raw
                $ageRange = Get-FieldValue -RawText $raw -FieldName "age_range"
                $diagnosisNameRaw = Get-FieldValue -RawText $raw -FieldName "diagnosis_name"
                $hasLesionAreaPath = $raw -match '"lesion_area"\s*:'
            }

            $Records.Add([PSCustomObject]@{
                image_id = $imageId
                image_path = $image.FullName
                label_path = $labelPath
                dataset_root = $DatasetRoot
                source_label_ko = $sourceLabel
                canonical_label = $canonicalLabel
                view = $normalizedView
                raw_view = $rawView
                split = $SplitName
                label_exists = $labelExists
                age_range = if ($ageRange) { $ageRange } else { "unknown" }
                diagnosis_name_raw = $diagnosisNameRaw
                lesion_area_path_declared = $hasLesionAreaPath
            }) | Out-Null
        }
    }
}

function Set-InternalTrainValSplit {
    param(
        [System.Collections.Generic.List[object]]$Records,
        [double]$TrainRatio
    )

    $trainingRecords = @($Records | Where-Object { $_.split -eq "train" })
    $validationRecords = @($Records | Where-Object { $_.split -eq "val" })

    foreach ($record in $validationRecords) {
        $record.split = "test"
    }

    $groups = $trainingRecords | Group-Object canonical_label
    foreach ($group in $groups) {
        $items = @($group.Group | Sort-Object image_id)
        $trainCount = [int][Math]::Floor($items.Count * $TrainRatio)

        for ($i = 0; $i -lt $items.Count; $i++) {
            if ($i -lt $trainCount) {
                $items[$i].split = "train"
            } else {
                $items[$i].split = "val"
            }
        }
    }
}

New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$records = New-Object System.Collections.Generic.List[object]
$referenceLookup = Get-ReferenceLookup -ManifestPath $ReferenceManifest

Add-DatasetRecords -DatasetRoot $TrainingRoot -SourcePrefix "TS" -LabelPrefix "TL" -SplitName "train" -Records $records -ReferenceLookup $referenceLookup -IncludeSideView:$IncludeSideView
Add-DatasetRecords -DatasetRoot $ValidationRoot -SourcePrefix "VS" -LabelPrefix "VL" -SplitName "val" -Records $records -ReferenceLookup $referenceLookup -IncludeSideView:$IncludeSideView

Set-InternalTrainValSplit -Records $records -TrainRatio $TrainRatio

$manifestPath = Join-Path $OutputDir "lesion_manifest.csv"
$records |
    Sort-Object split, canonical_label, image_id |
    Export-Csv -Path $manifestPath -NoTypeInformation -Encoding UTF8

$summary = [PSCustomObject]@{
    training_root = $TrainingRoot
    validation_root = $ValidationRoot
    include_side_view = [bool]$IncludeSideView
    split_policy = @{
        training_root_split = "train_val_by_label"
        train_ratio = $TrainRatio
        validation_root_split = "test"
    }
    generated_at = (Get-Date).ToString("s")
    total_samples = $records.Count
    labels = @(
        $records |
            Group-Object canonical_label |
            Sort-Object Name |
            ForEach-Object {
                [PSCustomObject]@{
                    canonical_label = $_.Name
                    count = $_.Count
                }
            }
    )
    views = @(
        $records |
            Group-Object view |
            Sort-Object Name |
            ForEach-Object {
                [PSCustomObject]@{
                    view = $_.Name
                    count = $_.Count
                }
            }
    )
    splits = @(
        $records |
            Group-Object split |
            Sort-Object Name |
            ForEach-Object {
                [PSCustomObject]@{
                    split = $_.Name
                    count = $_.Count
                }
            }
    )
    label_file_coverage = @{
        present = @($records | Where-Object { $_.label_exists }).Count
        missing = @($records | Where-Object { -not $_.label_exists }).Count
    }
    lesion_area_path_declared = @{
        present = @($records | Where-Object { $_.lesion_area_path_declared }).Count
        missing = @($records | Where-Object { -not $_.lesion_area_path_declared }).Count
    }
} | ConvertTo-Json -Depth 6

$summaryPath = Join-Path $OutputDir "dataset_summary.json"
Set-Content -Path $summaryPath -Value $summary -Encoding UTF8

Write-Output "Manifest written to: $manifestPath"
Write-Output "Summary written to: $summaryPath"
Write-Output ("Total samples: {0}" -f $records.Count)
