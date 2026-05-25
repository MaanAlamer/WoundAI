"""
WoundAI — Wound Infection Classifier
=====================================
Run this file to start the web server:

    python run.py

Then open your browser at:  http://localhost:5000
"""
import database
import models_loader
from app import app

if __name__ == '__main__':
    print("=" * 50)
    print("  WoundAI — Wound Infection Classifier")
    print("  Model : ConvNeXt-Tiny + Overlay Segmentation")
    print("  Acc   : 92.76%  |  F1: 0.9276  |  AUC: 0.9858")
    print("=" * 50)
    database.init_db()
    models_loader.load_models()
    print("  Open in browser: http://localhost:5000")
    print("  Press Ctrl+C to stop.\n")
    app.run(debug=False, host='0.0.0.0', port=5000)
