# Clarification

**Clarification** is an open-source, deterministic image clarification toolkit designed to make soft or low-contrast images easier to inspect. It combines a CPU-only unsharp-mask pipeline with contrast normalization and exposes the same core concepts through Rust, Go, Python, and Lua.

> **ملخص بالعربية:** Clarification مكتبة مفتوحة المصدر لتوضيح الصور وتحسين التفاصيل الدقيقة، مع نواة Rust وواجهات موحدة لـ Rust وGo وPython وLua، وأداة سطر أوامر مناسبة للأتمتة.

## Why Clarification?

The project focuses on predictable enhancement rather than generative reconstruction. It does not invent pixels or claim to recover information that is absent from the source image. Instead, it applies a controlled local-detail pass, preserves alpha transparency, and provides a lightweight sharpness score for before/after comparisons.

| Capability | Status |
|---|---|
| Rust core library | Available |
| Cross-platform CLI | Available |
| Python binding with Pillow | Available |
| Go binding through the official CLI | Available |
| Lua binding through the official CLI | Available |
| PNG, JPEG, GIF, BMP, WebP, ICO, PNM, and QOI | Supported by the Rust CLI build |
| Deterministic CPU processing | Available |
| Alpha-channel preservation | Available |
| Unit tests and CI | Included |

## Architecture

The repository is intentionally layered. `clarification-core` contains the image algorithm and scoring function. The `clarification` binary provides a stable process boundary for automation. The Python binding offers an in-process Pillow implementation for Python applications, while Go and Lua bindings call the same CLI so they can remain dependency-light and easy to deploy.

```text
Rust applications ───────┐
                         │
Python applications ─────┼── Clarification API
                         │
Go applications ─────────┼── clarification CLI ── clarification-core
                         │
Lua applications ────────┘
```

## Rust installation and usage

Install the CLI from source:

```bash
cargo install --path crates/clarification-cli
```

Clarify an image:

```bash
clarification clarify input.png clarified.png \
  --radius 1.2 \
  --amount 1.35 \
  --contrast 8 \
  --threshold 2
```

Measure local detail:

```bash
clarification score input.png
clarification score clarified.png
```

Use the Rust library directly:

```rust
use clarification_core::{clarify, ClarificationOptions};
use image::io::Reader as ImageReader;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let source = ImageReader::open("input.png")?.decode()?;
    let enhanced = clarify(&source, ClarificationOptions::default());
    enhanced.save("clarified.png")?;
    Ok(())
}
```

## Python

The Python package requires Python 3.9+ and Pillow:

```bash
python -m pip install -e bindings/python
```

```python
from clarification import Options, clarify_file, sharpness_score

before = sharpness_score("input.png")
clarify_file("input.png", "clarified.png", Options(amount=1.5, contrast=10.0))
after = sharpness_score("clarified.png")
print(f"detail score: {before:.4f} -> {after:.4f}")
```

The Python command-line interface is also available:

```bash
python -m clarification clarify input.png clarified.png --amount 1.5 --contrast 10
```

## Go

The Go binding keeps the application dependency-light by invoking the official CLI:

```go
options := clarification.DefaultOptions()
err := clarification.Enhance("clarification", "input.png", "clarified.png", options)
if err != nil {
    panic(err)
}
```

See `examples/go/main.go` for a complete program.

## Lua

Copy `bindings/lua/clarification.lua` into your Lua module path:

```lua
local clarification = require("clarification")
local options = clarification.defaults()
options.amount = 1.5
local output, err = clarification.enhance("clarification", "input.png", "clarified.png", options)
assert(output, err)
```

## Parameter guide

| Parameter | Meaning | Typical range | Default |
|---|---|---:|---:|
| `radius` | Radius of the local blur used by unsharp masking | `0.5`–`3.0` | `1.2` |
| `amount` | Strength of recovered local detail | `0.5`–`2.5` | `1.35` |
| `contrast` | Contrast adjustment in percentage points | `0`–`25` | `8` |
| `threshold` | Minimum difference treated as detail | `0`–`20` | `2` |

For text, line art, and scanned documents, start with a lower `radius` and a moderate `amount`. For low-contrast photographs, increase `contrast` gradually. Strong settings can create halos, so visual inspection is always recommended.

## Development

Run the complete Rust test suite:

```bash
cargo test --workspace
```

Run Python tests after installing the package:

```bash
python -m pytest tests/python
```

Build the release CLI:

```bash
cargo build --release -p clarification
```

The project includes a GitHub Actions workflow that checks Rust formatting, Rust tests, Python tests, and Go formatting/build validation.

## Limitations and responsible use

Clarification is an enhancement tool, not a forensic recovery system. Sharpening can improve legibility but cannot restore detail that was never captured. Avoid using a processed image as the sole basis for safety-critical, legal, medical, or identity decisions.

## License

Clarification is released under the MIT License. See [LICENSE](LICENSE) for the complete text.
