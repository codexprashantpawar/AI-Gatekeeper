# AI Gate Security - Milestone 1 (Phase 1-2)

Models: Hugging Face RT-DETR (vehicles + animals, COCO) + your cloned HF plate detector (`best.pt`).
Plate is detected and cropped only (no OCR). No face, DB or UI yet.

## Setup (PowerShell, in this folder)
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Copy-Item .env.example .env      # then edit PLATE_WEIGHTS and CAMERA_URL

## Run
    python scripts\check_env.py
    python scripts\run_phone.py --frames 30
    python scripts\run_images.py C:\test_images
    pytest tests

Evidence goes to `output\<event_id>\` (original, annotated, crops, event.json).
