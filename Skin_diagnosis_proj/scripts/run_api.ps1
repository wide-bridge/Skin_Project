$env:PYTHONPATH = "D:\vibe_coding\codex\Skin_Project\Skin_diagnosis_proj"
python -m uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --reload

