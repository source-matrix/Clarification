use clarification_core::{clarify, ClarificationOptions};
use image::io::Reader as ImageReader;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let input = ImageReader::open("input.png")?.decode()?;
    let output = clarify(&input, ClarificationOptions::default());
    output.save("clarified.png")?;
    println!("saved clarified.png");
    Ok(())
}
