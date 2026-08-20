from pathlib import Path
from PIL import Image, ImageStat, ImageFilter, ImageChops

root = Path(__file__).resolve().parents[1]
folder = root / "docs" / "assets" / "before-after"
paths = sorted(folder.glob("*"))
for path in paths:
    try:
        with Image.open(path) as image:
            rgba = image.convert("RGBA")
            gray = rgba.convert("L")
            edges = gray.filter(ImageFilter.FIND_EDGES)
            print(f"{path.name}\tformat={image.format}\tsize={image.size}\tmode={image.mode}\tmean={ImageStat.Stat(gray).mean[0]:.3f}\tedge_mean={ImageStat.Stat(edges).mean[0]:.3f}")
    except Exception as exc:
        print(f"{path.name}\tSKIP\t{exc}")
