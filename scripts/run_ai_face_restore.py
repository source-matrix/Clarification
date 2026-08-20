from __future__ import annotations

import argparse
from pathlib import Path

import cv2

# Basicsr 1.4.2 imports a module removed from newer torchvision releases.
# Installations using current torchvision can safely map it to the public functional API.
import sys
import torchvision.transforms.functional as _functional
sys.modules.setdefault('torchvision.transforms.functional_tensor', _functional)

from basicsr.archs.rrdbnet_arch import RRDBNet
from gfpgan import GFPGANer
from realesrgan import RealESRGANer


def main() -> None:
    parser = argparse.ArgumentParser(description='Run optional AI face restoration for Clarification evaluation.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--realesrgan-weights', required=True)
    parser.add_argument('--gfpgan-weights', required=True)
    parser.add_argument('--tile', type=int, default=128)
    parser.add_argument('--face-weight', type=float, default=0.5)
    args = parser.parse_args()

    image = cv2.imread(args.input, cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f'cannot read input: {args.input}')

    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=4,
    )
    bg_upsampler = RealESRGANer(
        scale=4,
        model_path=args.realesrgan_weights,
        model=model,
        tile=args.tile,
        tile_pad=10,
        pre_pad=0,
        half=False,
    )
    face_enhancer = GFPGANer(
        model_path=args.gfpgan_weights,
        upscale=4,
        arch='clean',
        channel_multiplier=2,
        bg_upsampler=bg_upsampler,
    )

    _, _, restored = face_enhancer.enhance(
        image,
        has_aligned=False,
        only_center_face=False,
        paste_back=True,
        weight=args.face_weight,
    )
    if restored is None:
        raise SystemExit('AI face restoration returned no image')
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output), restored):
        raise SystemExit(f'cannot write output: {output}')
    print(f'{args.input} -> {output} ({restored.shape[1]}x{restored.shape[0]})')


if __name__ == '__main__':
    main()
