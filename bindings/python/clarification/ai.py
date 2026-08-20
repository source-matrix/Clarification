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
    face_weight: float = 0.50
    upscale: int = 4
    eye_blend: float = 0.65

    @classmethod
    def portrait(cls) -> "AIOptions":
        """Balanced face-restoration profile with stronger natural eye detail."""
        return cls(tile=128, face_weight=0.50, upscale=4, eye_blend=0.65)


def _blend_eye_detail(cv2, source, restored, background, landmarks, upscale, strength):
    """Blend conservative background-SR eye detail back into GFPGAN output.

    GFPGAN can smooth tiny irises and catchlights while restoring the overall
    face. The background Real-ESRGAN pass does not invent a face structure, so
    a soft, landmark-guided eye-only blend keeps those small details natural.
    """
    if strength <= 0 or not landmarks:
        return restored

    import numpy as np

    result = restored.copy()
    h, w = result.shape[:2]
    alpha_strength = max(0.0, min(1.0, float(strength)))
    for landmark_set in landmarks:
        if len(landmark_set) < 2:
            continue
        left_eye, right_eye = landmark_set[0], landmark_set[1]
        center_distance = float(np.linalg.norm(right_eye - left_eye) * upscale)
        if center_distance < 4:
            continue
        center = ((left_eye + right_eye) * 0.5 * upscale).astype(int)
        angle = float(np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0])))
        # The first two 5-point landmarks are eye centers. The ellipse is
        # intentionally tight so skin and eyelids remain owned by GFPGAN.
        axes = (
            max(3, int(center_distance * 0.29)),
            max(2, int(center_distance * 0.17)),
        )
        outer = np.zeros((h, w), dtype=np.uint8)
        cv2.ellipse(outer, tuple(center), axes, angle, 0, 360, 255, -1)
        blur = max(1, int(center_distance * 0.035) * 2 + 1)
        soft = cv2.GaussianBlur(outer, (blur, blur), 0).astype(np.float32) / 255.0
        soft *= alpha_strength
        soft = soft[..., None]
        result = (result.astype(np.float32) * (1.0 - soft) + background.astype(np.float32) * soft).clip(0, 255).astype(np.uint8)
    return result


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
    options = options or AIOptions.portrait()
    try:
        import cv2
        import torchvision.transforms.functional as _functional
        sys.modules.setdefault("torchvision.transforms.functional_tensor", _functional)
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

    if options.eye_blend > 0 and getattr(face_enhancer, "face_helper", None) is not None:
        landmarks = getattr(face_enhancer.face_helper, "all_landmarks_5", [])
        if landmarks:
            background, _ = bg_upsampler.enhance(source, outscale=options.upscale)
            restored = _blend_eye_detail(
                cv2,
                source,
                restored,
                background,
                landmarks,
                options.upscale,
                options.eye_blend,
            )

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
    parser.add_argument("--face-weight", type=float, default=0.50)
    parser.add_argument("--eye-blend", type=float, default=0.65)
    args = parser.parse_args()
    clarify_ai_file(
        args.input,
        args.output,
        args.realesrgan_weights,
        args.gfpgan_weights,
        options=AIOptions(tile=args.tile, face_weight=args.face_weight, eye_blend=args.eye_blend),
    )
    print(f"AI clarified {args.input} -> {args.output}")


__all__ = ["AIOptions", "clarify_ai_file"]


if __name__ == "__main__":
    main()
