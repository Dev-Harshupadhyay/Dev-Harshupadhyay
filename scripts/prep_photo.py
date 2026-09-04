#!/usr/bin/env python3
"""
Optional step for when you want to replace the placeholder banner in
dh-ascii.svg with a real ASCII portrait made from your own photo.

Usage:
    pip install -r requirements.txt   # needs pillow, numpy, opencv-python, rembg
    python prep_photo.py source-photo.jpg
    # -> writes source-prepped.png

Pipeline:
  1. rembg strips the background so only the subject remains.
  2. OpenCV CLAHE boosts local contrast (a flatly-lit face otherwise
     converts to a dark, unreadable blob of ASCII characters).
  3. Composite onto pure white so the background maps to the blank end
     of the character ramp (" .`:-=+*cs#%@") instead of printing noise.

The output source-prepped.png can then be fed into a grid-sampling +
density-ramp converter (downsample to ~100x53 characters, pick a glyph
per cell by brightness) to replace build_grid() in make_ascii_svg.py.
"""
import sys

def main():
    if len(sys.argv) < 2:
        print("usage: python prep_photo.py <source-photo.jpg>")
        sys.exit(1)

    from rembg import remove
    import cv2
    import numpy as np
    from PIL import Image

    src_path = sys.argv[1]

    # 1. remove background
    with open(src_path, "rb") as f:
        cutout = remove(f.read())
    img = Image.open(__import__("io").BytesIO(cutout)).convert("RGBA")

    # 2. CLAHE contrast boost (grayscale)
    arr = np.array(img.convert("L"))
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    boosted = clahe.apply(arr)

    # 3. composite the boosted subject onto pure white using the
    #    original alpha as a mask
    alpha = np.array(img)[:, :, 3]
    white_bg = np.full_like(boosted, 255)
    mask = alpha > 10
    out = np.where(mask, boosted, white_bg).astype(np.uint8)

    Image.fromarray(out).save("source-prepped.png")
    print("wrote source-prepped.png")


if __name__ == "__main__":
    main()
  
