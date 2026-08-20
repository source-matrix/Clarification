# Validation notes

The generated 256×256 fixture was processed with the Rust release CLI using the documented defaults: radius 1.2, amount 1.35, contrast 8, and threshold 2.

The CLI measured a local-detail score increase from **1.2344** before processing to **1.5007** after processing, an increase of approximately **21.00%**. The output remained 256×256 and was written as an RGBA PNG with an opaque alpha channel because the fixture itself is RGB.

Visual inspection confirmed that the square, circle, diagonal line, and central label remain aligned and that the enhanced image has stronger edge definition without obvious clipping or geometry changes. This is a controlled enhancement check, not a claim of recovering information absent from the source.

The complete local checks passed after the repository reorganization: Rust formatting and workspace tests, Python unit tests, Go formatting and tests, Lua smoke integration, README local-link validation, release CLI execution, and visual-asset presence checks.
