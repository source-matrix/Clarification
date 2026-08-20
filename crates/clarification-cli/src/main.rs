use clarification_core::{clarify, sharpness_score, ClarificationOptions};
use image::io::Reader as ImageReader;
use std::{env, process};

fn usage() -> ! {
    eprintln!(
        "Usage:\n  clarification clarify <input> <output> [--radius N] [--amount N] [--contrast N] [--threshold N]\n  clarification score <input>"
    );
    process::exit(2);
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
            let options = ClarificationOptions {
                radius: value(&args, "--radius", 1.2),
                amount: value(&args, "--amount", 1.35),
                contrast: value(&args, "--contrast", 8.0),
                threshold: value(&args, "--threshold", 2.0).clamp(0.0, 255.0) as u8,
            };
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
