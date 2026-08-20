# Quick start

## Build the CLI

```bash
cargo build --release
```

The binary is written to `target/release/clarification`.

## Clarify an image

```bash
clarification clarify input.png output.png \
  --radius 1.2 \
  --amount 1.35 \
  --contrast 8 \
  --threshold 2
```

## Compare detail scores

```bash
clarification score input.png
clarification score output.png
```

The score is intended for repeatable local comparisons on the same image, not as an absolute image-quality rating.

## Python

```python
from clarification import Options, clarify_file, sharpness_score

options = Options(amount=1.5, contrast=10.0)
clarify_file("input.png", "output.png", options)
print(sharpness_score("output.png"))
```

## Go and Lua

Go and Lua use the same release binary. See the runnable files in `examples/go` and `examples/lua`; set the binary path before calling `Enhance` or `enhance`.
