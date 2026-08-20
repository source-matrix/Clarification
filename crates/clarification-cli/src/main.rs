use clarification_core::{clarify, sharpness_score, ClarificationOptions};
use image::io::Reader as ImageReader;
use std::{env, process};

fn usage() -> ! {
    eprintln!(
        "Usage:\n  clarification clarify <input> <output> [--preset portrait] [--scale N] [--radius N] [--amount N] [--contrast N] [--threshold N]\n  clarification score <input>"
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
            options.radius = value(&args, "--radius", options.radius);
            options.amount = value(&args, "--amount", options.amount);
            options.contrast = value(&args, "--contrast", options.contrast);
            options.threshold =
                value(&args, "--threshold", options.threshold as f32).clamp(0.0, 255.0) as u8;
            options.scale = value(&args, "--scale", options.scale).max(1.0);
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
