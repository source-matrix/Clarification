from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.metrics import structural_similarity


def load_rgb(path: Path) -> np.ndarray:
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(path)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


def resize_rgb(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    return cv2.resize(image, size, interpolation=cv2.INTER_AREA)


def sharpness(image: np.ndarray) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def reference_scores(image: np.ndarray, reference: np.ndarray) -> tuple[float, float]:
    target = resize_rgb(reference, (image.shape[1], image.shape[0]))
    mse = np.mean((image.astype(np.float32) - target.astype(np.float32)) ** 2)
    psnr = float('inf') if mse == 0 else float(20.0 * np.log10(255.0 / np.sqrt(mse)))
    gray_a = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray_b = cv2.cvtColor(target, cv2.COLOR_RGB2GRAY)
    ssim = float(structural_similarity(gray_a, gray_b, data_range=255))
    return psnr, ssim


def make_grid(images: list[tuple[str, np.ndarray]], output: Path) -> None:
    panel_size = (512, 512)
    header = 56
    margin = 16
    cols = 2
    rows = (len(images) + cols - 1) // cols
    canvas = Image.new('RGB', (cols * (panel_size[0] + margin) + margin, rows * (panel_size[1] + header + margin) + margin), '#111827')
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    for index, (label, image) in enumerate(images):
        col = index % cols
        row = index // cols
        x = margin + col * (panel_size[0] + margin)
        y = margin + row * (panel_size[1] + header + margin)
        draw.text((x, y + 12), label, fill='#f9fafb', font=font)
        thumb = Image.fromarray(resize_rgb(image, panel_size))
        canvas.paste(thumb, (x, y + header))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('items', nargs='+', help='label=path')
    args = parser.parse_args()

    reference = load_rgb(args.reference)
    rows = []
    grid_items = []
    for item in args.items:
        label, raw_path = item.split('=', 1)
        path = Path(raw_path)
        image = load_rgb(path)
        psnr, ssim = reference_scores(image, reference)
        rows.append({
            'label': label,
            'path': str(path),
            'width': int(image.shape[1]),
            'height': int(image.shape[0]),
            'sharpness_laplacian_variance': sharpness(image),
            'reference_psnr_db': psnr,
            'reference_ssim': ssim,
        })
        grid_items.append((label, image))

    grid_items.append(('Reference', reference))
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'metrics.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
    make_grid(grid_items, output_dir / 'comparison-grid.jpg')
    print(json.dumps({'metrics': str(output_dir / 'metrics.json'), 'grid': str(output_dir / 'comparison-grid.jpg')}, indent=2))


if __name__ == '__main__':
    main()
