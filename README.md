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

## 5. Installation and Setup

Open PowerShell in the project root directory.

### Step 1: Clone the repository

```powershell
git clone https://github.com/codexprashantpawar/AI-Gatekeeper.git

cd AI-Gatekeeper
```

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

### Step 3: Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 4: Install dependencies

```powershell
python -m pip install --upgrade pip

pip install -r requirements.txt
```

### Step 5: Configure environment variables

Create your local `.env` file using the example configuration:

```powershell
Copy-Item .env.example .env
```

Update the configuration with your actual values, including:

- `PLATE_WEIGHTS` — path to your local license plate model weights.
- `CAMERA_URL` — camera or phone camera stream URL.

**Important:** Keep `.env` and private credentials out of GitHub.

## 6. Running the Project

Run these commands from the project root directory with the virtual environment activated.

### Check environment and configuration

```powershell
python scripts/check_env.py
```

### Process live camera frames

```powershell
python scripts/run_phone.py --frames 30
```

This processes up to 30 frames from the configured phone camera stream.

### Process images from a directory

```powershell
python scripts/run_images.py C:\test_images
```

Replace `C:\test_images` with your actual image directory.

### Run automated tests

```powershell
pytest tests
```

## 7. Evidence Generation

The system stores generated evidence under the following directory structure:

```text
output/
└── <event_id>/
    ├── original.jpg
    ├── annotated.jpg
    ├── crops/
    │   └── plate_*.jpg
    └── event.json
```

The evidence includes:

- **Original image:** Input image or camera frame.
- **Annotated image:** Image containing detection annotations.
- **Cropped plates:** Cropped license plate regions.
- **Event JSON:** Structured event information.

Generated evidence is stored locally and is not intended to be committed to the Git repository.

## 8. Current Limitations

This milestone focuses on the initial computer vision pipeline.

The following capabilities are outside the current implementation scope:

- License plate text recognition (OCR).
- Face detection and recognition.
- Database persistence.
- Web-based monitoring dashboard.
- User authentication and authorization.
- Complete gate access-control automation.

These capabilities may be considered in future milestones.

## 9. Development Roadmap

The project will evolve incrementally toward a complete AI-powered gate security system.

Future development areas may include:

1. License plate OCR and text extraction.
2. Structured event management.
3. Database integration.
4. Real-time monitoring dashboard.
5. Event history and search.
6. Access-control workflows.
7. Production deployment and monitoring.

## 10. Repository

**GitHub:** https://github.com/codexprashantpawar/AI-Gatekeeper

---

**Project:** AI Gatekeeper  
**Milestone:** 1 (Phase 1–2)  
**Status:** Initial computer vision pipeline development
