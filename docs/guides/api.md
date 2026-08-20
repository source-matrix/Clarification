# API reference

## Rust

`ClarificationOptions` contains `radius`, `amount`, `contrast`, `threshold`, `scale`, `denoise`, and `skin_protection`. Pass it to `clarify(&DynamicImage, options)` to receive a new `DynamicImage`; the original image is not mutated. `ClarificationOptions::portrait()` returns the calibrated portrait profile with controlled speck reduction, face-region protection, and 4× default scaling. `sharpness_score(&DynamicImage)` returns a deterministic local-detail proxy.

## Python

`clarification.Options` mirrors the Rust parameters, including `denoise` and `skin_protection`. `Options.portrait()` returns the calibrated portrait profile. `clarify(image, options)` returns a new Pillow image, `clarify_file(input, output, options)` processes files, and `sharpness_score(image)` enables before/after comparisons.

## Go

`clarification.Enhance(binary, input, output, options)` invokes the official CLI and returns a Go error if the process fails. `clarification.Options` includes `Denoise` and `SkinProtection`; `clarification.PortraitOptions()` returns the calibrated portrait profile with 4× scaling. `clarification.Score(binary, input)` parses the CLI score as `float64`.

## Lua

`clarification.enhance(binary, input, output, options)` returns CLI output or `nil, error`. `clarification.score(binary, input)` returns a number or `nil, error`. `clarification.defaults()` returns the default option table, while `clarification.portrait()` returns the calibrated portrait profile with `denoise` and `skin_protection`.

## CLI options

The `clarify` command accepts `--radius`, `--amount`, `--contrast`, `--threshold`, `--scale`, `--denoise`, and `--skin-protection`. The shortcut `--preset portrait` applies the calibrated profile, and explicit flags can override any profile value.

## Processing model

The pipeline converts the input into RGBA, optionally resizes it with Lanczos, applies a small edge-preserving denoise pass, derives local detail from a soft image, applies thresholded protected detail gain, adjusts contrast around mid-gray, clamps channels to `[0, 255]`, and restores the original alpha channel. Warm, low-gradient regions receive less sharpening when `skin_protection` is enabled, while strong edges such as eyes, eyelashes, hair, and clothing remain eligible for detail enhancement.

The portrait profile is a deterministic enhancement-and-upscale filter, not a generative face-restoration model. It can reduce visible noise and improve clarity while preserving geometry, but it cannot guarantee recovery of texture that is absent from a low-resolution source.
