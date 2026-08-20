"""Clarification image enhancement for Python.

This binding mirrors the Rust engine's public options while remaining portable
by using Pillow for in-process processing.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from .ai import AIOptions, clarify_ai_file

ImageLike = Union[Image.Image, str, Path]


@dataclass(frozen=True)
class Options:
    radius: float = 1.2
    amount: float = 1.35
    contrast: float = 8.0
    threshold: int = 2
    scale: float = 1.0
    denoise: float = 0.12
    skin_protection: float = 0.25

    @classmethod
    def portrait(cls) -> "Options":
        """Return the portrait profile for blemish reduction and face protection."""
        return cls(
            radius=0.15,
            amount=6.0,
            contrast=10.0,
            threshold=1,
            scale=4.0,
            denoise=0.02,
            skin_protection=0.72,
        )


def _denoise(source: Image.Image, strength: float) -> Image.Image:
    """Reduce isolated specks with a small median pass and controlled blending."""
    strength = max(0.0, min(1.0, strength))
    if strength == 0.0:
        return source
    rgb = source.convert("RGB")
    median = rgb.filter(ImageFilter.MedianFilter(size=3))
    return Image.blend(rgb, median, strength)


def clarify(image: ImageLike, options: Options | None = None) -> Image.Image:
    """Clarify an image and return a new Pillow image.

    The portrait profile uses a conservative median pass before sharpening. This
    reduces isolated blemishes while keeping the input geometry and alpha.
    ``skin_protection`` lowers the global sharpening strength for portrait use;
    the Rust core additionally applies a local warm-region protection gate.
    """
    options = options or Options()
    close_after = False
    if isinstance(image, (str, Path)):
        image = Image.open(image)
        close_after = True
    try:
        source = image.convert("RGBA")
        prepared_rgb = _denoise(source, options.denoise)
        percent = max(
            0,
            int(
                options.amount
                * 100
                * (1.0 - 0.45 * max(0.0, min(1.0, options.skin_protection)))
            ),
        )
        sharpened = prepared_rgb.convert("RGBA").filter(
            ImageFilter.UnsharpMask(
                radius=max(0.1, options.radius),
                percent=percent,
                threshold=max(0, int(options.threshold)),
            )
        )
        rgb = sharpened.convert("RGB")
        enhanced = ImageEnhance.Contrast(rgb).enhance(max(0.0, 1 + options.contrast / 100))
        result = enhanced.convert("RGBA")
        result.putalpha(source.getchannel("A"))
        if options.scale > 1.0:
            width = max(1, round(result.width * options.scale))
            height = max(1, round(result.height * options.scale))
            result = result.resize((width, height), Image.Resampling.LANCZOS)
        return result
    finally:
        if close_after:
            image.close()


def clarify_file(input_path: ImageLike, output_path: str | Path, options: Options | None = None) -> None:
    """Clarify an image file and save it using the output extension."""
    result = clarify(input_path, options)
    result.save(output_path)


def sharpness_score(image: ImageLike) -> float:
    """Return a lightweight local-detail score for before/after comparisons."""
    close_after = False
    if isinstance(image, (str, Path)):
        image = Image.open(image)
        close_after = True
    try:
        gray = ImageOps.grayscale(image)
        pixels = gray.load()
        width, height = gray.size
        if width < 2 or height < 2:
            return 0.0
        total = sum(
            abs(pixels[x, y] - pixels[x + 1, y]) + abs(pixels[x, y] - pixels[x, y + 1])
            for y in range(height - 1)
            for x in range(width - 1)
        )
        return total / (2 * (width - 1) * (height - 1))
    finally:
        if close_after:
            image.close()


__all__ = [
    "Options",
    "AIOptions",
    "clarify",
    "clarify_file",
    "clarify_ai_file",
    "sharpness_score",
]
__version__ = "0.1.0"
