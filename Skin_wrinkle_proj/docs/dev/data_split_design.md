# Data and Split Design

## External Data Policy
- Original images and JSON labels remain outside `Skin_Project`.
- This project references external roots through a local config file.
- ROI crops are derived artifacts and should be written outside the repository when materialized.

## Target Definition
- Current target: `annotations.forehead_wrinkle`
- Source label file: facepart `1` JSON (`*_01.json`)
- Source image: `info.filename` inside the matching scenario/id folder

## Manifest Row Design
Each usable sample records:
- `scenario`
- `subject_id`
- `person_key`
- `image_filename`
- `image_path`
- `label_path`
- `forehead_wrinkle`
- `bbox`
- `roi_available`
- `angle_token`
- `width`, `height`

## ROI Policy
- Prefer forehead ROI crop from `images.bbox`
- Validate bbox bounds against image width/height
- If bbox is invalid or missing, record that explicitly in the validation report
- Training can either skip invalid ROI samples or fall back to full image according to config

## Split Policy
### Loose Split
- Random sample-level split
- Used to estimate an easy upper bound and memorization tendency

### Strict Split
- Group split by `person_key`
- No same-person overlap across train/val/test
- Used as the main interpretation split

## Leakage Checks
- person-key intersection across split partitions
- duplicate filename or duplicate image path overlap
- count of per-person images across scenarios and angles

## Output Artifacts
- `outputs/reports/data_validation_report.md`
- `outputs/reports/loose_split.json`
- `outputs/reports/strict_split.json`
- `outputs/metrics/label_distribution_forehead_wrinkle.csv`
