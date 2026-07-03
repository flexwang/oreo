"""Process Oreo's photos: remove background, resize to 150px cutouts."""

import os
from PIL import Image
from rembg import remove

SRC_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(SRC_DIR, "assets")

PHOTO_MAP = {
    "C164857B-2425-4ECF-88BF-158EA832FACF_4_5005_c.jpeg": "idle.png",
    "268FF131-B67E-40CB-B2E4-4C2C947D6999.jpeg": "walk.png",
    "9329D177-D175-4A47-966F-6A43DBAC78C7_1_105_c.jpeg": "sit.png",
    "10F8958E-66D1-4E5F-B1E4-8D1BF00C42D0_1_105_c.jpeg": "happy.png",
}

TARGET_SIZE = 150


def process_images():
    os.makedirs(ASSETS_DIR, exist_ok=True)

    for src_name, dst_name in PHOTO_MAP.items():
        src_path = os.path.join(SRC_DIR, src_name)
        dst_path = os.path.join(ASSETS_DIR, dst_name)

        if os.path.exists(dst_path):
            print(f"  Skip (exists): {dst_name}")
            continue

        print(f"  Processing: {src_name} → {dst_name}")
        with open(src_path, "rb") as f:
            input_data = f.read()

        output_data = remove(input_data)

        img = Image.open(__import__("io").BytesIO(output_data)).convert("RGBA")

        # Crop to content (remove excess transparent space)
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)

        # Resize to fit within TARGET_SIZE x TARGET_SIZE
        img.thumbnail((TARGET_SIZE, TARGET_SIZE), Image.LANCZOS)

        img.save(dst_path)
        print(f"  Saved: {dst_name} ({img.size[0]}x{img.size[1]})")

    print("\nDone! Cutouts saved to assets/")


if __name__ == "__main__":
    process_images()
