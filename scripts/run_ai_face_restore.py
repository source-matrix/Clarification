from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bindings/python'))

from clarification.ai import AIOptions, clarify_ai_file


def main() -> None:
    parser = argparse.ArgumentParser(description='Run optional AI face restoration for Clarification evaluation.')
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--realesrgan-weights', required=True)
    parser.add_argument('--gfpgan-weights', required=True)
    parser.add_argument('--tile', type=int, default=128)
    parser.add_argument('--face-weight', type=float, default=0.50, help='GFPGAN blend weight; 0.50 is the portrait eye-detail profile')
    parser.add_argument('--eye-blend', type=float, default=0.65, help='Conservative Real-ESRGAN eye-detail blend, from 0 to 1')
    args = parser.parse_args()

    options = AIOptions(
        tile=args.tile,
        face_weight=args.face_weight,
        eye_blend=args.eye_blend,
    )
    clarify_ai_file(
        args.input,
        args.output,
        args.realesrgan_weights,
        args.gfpgan_weights,
        options,
    )
    print(f'{args.input} -> {args.output}')


if __name__ == '__main__':
    main()
