# Microfilm Quality Test Software

## Overview

This document describes a proposed Python-based system for automated comparison and quality assessment between:

1. **Original digital documents** (PDF format)
2. **Recreated microfilm scans** (obtained from physical microfilm, scanned and exported as PDF, TIFF, PNG, or JPEG)

The goal is to **automatically evaluate** how closely the microfilm reproduction matches the original, in terms of visual fidelity, legibility, and content integrity.

---

## Objectives

- Extract and normalize pages from both original and microfilm versions.
- Compare the two versions using **image processing** and **text-based metrics**.
- Generate a **quality score** and **visual report** highlighting differences.
- Support multiple input formats (PDF, TIFF, PNG, JPG).
- Allow configurable thresholds for quality tolerance.

---

## System Architecture

### 1. Input Layer

| Input | Description | Tools/Libraries |
|-------|--------------|----------------|
| Original document | Always a PDF (digital source) | `PyMuPDF` (`fitz`) or `pdf2image` |
| Microfilm scan | Can be PDF, TIFF, PNG, or JPG | `pdf2image`, `Pillow`, or `OpenCV` |

Both will be converted into **normalized image sequences** for direct comparison.

---

### 2. Preprocessing Pipeline

Steps to ensure fair and standardized comparison:

1. **PDF to Image Conversion**  
   - Convert all pages to images (e.g., PNG at 300–600 DPI).  
   - Tools: `pdf2image`, `fitz`.

2. **Grayscale Conversion**  
   - Convert color to grayscale for simplicity.  
   - `cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)`

3. **Image Normalization**  
   - Resize both images to the same resolution.  
   - Deskew using OpenCV’s `cv2.minAreaRect` or `cv2.HoughLines`.  
   - Apply contrast normalization or adaptive histogram equalization.  
   - Example: `cv2.equalizeHist(gray_img)`

4. **Noise Reduction (Optional)**  
   - Use median filtering or Gaussian blur to smooth scanning artifacts.  
   - `cv2.GaussianBlur(gray_img, (3, 3), 0)`

---

### 3. Comparison Layer

Two main comparison approaches can be applied:

#### A. Visual / Image-Based Comparison

1. **Structural Similarity Index (SSIM)**  
   - Measures perceptual similarity between two images.  
   - From `skimage.metrics import structural_similarity`.  
   - Output: SSIM score (0–1) and difference heatmap.

2. **Pixel-Level Difference Map**  
   - Compute absolute difference using OpenCV:  
     ```python
     diff = cv2.absdiff(img1, img2)
     ```
   - Apply thresholding to highlight significant deviations.

3. **Feature-Based Matching (Optional)**  
   - Use ORB/SIFT features to detect shifts or distortions.  
   - Compare keypoint matching accuracy.

#### B. OCR / Text-Based Comparison

1. **Optical Character Recognition (OCR)**  
   - Run Tesseract OCR (`pytesseract`) on both original and microfilm pages.
   - Output plain text for each page.

2. **Text Normalization**  
   - Remove whitespace, punctuation, and normalize casing.

3. **Text Similarity Metrics**  
   - Use string similarity algorithms:
     - **Levenshtein distance**
     - **Cosine similarity** on TF-IDF vectors
   - Tools: `fuzzywuzzy`, `difflib`, `sklearn.feature_extraction.text`.

4. **Character/Word Error Rate**  
   - Compute CER and WER to assess OCR degradation.

---

### 4. Quality Scoring & Reporting

Each page (and optionally the whole document) will receive a **Quality Score** based on weighted criteria:

| Metric | Description | Weight |
|---------|--------------|--------|
| SSIM | Structural similarity | 0.5 |
| OCR Text Similarity | Textual consistency | 0.3 |
| Edge / Layout Match | Visual alignment and geometry | 0.2 |

**Final Score Formula Example:**

\[
Q = 0.5 \times SSIM + 0.3 \times TextSim + 0.2 \times LayoutSim
\]

---

### 5. Output & Visualization

1. **Per-Page Report**
   - SSIM score, OCR similarity, and threshold flag.
   - Save visual overlays of difference maps.

2. **Summary PDF / HTML Report**
   - Aggregated metrics and overall pass/fail verdict.
   - Highlight worst pages.

3. **Optional Dashboard**
   - Streamlit or Dash app for interactive exploration.

---

## Example Workflow (Python Pseudocode)

```python
from pdf2image import convert_from_path
from skimage.metrics import structural_similarity as ssim
import cv2, pytesseract, numpy as np

# Step 1: Convert PDFs to images
orig_pages = convert_from_path("original.pdf", dpi=300)
film_pages = convert_from_path("microfilm.pdf", dpi=300)

for i, (orig_img, film_img) in enumerate(zip(orig_pages, film_pages)):
    # Step 2: Convert to grayscale
    o = cv2.cvtColor(np.array(orig_img), cv2.COLOR_BGR2GRAY)
    f = cv2.cvtColor(np.array(film_img), cv2.COLOR_BGR2GRAY)

    # Step 3: Normalize size
    f = cv2.resize(f, (o.shape[1], o.shape[0]))

    # Step 4: Compute SSIM
    ssim_score, diff = ssim(o, f, full=True)
    diff = (diff * 255).astype("uint8")

    # Step 5: OCR comparison
    text_o = pytesseract.image_to_string(o)
    text_f = pytesseract.image_to_string(f)
    text_sim = difflib.SequenceMatcher(None, text_o, text_f).ratio()

    print(f"Page {i+1}: SSIM={ssim_score:.3f}, TextSim={text_sim:.3f}")

```

## Recommended Libraries

| Purpose           | Library                        | Notes                                  |
|-------------------|-------------------------------|----------------------------------------|
| PDF to Image      | `pdf2image`, `PyMuPDF`         | High-quality PDF rasterization         |
| Image Processing  | `OpenCV`, `scikit-image`       | Core comparison & normalization        |
| OCR               | `pytesseract`                  | Tesseract OCR engine                   |
| Text Similarity   | `difflib`, `fuzzywuzzy`, `sklearn` | Various distance metrics           |
| Reporting         | `matplotlib`, `reportlab`, `pandas`, `jinja2` | Visualization & export      |

---

## Possible Extensions

- **ML-based Quality Classification:**  
  Train a CNN or Vision Transformer to classify page quality (good/bad).
- **Batch Processing Pipeline:**  
  Process multiple document pairs automatically.
- **Threshold Calibration:**  
  Learn optimal thresholds from human QA data.
- **Web Interface:**  
  Streamlit app for human validation and visual inspection.

---

## Performance Considerations

- Use multiprocessing for large batches.
- Cache intermediate images to disk.
- Limit OCR to problematic pages when SSIM < threshold.
- Support GPU acceleration (OpenCV CUDA, PyTorch OCR).

---

## Deliverables

- `compare_documents.py` — Command-line tool for batch comparison
- `report_generator.py` — Builds HTML/PDF reports
- `config.yaml` — Configurable parameters (DPI, thresholds, weights)
- `docs/` — Technical documentation and setup guide

---

## Example Command

```sh
python compare_documents.py \
  --original original.pdf \
  --microfilm microfilm.pdf \
  --dpi 300 \
  --output results/
```

---

## Summary

This system provides a robust and flexible framework to:

- Objectively evaluate microfilm reproduction quality.
- Combine image similarity, OCR text analysis, and layout consistency.
- Generate reproducible, automated reports for archival QA.
