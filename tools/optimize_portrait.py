"""Encode responsive WebP copies of the original portrait. Requires Pillow locally.

Only the encoding and pixel dimensions change. The original stays available as the
JPEG fallback and social-sharing image. Generated files are committed, so deployment
requires no image-processing dependency.
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'assets/images'
WIDTHS = (192, 320, 480, 720)

if __name__ == '__main__':
    DEST.mkdir(parents=True, exist_ok=True)
    with Image.open(ROOT / 'avatar.jpg') as original:
        source = ImageOps.exif_transpose(original).convert('RGB')
        for width in WIDTHS:
            height = round(source.height * width / source.width)
            resized = source.resize((width, height), Image.Resampling.LANCZOS)
            path = DEST / f'marc-luehr-{width}.webp'
            resized.save(path, format='WEBP', quality=85, method=6)
            with Image.open(path) as encoded:
                assert encoded.size == (width, height)
                encoded.load()
            print(f'{path.relative_to(ROOT)}: {width}x{height}, {path.stat().st_size} bytes')
