//! Clarification image enhancement engine.
//!
//! The pipeline is intentionally deterministic and CPU-only so it can be used
//! consistently from Rust, Go, Python, and Lua bindings.

use image::{DynamicImage, ImageBuffer, Pixel, Rgba};

/// Parameters controlling the clarification pipeline.
#[derive(Debug, Clone, Copy)]
pub struct ClarificationOptions {
    /// Radius of the local blur used by unsharp masking, in pixels.
    pub radius: f32,
    /// Detail gain. Values above 1.0 increase edge definition.
    pub amount: f32,
    /// Contrast adjustment in percentage points.
    pub contrast: f32,
    /// Ignore tiny differences below this luminance threshold.
    pub threshold: u8,
}

impl Default for ClarificationOptions {
    fn default() -> Self {
        Self {
            radius: 1.2,
            amount: 1.35,
            contrast: 8.0,
            threshold: 2,
        }
    }
}

/// Clarify an image using a deterministic unsharp-mask and contrast pipeline.
pub fn clarify(image: &DynamicImage, options: ClarificationOptions) -> DynamicImage {
    let rgba = image.to_rgba8();
    let (width, height) = rgba.dimensions();
    let blurred = image::imageops::blur(&rgba, options.radius.max(0.1));
    let contrast_factor = 1.0 + (options.contrast / 100.0);
    let amount = options.amount.max(0.0);
    let threshold = options.threshold as i16;

    let output: ImageBuffer<Rgba<u8>, Vec<u8>> = ImageBuffer::from_fn(width, height, |x, y| {
        let original = rgba.get_pixel(x, y);
        let soft = blurred.get_pixel(x, y);
        let mut channels = [0u8; 4];

        for channel in 0..3 {
            let base = original[channel] as f32;
            let detail = base - soft[channel] as f32;
            let sharpened = if detail.abs() >= threshold as f32 {
                base + amount * detail
            } else {
                base
            };
            let contrasted = ((sharpened - 128.0) * contrast_factor) + 128.0;
            channels[channel] = contrasted.clamp(0.0, 255.0).round() as u8;
        }
        channels[3] = original[3];
        Rgba(channels)
    });

    DynamicImage::ImageRgba8(output)
}

/// Return a simple sharpness proxy based on average horizontal/vertical luminance difference.
/// Higher values generally indicate more visible local detail.
pub fn sharpness_score(image: &DynamicImage) -> f32 {
    let gray = image.to_luma8();
    let (width, height) = gray.dimensions();
    if width < 2 || height < 2 {
        return 0.0;
    }
    let mut total = 0.0f32;
    let samples = ((width - 1) * (height - 1)) as f32;
    for y in 0..height - 1 {
        for x in 0..width - 1 {
            let a = gray.get_pixel(x, y).channels()[0] as f32;
            let right = gray.get_pixel(x + 1, y).channels()[0] as f32;
            let down = gray.get_pixel(x, y + 1).channels()[0] as f32;
            total += (a - right).abs() + (a - down).abs();
        }
    }
    total / (samples * 2.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    use image::{DynamicImage, GenericImageView, ImageBuffer, Rgba};

    fn fixture() -> DynamicImage {
        let image = ImageBuffer::from_fn(32, 32, |x, y| {
            let edge = if x == 16 || y == 16 { 240 } else { 100 };
            Rgba([edge, edge, edge, 255])
        });
        DynamicImage::ImageRgba8(image)
    }

    #[test]
    fn clarification_preserves_dimensions_and_alpha() {
        let input = fixture();
        let output = clarify(&input, ClarificationOptions::default());
        assert_eq!(input.dimensions(), output.dimensions());
        assert_eq!(output.to_rgba8().get_pixel(0, 0)[3], 255);
    }

    #[test]
    fn clarification_increases_detail_score_for_soft_edges() {
        let input = fixture().blur(2.0);
        let output = clarify(&input, ClarificationOptions::default());
        assert!(sharpness_score(&output) >= sharpness_score(&input));
    }
}
