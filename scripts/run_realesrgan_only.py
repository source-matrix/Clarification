from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import torchvision.transforms.functional as _functional
sys.modules.setdefault('torchvision.transforms.functional_tensor', _functional)

from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer


def main() -> None:
    parser = argparse.ArgumentParser(description='Run Real-ESRGAN background upscaling without face hallucination.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--weights', required=True)
    parser.add_argument('--tile', type=int, default=128)
    args = parser.parse_args()

    image = cv2.imread(args.input, cv2.IMREAD_COLOR)
    if image is None:
        raise SystemExit(f'cannot read input: {args.input}')
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
    upsampler = RealESRGANer(
        scale=4,
        model_path=args.weights,
        model=model,
        tile=args.tile,
        tile_pad=10,
        pre_pad=0,
        half=False,
    )
    output, _ = upsampler.enhance(image, outscale=4)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), output):
        raise SystemExit(f'cannot write output: {path}')
    print(f'{args.input} -> {path} ({output.shape[1]}x{output.shape[0]})')


if __name__ == '__main__':
    main()
