# AI Gatekeeper

**AI-Powered Gate Security System — Milestone 1 (Phase 1–2)**

AI Gatekeeper is a Python-based computer vision project designed to detect vehicles, animals, and vehicle license plates from camera frames or input images.

The current milestone focuses on camera input, object detection, license plate detection, image processing, and evidence generation.

## 1. Project Overview

The system currently uses two computer vision models:

- **Hugging Face RT-DETR:** Detects vehicles and animals using the COCO object detection dataset.
- **License Plate Detector:** Uses a locally stored, cloned Hugging Face model checkpoint (`best.pt`) to detect vehicle license plates.

Detected license plates are cropped and saved as evidence. OCR (Optical Character Recognition) is not implemented yet.

### Current Scope

| Feature | Status |
|---|---|
| Camera frame acquisition | Implemented |
| Vehicle detection | Implemented |
| Animal detection | Implemented |
| License plate detection | Implemented |
| License plate cropping | Implemented |
| Annotated image generation | Implemented |
| Evidence storage | Implemented |
| Event JSON generation | Implemented |
| License plate OCR | Not implemented |
| Face detection | Not implemented |
| Database integration | Not implemented |
| Web UI / Dashboard | Not implemented |

## 2. Technology Stack

- **Language:** Python
- **Object Detection:** Hugging Face RT-DETR
- **License Plate Detection:** Custom / cloned Hugging Face detector
- **Computer Vision:** OpenCV
- **Model Weights:** Local `best.pt` checkpoint
- **Configuration:** Environment variables (`.env`)
- **Testing:** Pytest

## 3. Project Structure

```text
gate_ai/
│
├── app/
│   ├── detectors/
│   │   ├── hf_objects.py
│   │   └── plate.py
│   │
│   ├── __init__.py
│   ├── camera.py
│   ├── config.py
│   ├── evidence.py
│   ├── pipeline.py
│   └── types.py
│
├── scripts/
│   ├── check_env.py
│   ├── live_view.py
│   ├── run_images.py
│   └── run_phone.py
│
├── tests/
│   └── test_logic.py
│
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## 4. Prerequisites

Before running the project, ensure you have:

- Python installed.
- Git installed.
- A compatible camera or phone camera stream URL (for live camera processing).
- Access to the required model weights.
- Internet access when downloading model dependencies or model files for the first time.

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
