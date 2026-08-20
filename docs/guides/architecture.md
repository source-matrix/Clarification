# Architecture

Clarification uses one enhancement contract across four language entry points. Rust owns the reference implementation and the command-line interface. Python performs the same operation in-process through Pillow, while Go and Lua invoke the portable CLI bridge so applications can reuse the same binary and option names.

![Clarification processing architecture](../assets/architecture.png)

## Processing stages

The core converts the source to a stable pixel representation, applies local contrast, performs controlled unsharp enhancement, restores the original alpha channel, and writes the output in the format selected by the destination extension. The `sharpness_score` command is a lightweight comparison metric for controlled before/after checks; it is not a perceptual quality score or a forensic confidence measure.

## Why a shared CLI exists

A small CLI gives Go and Lua a stable integration point without requiring every language binding to duplicate image codecs or unsafe native FFI. Rust applications can call the core directly or invoke the CLI. Python uses Pillow in-process for a zero-subprocess workflow.

## Data and safety properties

Clarification processes files locally. It does not upload images, call a remote service, or require credentials. The operation preserves image dimensions and alpha transparency when the selected decoder and encoder support them.
