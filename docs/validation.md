# Validation notes

The generated 256×256 fixture was processed with the Rust CLI using radius 1.2, amount 1.5, contrast 10, and threshold 2.

The CLI measured a local-detail score increase from **1.2344** before processing to **1.5435** after processing, an increase of approximately **25.0%**. The output remained a valid 256×256 RGBA PNG.

Visual inspection confirmed that the square, circle, diagonal line, and central label remain aligned and that the enhanced image has stronger edge definition without obvious clipping or geometry changes. This is a controlled enhancement check, not a claim of recovering information absent from the source.
