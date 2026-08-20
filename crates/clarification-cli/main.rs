use clarification_core::{clarify, sharpness_score, ClarificationOptions};
use image::io::Reader as ImageReader;
use std::{env, process, process::Command};

fn usage() -> ! {
    eprintln!(
        "Usage:\n  clarification clarify <input> <output> [--preset portrait] [--scale N] [--radius N] [--amount N] [--contrast N] [--threshold N] [--denoise N] [--skin-protection N]\n  clarification ai <input> <output> --realesrgan-weights PATH --gfpgan-weights PATH [--runner clarification-ai] [--face-weight N] [--tile N]\n  clarification score <input>"
    );
    process::exit(2);
}

fn has_flag(args: &[String], flag: &str) -> bool {
    args.iter().any(|arg| arg == flag)
}

fn value(args: &[String], flag: &str, default: f32) -> f32 {
    args.windows(2)
        .find(|pair| pair[0] == flag)
        .and_then(|pair| pair[1].parse().ok())
        .unwrap_or(default)
}

fn string_value(args: &[String], flag: &str, default: &str) -> String {
    args.windows(2)
        .find(|pair| pair[0] == flag)
        .map(|pair| pair[1].clone())
        .unwrap_or_else(|| default.to_string())
}

fn required_value(args: &[String], flag: &str) -> String {
    args.windows(2)
        .find(|pair| pair[0] == flag)
        .map(|pair| pair[1].clone())
        .unwrap_or_else(|| fatal(&format!("missing required option {flag}")))
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 3 {
        usage();
    }

    match args[1].as_str() {
        "clarify" => {
            if args.len() < 4 {
                usage();
            }
            let input = &args[2];
            let output = &args[3];
            let mut options = if has_flag(&args, "--preset")
                && args
                    .windows(2)
                    .any(|pair| pair[0] == "--preset" && pair[1] == "portrait")
            {
                ClarificationOptions::portrait()
            } else {
                ClarificationOptions::default()
            };
            options.radius = value(&args, "--radius", options.radius).max(0.1);
            options.amount = value(&args, "--amount", options.amount).max(0.0);
            options.contrast = value(&args, "--contrast", options.contrast);
            options.threshold =
                value(&args, "--threshold", options.threshold as f32).clamp(0.0, 255.0) as u8;
            options.scale = value(&args, "--scale", options.scale).max(1.0);
            options.denoise = value(&args, "--denoise", options.denoise).clamp(0.0, 1.0);
            options.skin_protection =
                value(&args, "--skin-protection", options.skin_protection).clamp(0.0, 1.0);
            let image = ImageReader::open(input)
                .unwrap_or_else(|e| fatal(&format!("cannot open input: {e}")))
                .decode()
                .unwrap_or_else(|e| fatal(&format!("cannot decode input: {e}")));
            let enhanced = clarify(&image, options);
            enhanced
                .save(output)
                .unwrap_or_else(|e| fatal(&format!("cannot save output: {e}")));
            println!("clarified {input} -> {output}");
        }
        "ai" => {
            if args.len() < 4 {
                usage();
            }
            let input = &args[2];
            let output = &args[3];
            let runner = string_value(&args, "--runner", "clarification-ai");
            let realesrgan_weights = required_value(&args, "--realesrgan-weights");
            let gfpgan_weights = required_value(&args, "--gfpgan-weights");
            let face_weight = value(&args, "--face-weight", 0.25).clamp(0.0, 1.0);
            let face_weight_value = face_weight.to_string();
            let tile = string_value(&args, "--tile", "128");
            let status = Command::new(&runner)
                .args([
                    input,
                    output,
                    "--realesrgan-weights",
                    &realesrgan_weights,
                    "--gfpgan-weights",
                    &gfpgan_weights,
                    "--face-weight",
                    &face_weight_value,
                    "--tile",
                    &tile,
                ])
                .status()
                .unwrap_or_else(|e| fatal(&format!("cannot start AI runner {runner}: {e}")));
            if !status.success() {
                fatal(&format!("AI runner exited with status {status}"));
            }
            println!("AI clarified {input} -> {output}");
        }
        "score" => {
            let image = ImageReader::open(&args[2])
                .unwrap_or_else(|e| fatal(&format!("cannot open input: {e}")))
                .decode()
                .unwrap_or_else(|e| fatal(&format!("cannot decode input: {e}")));
            println!("{:.4}", sharpness_score(&image));
        }
        _ => usage(),
    }
}

fn fatal(message: &str) -> ! {
    eprintln!("error: {message}");
    process::exit(1);
}
