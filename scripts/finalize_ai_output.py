from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    parser.add_argument('output')
    parser.add_argument('--size', type=int, default=2048)
    args = parser.parse_args()

    source = Image.open(args.input).convert('RGB')
    result = source.resize((args.size, args.size), Image.Resampling.LANCZOS)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result.save(output, format='PNG', optimize=True)
    print(f'{args.input} -> {output} ({args.size}x{args.size})')


if __name__ == '__main__':
    main()
