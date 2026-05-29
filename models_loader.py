"""
Loads ImprovedUNet (segmentation) + ConvNeXt-Tiny (classification).
Model files are expected in:  WoundAI_Deploy/models/
"""

import os
import urllib.request
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from torchvision import transforms, models

# ── Model paths (relative to this file) ───────────────────────────────────
_BASE    = os.path.join(os.path.dirname(__file__), 'models')
SEG_PATH = os.path.join(_BASE, 'segmentation_improved_unet.pth')
CLS_PATH = os.path.join(_BASE, 'cls_overlay_convnext.pth')

DEVICE     = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
_seg_model = None
_cls_model = None

# ── Transforms ────────────────────────────────────────────────────────────
_seg_tf = transforms.Compose([
    transforms.Resize((256, 256)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

_cls_tf = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

# ── Architecture: ImprovedUNet ─────────────────────────────────────────────
class _ConvBlock(nn.Module):
    def __init__(self, in_c, out_c, dropout=0.0):
        super().__init__()
        layers = [
            nn.Conv2d(in_c, out_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_c), nn.ReLU(inplace=True),
            nn.Conv2d(out_c, out_c, 3, padding=1, bias=False),
            nn.BatchNorm2d(out_c), nn.ReLU(inplace=True),
        ]
        if dropout > 0:
            layers.append(nn.Dropout2d(p=dropout))
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        return self.block(x)


class _ImprovedUNet(nn.Module):
    def __init__(self, in_ch=3, out_ch=1, base=48, drop=0.10):
        super().__init__()
        b = base
        self.enc1       = _ConvBlock(in_ch, b,    dropout=0)
        self.enc2       = _ConvBlock(b,     b*2,  dropout=drop)
        self.enc3       = _ConvBlock(b*2,   b*4,  dropout=drop)
        self.enc4       = _ConvBlock(b*4,   b*8,  dropout=drop)
        self.bottleneck = _ConvBlock(b*8,   b*16, dropout=drop)
        self.up4  = nn.ConvTranspose2d(b*16, b*8, 2, stride=2)
        self.dec4 = _ConvBlock(b*16, b*8)
        self.up3  = nn.ConvTranspose2d(b*8,  b*4, 2, stride=2)
        self.dec3 = _ConvBlock(b*8,  b*4)
        self.up2  = nn.ConvTranspose2d(b*4,  b*2, 2, stride=2)
        self.dec2 = _ConvBlock(b*4,  b*2)
        self.up1  = nn.ConvTranspose2d(b*2,  b,   2, stride=2)
        self.dec1 = _ConvBlock(b*2,  b)
        self.pool = nn.MaxPool2d(2)
        self.head = nn.Conv2d(b, out_ch, 1)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(self.pool(e1))
        e3 = self.enc3(self.pool(e2))
        e4 = self.enc4(self.pool(e3))
        bn = self.bottleneck(self.pool(e4))
        d4 = self.dec4(torch.cat([self.up4(bn), e4], dim=1))
        d3 = self.dec3(torch.cat([self.up3(d4), e3], dim=1))
        d2 = self.dec2(torch.cat([self.up2(d3), e2], dim=1))
        d1 = self.dec1(torch.cat([self.up1(d2), e1], dim=1))
        return self.head(d1)


# ── Architecture: ConvNeXt-Tiny classifier ─────────────────────────────────
def _build_convnext(nc=2):
    m  = models.convnext_tiny(weights=None)
    nf = m.classifier[2].in_features
    m.classifier[2] = nn.Sequential(
        nn.Dropout(0.4), nn.Linear(nf, 512), nn.BatchNorm1d(512), nn.ReLU(True),
        nn.Dropout(0.3), nn.Linear(512, 128), nn.BatchNorm1d(128), nn.ReLU(True),
        nn.Dropout(0.2), nn.Linear(128, nc),
    )
    return m


# ── Download missing weights from Hugging Face ─────────────────────────────
def download_models_if_missing():
    os.makedirs(_BASE, exist_ok=True)
    for filename, url in (
        ('segmentation_improved_unet.pth',
         'https://huggingface.co/Maan8/woundai-models/resolve/main/segmentation_improved_unet.pth'),
        ('cls_overlay_convnext.pth',
         'https://huggingface.co/Maan8/woundai-models/resolve/main/cls_overlay_convnext.pth'),
    ):
        path = os.path.join(_BASE, filename)
        if not os.path.exists(path):
            print(f"[Models] Downloading {filename} ...")
            urllib.request.urlretrieve(url, path)


# ── Public: load both models ───────────────────────────────────────────────
def load_models():
    global _seg_model, _cls_model

    download_models_if_missing()

    if not os.path.exists(SEG_PATH):
        raise FileNotFoundError(f"Segmentation model not found:\n  {SEG_PATH}")
    if not os.path.exists(CLS_PATH):
        raise FileNotFoundError(f"Classifier model not found:\n  {CLS_PATH}")

    print(f"[Models] Device: {DEVICE}")
    print(f"[Models] Loading segmentation model ...")
    _seg_model = _ImprovedUNet().to(DEVICE)
    ck = torch.load(SEG_PATH, map_location=DEVICE, weights_only=False)
    _seg_model.load_state_dict(ck['model_state_dict'])
    _seg_model.eval()

    print(f"[Models] Loading classifier model ...")
    _cls_model = _build_convnext().to(DEVICE)
    ck = torch.load(CLS_PATH, map_location=DEVICE, weights_only=False)
    _cls_model.load_state_dict(ck['model_state_dict'])
    _cls_model.eval()

    print("[Models] Both models ready.\n")


# ── Public: apply overlay ──────────────────────────────────────────────────
def apply_overlay(img_pil: Image.Image, bg_alpha: float = 0.5) -> Image.Image:
    """
    Segments the wound and returns the full image with background
    dimmed to bg_alpha (0.5 = 50%) while the wound stays at full brightness.
    """
    if _seg_model is None:
        raise RuntimeError("Models not loaded. Call load_models() first.")

    W, H = img_pil.size
    with torch.inference_mode():
        inp       = _seg_tf(img_pil).unsqueeze(0).to(DEVICE)
        logits    = _seg_model(inp)
        soft_mask = torch.sigmoid(logits).squeeze().cpu().numpy()

    mask_resized = np.array(
        Image.fromarray((soft_mask * 255).astype(np.uint8)).resize((W, H), Image.BILINEAR),
        dtype=np.float32,
    ) / 255.0

    weight  = bg_alpha + (1.0 - bg_alpha) * mask_resized
    img_arr = np.array(img_pil, dtype=np.float32)
    result  = (img_arr * weight[:, :, np.newaxis]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(result)


# ── Public: classify ───────────────────────────────────────────────────────
# Classes sorted alphabetically by ImageFolder: ['infected', 'non-infected']
_CLASSES = ['infected', 'non-infected']

def classify(img_pil: Image.Image):
    """
    Returns (label: str, infected_prob: float, non_infected_prob: float).
    Pass the overlay image (output of apply_overlay) as input.
    """
    if _cls_model is None:
        raise RuntimeError("Models not loaded. Call load_models() first.")

    tensor = _cls_tf(img_pil).unsqueeze(0).to(DEVICE)
    with torch.inference_mode():
        logits = _cls_model(tensor)
        probs  = torch.softmax(logits, dim=1).squeeze().cpu().numpy()

    infected_prob     = float(probs[0])
    non_infected_prob = float(probs[1])
    label = _CLASSES[int(probs.argmax())]
    return label, infected_prob, non_infected_prob
