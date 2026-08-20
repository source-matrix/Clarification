"""Optional AI super-resolution backend.

The base package remains Pillow-only. Install the optional AI dependencies before
using this module and keep model weights outside the source distribution.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AIOptions:
    """Runtime controls for the optional Real-ESRGAN + GFPGAN backend."""

    tile: int = 128
    face_weight: float = 0.25
    upscale: int = 4


def clarify_ai_file(
    input_path: str | Path,
    output_path: str | Path,
    realesrgan_weights: str | Path,
    gfpgan_weights: str | Path,
    options: AIOptions | None = None,
) -> None:
    """Restore a face and upscale an image with optional AI model weights.

    This function intentionally requires explicit weight paths. It never downloads
    model files implicitly, which makes deployments reproducible and auditable.
    """
    options = options or AIOptions()
    try:
        import cv2
        import sys as _sys
        import torchvision.transforms.functional as _functional
        _sys.modules.setdefault("torchvision.transforms.functional_tensor", _functional)
        from basicsr.archs.rrdbnet_arch import RRDBNet
        from gfpgan import GFPGANer
        from realesrgan import RealESRGANer
    except ImportError as exc:
        raise RuntimeError(
            "AI backend dependencies are missing; install the optional AI requirements"
        ) from exc

    source = cv2.imread(str(input_path), cv2.IMREAD_COLOR)
    if source is None:
        raise ValueError(f"cannot read input image: {input_path}")

    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=options.upscale,
    )
    bg_upsampler = RealESRGANer(
        scale=options.upscale,
        model_path=str(realesrgan_weights),
        model=model,
        tile=max(0, int(options.tile)),
        tile_pad=10,
        pre_pad=0,
        half=False,
    )
    face_enhancer = GFPGANer(
        model_path=str(gfpgan_weights),
        upscale=options.upscale,
        arch="clean",
        channel_multiplier=2,
        bg_upsampler=bg_upsampler,
    )
    _, _, restored = face_enhancer.enhance(
        source,
        has_aligned=False,
        only_center_face=False,
        paste_back=True,
        weight=max(0.0, min(1.0, options.face_weight)),
    )
    if restored is None:
        raise RuntimeError("AI backend returned no image")
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output), restored):
        raise OSError(f"cannot write output image: {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Optional AI face restoration backend")
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--realesrgan-weights", required=True)
    parser.add_argument("--gfpgan-weights", required=True)
    parser.add_argument("--tile", type=int, default=128)
    parser.add_argument("--face-weight", type=float, default=0.25)
    args = parser.parse_args()
    clarify_ai_file(
        args.input,
        args.output,
        args.realesrgan_weights,
        args.gfpgan_weights,
        AIOptions(tile=args.tile, face_weight=args.face_weight),
    )
    print(f"AI clarified {args.input} -> {args.output}")


__all__ = ["AIOptions", "clarify_ai_file"]
