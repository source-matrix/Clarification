# API reference

## Rust

`ClarificationOptions` contains `radius`, `amount`, `contrast`, and `threshold`. Pass it to `clarify(&DynamicImage, options)` to receive a new `DynamicImage`. The original image is not mutated. `sharpness_score(&DynamicImage)` returns a deterministic local-detail proxy.

## Python

`clarification.Options` mirrors the Rust parameters. `clarify(image, options)` returns a new Pillow image, `clarify_file(input, output, options)` processes files, and `sharpness_score(image)` enables before/after comparisons.

## Go

`clarification.Enhance(binary, input, output, options)` invokes the official CLI and returns a Go error if the process fails. `clarification.Score(binary, input)` parses the CLI score as `float64`.

## Lua

`clarification.enhance(binary, input, output, options)` returns CLI output or `nil, error`. `clarification.score(binary, input)` returns a number or `nil, error`. `clarification.defaults()` returns the default option table.

## Processing model

The pipeline converts the input into RGBA, computes a Gaussian soft image, derives local detail as the difference between the source and soft image, applies thresholded detail gain, adjusts contrast around mid-gray, clamps channels to `[0, 255]`, and restores the original alpha channel.
