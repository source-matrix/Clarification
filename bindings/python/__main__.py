from __future__ import annotations

import argparse

from . import Options, clarify_file, sharpness_score


def main() -> None:
    parser = argparse.ArgumentParser(description="Clarify images with Pillow")
    sub = parser.add_subparsers(dest="command", required=True)

    enhance = sub.add_parser("clarify", help="clarify an image")
    enhance.add_argument("input")
    enhance.add_argument("output")
    enhance.add_argument("--radius", type=float, default=1.2)
    enhance.add_argument("--amount", type=float, default=1.35)
    enhance.add_argument("--contrast", type=float, default=8.0)
    enhance.add_argument("--threshold", type=int, default=2)

    score = sub.add_parser("score", help="measure local detail")
    score.add_argument("input")

    args = parser.parse_args()
    if args.command == "clarify":
        clarify_file(args.input, args.output, Options(args.radius, args.amount, args.contrast, args.threshold))
        print(f"clarified {args.input} -> {args.output}")
    else:
        print(f"{sharpness_score(args.input):.4f}")


if __name__ == "__main__":
    main()
