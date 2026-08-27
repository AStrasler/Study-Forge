# OCR and file formats

Study Forge extracts **text** from materials, then runs the agent / pack pipeline.

## Supported now

| Format | How |
|--------|-----|
| PDF (text layer) | PyMuPDF, then pypdf |
| PDF (scanned / image-heavy) | Render pages → **Tesseract OCR** |
| PNG, JPG, JPEG, WEBP, TIF, BMP, GIF | **Tesseract OCR** |
| DOCX | python-docx |
| PPTX | python-pptx |
| TXT, MD | raw read |
| XLSX / XLSM | openpyxl |
| XLS (legacy) | optional `xlrd` |

MP3 / audio still needs a speech-to-text step (next).

## Deepnote system package (required for OCR)

In a Deepnote terminal **once per machine image**:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr
```

Python deps (repo root):

```bash
pip install -r requirements.txt
pip install -r deepnote/requirements-engine.txt
```

## Behavior

- Digital PDFs with enough text skip OCR (faster).
- Thin text (under ~80 characters) triggers OCR on up to **40** pages.
- Failures log warnings; extraction returns whatever text was available.

## Local (optional)

Windows: install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and ensure `tesseract` is on `PATH`.
