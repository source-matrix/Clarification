# Portrait profile validation

## Input and reference

- Input: `docs/assets/before-after/before.jpeg`, 447×447 RGB.
- User-provided clarified reference: `docs/assets/before-after/after.jpeg`, 2048×2048 RGB.
- The reference is a visual target, not pixel-perfect ground truth: dimensions and JPEG encoding differ.

## Validation commands

```bash
cargo test --workspace
python3 scripts/verify_fixture.py
```

The fixture checks that output dimensions remain stable, alpha is preserved when present, and isolated bright specks are reduced by the portrait profile.

## Visual review of later candidates

The v4 and v5 candidates preserve the face geometry and remove isolated noise, but their skin remains intentionally smooth and their fine texture is still below the user-provided 2048×2048 reference. v5 increases local edge definition around the eyes and hair without obvious ringing, but a classical deterministic filter cannot recreate eyelashes and skin texture that are absent from the 447×447 source. The implementation should therefore keep conservative defaults and expose stronger controls rather than claim exact reference reconstruction.
