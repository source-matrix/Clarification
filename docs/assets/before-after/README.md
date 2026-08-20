# Before / after reference

This directory contains the user-provided reference pair used to calibrate and document the `portrait` profile.

| File | Meaning |
| --- | --- |
| [`before.jpeg`](before.jpeg) | Original 447 × 447 input image. |
| [`after.jpeg`](after.jpeg) | User-provided clarified reference at 2048 × 2048. |
| [`generated-portrait-native.jpeg`](generated-portrait-native.jpeg) | Clarification `portrait` output at the original 447 × 447 dimensions. |
| [`generated-portrait-2048.jpeg`](generated-portrait-2048.jpeg) | Clarification `portrait` output resized to approximately 2048 × 2048 (`2047 × 2047` with the tested scale). |

The pair is a visual reference, not a pixel-perfect ground-truth comparison: the dimensions and JPEG encoding differ. Clarification uses it to document the intended direction—stronger local detail, controlled contrast, and a larger output—while preserving the limitations of deterministic CPU-only enhancement. The generated files demonstrate the library’s deterministic result; they are not claimed to reproduce the supplied reference pixel-for-pixel.
