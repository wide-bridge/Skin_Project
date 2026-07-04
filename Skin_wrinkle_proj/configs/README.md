# Config Notes

Published config files in this directory are GitHub-safe templates.

Required environment variables:

- `SKIN_DATA_IMAGE_ROOT`: source image root
- `SKIN_DATA_LABEL_ROOT`: source label root
- `SKIN_CROP_ROOT`: pre-cropped ROI root for precrop experiments
- `SKIN_EXTERNAL_CROP_ROOT`: optional external crop root used by baseline templates

Default relative output directories:

- `outputs`
- `checkpoints`
- `logs`

Example (PowerShell):

```powershell
$env:SKIN_DATA_IMAGE_ROOT="D:/path/to/dataset/img"
$env:SKIN_DATA_LABEL_ROOT="D:/path/to/dataset/label"
$env:SKIN_CROP_ROOT="D:/path/to/skin_crop_data"
python .\scripts\run_fw07_strict_only.py --config .\configs\forehead_wrinkle_fw07_v2s_tuned.yaml
```
