==================================================
  WoundAI — Wound Infection Classifier
  Graduation Project — April 2026
==================================================

ABOUT
-----
This app uses deep learning to classify wound photographs
as INFECTED or NON-INFECTED.

Pipeline:
  1. Upload a wound photo
  2. ImprovedUNet segments the wound region
  3. Overlay applied (wound x1.0 + background x0.5)
  4. ConvNeXt-Tiny classifies the overlay image
  5. Result + both images saved to local database

Model performance on test set (152 images):
  Accuracy : 92.76%
  F1 Score : 0.9276
  AUC-ROC  : 0.9858


FOLDER STRUCTURE
----------------
WoundAI_Deploy/
  run.py                  <-- START HERE
  app.py                  Flask routes
  models_loader.py        Model loading & inference
  database.py             SQLite database
  requirements.txt        Python dependencies
  models/
    segmentation_improved_unet.pth   (66.7 MB)
    cls_overlay_convnext.pth         (108.0 MB)
  static/
    css/style.css
    uploads/              Original images saved here
    overlays/             Overlay images saved here
  templates/
    index.html            Upload page
    result.html           Result page
    history.html          History page


SETUP — First Time Only
-----------------------
Step 1: Make sure Python 3.9 or newer is installed.

Step 2: Install dependencies (run once):
    pip install -r requirements.txt

  If you already have PyTorch installed, you can skip it:
    pip install flask Pillow werkzeug


START THE SERVER
----------------
Open a terminal/command prompt inside this folder and run:

    python run.py

Then open your browser and go to:

    http://localhost:5000

The server will load the models (takes ~10–30 seconds on first start).
Press Ctrl+C in the terminal to stop the server.


NOTES
-----
- The database (wound_app.db) is created automatically on first run.
- Uploaded images are stored in static/uploads/ and static/overlays/.
- Works on CPU — no GPU required.
- Supported image formats: JPG, PNG, BMP, WEBP (max 16 MB).
- This tool is for educational/research purposes only.
  It is NOT a substitute for professional medical diagnosis.


TROUBLESHOOTING
---------------
"Module not found: flask"
  -> Run: pip install -r requirements.txt

"Model not found" error
  -> Make sure both .pth files are inside the models/ folder.

Port already in use
  -> Change the port in run.py: app.run(port=5001)

==================================================
