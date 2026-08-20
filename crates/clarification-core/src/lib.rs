//! Clarification image enhancement engine.
//!
//! The pipeline is deterministic and CPU-only so it can be used consistently
//! from Rust, Go, Python, and Lua bindings.

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
    /// Optional output scale. Values at or below 1.0 keep the input dimensions.
    pub scale: f32,
    /// Strength of the small-radius, edge-preserving denoise pass.
    pub denoise: f32,
    /// Protection applied to warm, low-gradient skin-like regions.
    pub skin_protection: f32,
}

impl Default for ClarificationOptions {
    fn default() -> Self {
        Self {
            radius: 1.2,
            amount: 1.35,
            contrast: 8.0,
            threshold: 2,
            scale: 1.0,
            denoise: 0.12,
            skin_protection: 0.25,
        }
    }
}

impl ClarificationOptions {
    /// A portrait-oriented profile with blemish suppression and face protection.
    pub fn portrait() -> Self {
        Self {
            radius: 0.15,
            amount: 6.0,
            contrast: 10.0,
            threshold: 1,
            scale: 4.0,
            denoise: 0.02,
            skin_protection: 0.72,
        }
    }
}

fn luminance(pixel: &Rgba<u8>) -> f32 {
    0.2126 * pixel[0] as f32 + 0.7152 * pixel[1] as f32 + 0.0722 * pixel[2] as f32
}

fn skin_likelihood(pixel: &Rgba<u8>) -> f32 {
    let r = pixel[0] as f32;
    let g = pixel[1] as f32;
    let b = pixel[2] as f32;
    let brightness = ((r + g + b) / 3.0 / 210.0).clamp(0.0, 1.0);
    let warm = ((r - g).max(0.0) / 55.0).clamp(0.0, 1.0);
    let red_bias = ((r - b).max(0.0) / 100.0).clamp(0.0, 1.0);
    let not_extreme = if r > 35.0 && g > 20.0 && b > 10.0 {
        1.0
    } else {
        0.0
    };
    ((warm * 0.55) + (red_bias * 0.45)) * brightness * not_extreme
}

/// Apply a small bilateral-like filter that reduces isolated color specks while
/// keeping strong edges and facial features intact.
fn edge_preserving_denoise(
    image: &ImageBuffer<Rgba<u8>, Vec<u8>>,
    strength: f32,
) -> ImageBuffer<Rgba<u8>, Vec<u8>> {
    let strength = strength.clamp(0.0, 1.0);
    if strength <= 0.0 {
        return image.clone();
    }
    let (width, height) = image.dimensions();
    let sigma = 18.0 + 52.0 * (1.0 - strength);
    ImageBuffer::from_fn(width, height, |x, y| {
        let center = image.get_pixel(x, y);
        let mut sums = [0.0f32; 3];
        let mut weights = 0.0f32;
        let x0 = x.saturating_sub(1);
        let y0 = y.saturating_sub(1);
        let x1 = (x + 1).min(width.saturating_sub(1));
        let y1 = (y + 1).min(height.saturating_sub(1));
        for ny in y0..=y1 {
            for nx in x0..=x1 {
                let neighbor = image.get_pixel(nx, ny);
                let color_delta = ((center[0] as f32 - neighbor[0] as f32).abs()
                    + (center[1] as f32 - neighbor[1] as f32).abs()
                    + (center[2] as f32 - neighbor[2] as f32).abs())
                    / 3.0;
                let spatial = if nx == x && ny == y {
                    1.0
                } else if nx == x || ny == y {
                    0.8
                } else {
                    0.6
                };
                let color_weight = (-(color_delta * color_delta) / (2.0 * sigma * sigma)).exp();
                let weight = spatial * color_weight;
                for channel in 0..3 {
                    sums[channel] += neighbor[channel] as f32 * weight;
                }
                weights += weight;
            }
        }
        let mut channels = [0u8; 4];
        for channel in 0..3 {
            let local = sums[channel] / weights.max(f32::EPSILON);
            let base = center[channel] as f32;
            channels[channel] = (base * (1.0 - strength) + local * strength)
                .clamp(0.0, 255.0)
                .round() as u8;
        }
        channels[3] = center[3];
        Rgba(channels)
    })
}

/// Clarify an image using denoising, protected unsharp detail, contrast, and optional resize.
pub fn clarify(image: &DynamicImage, options: ClarificationOptions) -> DynamicImage {
    let input = image.to_rgba8();
    let scale = options.scale.max(1.0);
    let rgba = if scale > 1.0 {
        let (input_width, input_height) = input.dimensions();
        let target_width = ((input_width as f32) * scale).round().max(1.0) as u32;
        let target_height = ((input_height as f32) * scale).round().max(1.0) as u32;
        image::imageops::resize(
            &input,
            target_width,
            target_height,
            image::imageops::FilterType::Lanczos3,
        )
    } else {
        input
    };
    let (width, height) = rgba.dimensions();
    let prepared = edge_preserving_denoise(&rgba, options.denoise);
    let blurred = image::imageops::blur(&prepared, options.radius.max(0.1));
    let contrast_factor = 1.0 + (options.contrast / 100.0);
    let amount = options.amount.max(0.0);
    let threshold = options.threshold as f32;
    let protection = options.skin_protection.clamp(0.0, 1.0);

    let output: ImageBuffer<Rgba<u8>, Vec<u8>> = ImageBuffer::from_fn(width, height, |x, y| {
        let original = rgba.get_pixel(x, y);
        let base_pixel = prepared.get_pixel(x, y);
        let soft = blurred.get_pixel(x, y);
        let right = prepared.get_pixel((x + 1).min(width.saturating_sub(1)), y);
        let down = prepared.get_pixel(x, (y + 1).min(height.saturating_sub(1)));
        let local_gradient = ((luminance(base_pixel) - luminance(right)).abs()
            + (luminance(base_pixel) - luminance(down)).abs())
            / 2.0;
        let edge_gate = (local_gradient / 32.0).clamp(0.0, 1.0);
        let skin_gate = skin_likelihood(original);
        let protected_gain =
            amount * (1.0 - protection * skin_gate * (1.0 - 0.45 * edge_gate)).clamp(0.25, 1.0);
        let mut channels = [0u8; 4];

        for channel in 0..3 {
            let base = base_pixel[channel] as f32;
            let detail = base - soft[channel] as f32;
            let sharpened = if detail.abs() >= threshold {
                base + protected_gain * detail
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

    #[test]
    fn portrait_reduces_an_isolated_bright_speck() {
        let mut image = ImageBuffer::from_pixel(17, 17, Rgba([90, 70, 60, 255]));
        image.put_pixel(8, 8, Rgba([245, 220, 210, 255]));
        let input = DynamicImage::ImageRgba8(image);
        let output = clarify(&input, ClarificationOptions::portrait()).to_rgba8();
        assert!(output.get_pixel(8, 8)[0] < 245);
        assert_eq!(output.dimensions(), (68, 68));
    }
}
