# Portrait calibration notes

## Reference files

- Input: `docs/assets/before-after/before.jpeg`, 447×447 RGB.
- User-provided clarified reference: `docs/assets/before-after/after.jpeg`, 2048×2048 RGB.

## Iterations

- Initial portrait output: 2047×2047, local-detail score 1.8152; it was visibly softer than the reference after resizing.
- Resize-before-sharpen output: 2047×2047, local-detail score 1.4134; the visual result remained too soft, so it was not selected.
- The current implementation uses deterministic denoising, protected unsharp detail, local contrast, and Lanczos resizing. Further calibration is focused on increasing fine feature definition around eyes and hair while preserving smooth skin and face geometry.

These measurements are diagnostics, not a claim of pixel-perfect reconstruction. A 447×447 source cannot deterministically recover all texture present in a separate 2048×2048 reference.


## Visual review of later candidates

The v4 and v5 candidates preserve the face geometry and remove isolated noise, but their skin remains intentionally smooth and their fine texture is still below the user-provided 2048×2048 reference. v5 increases local edge definition around the eyes and hair without obvious ringing, but a classical deterministic filter cannot recreate eyelashes and skin texture that are absent from the 447×447 source. The implementation should therefore keep conservative defaults and expose stronger controls rather than claim exact reference reconstruction.

