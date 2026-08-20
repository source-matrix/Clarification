// Package clarification provides a Go bridge to the Clarification CLI.
package clarification

import (
	"fmt"
	"os/exec"
	"strconv"
	"strings"
)

// Options mirrors the Rust engine's parameters.
type Options struct {
	Radius         float32
	Amount         float32
	Contrast       float32
	Threshold      uint8
	Scale          float32
	Denoise        float32
	SkinProtection float32
}

// DefaultOptions returns production-friendly defaults.
func DefaultOptions() Options {
	return Options{Radius: 1.2, Amount: 1.35, Contrast: 8.0, Threshold: 2, Scale: 1.0, Denoise: 0.12, SkinProtection: 0.25}
}

// PortraitOptions returns the portrait profile for blemish reduction and face protection.
func PortraitOptions() Options {
	return Options{Radius: 0.15, Amount: 6.0, Contrast: 10.0, Threshold: 1, Scale: 4.0, Denoise: 0.02, SkinProtection: 0.72}
}

// Enhance runs the Clarification binary on an input and output path.
func Enhance(binary, input, output string, options Options) error {
	if binary == "" || input == "" || output == "" {
		return fmt.Errorf("binary, input, and output are required")
	}
	args := []string{
		"clarify", input, output,
		"--radius", strconv.FormatFloat(float64(options.Radius), 'f', -1, 32),
		"--amount", strconv.FormatFloat(float64(options.Amount), 'f', -1, 32),
		"--contrast", strconv.FormatFloat(float64(options.Contrast), 'f', -1, 32),
		"--threshold", strconv.Itoa(int(options.Threshold)),
		"--scale", strconv.FormatFloat(float64(maxScale(options.Scale)), 'f', -1, 32),
		"--denoise", strconv.FormatFloat(float64(clamp01(options.Denoise)), 'f', -1, 32),
		"--skin-protection", strconv.FormatFloat(float64(clamp01(options.SkinProtection)), 'f', -1, 32),
	}
	command := exec.Command(binary, args...)
	if outputBytes, err := command.CombinedOutput(); err != nil {
		return fmt.Errorf("clarification failed: %w: %s", err, outputBytes)
	}
	return nil
}

func maxScale(value float32) float32 {
	if value < 1.0 {
		return 1.0
	}
	return value
}

func clamp01(value float32) float32 {
	if value < 0 {
		return 0
	}
	if value > 1 {
		return 1
	}
	return value
}

// EnhanceAI runs the optional clarification-ai backend with the portrait eye-detail profile.
// The model weights remain outside the Go package and are supplied explicitly by the caller.
func EnhanceAI(command, input, output, realesrganWeights, gfpganWeights string, faceWeight float32, tile int) error {
	return EnhanceAIWithEyeBlend(command, input, output, realesrganWeights, gfpganWeights, faceWeight, 0.65, tile)
}

// EnhanceAIWithEyeBlend exposes the conservative eye-detail blend used by portrait.
func EnhanceAIWithEyeBlend(command, input, output, realesrganWeights, gfpganWeights string, faceWeight, eyeBlend float32, tile int) error {
	if command == "" || input == "" || output == "" || realesrganWeights == "" || gfpganWeights == "" {
		return fmt.Errorf("command, input, output, and model weights are required")
	}
	if tile < 0 {
		tile = 0
	}
	args := []string{
		input,
		output,
		"--realesrgan-weights", realesrganWeights,
		"--gfpgan-weights", gfpganWeights,
		"--face-weight", strconv.FormatFloat(float64(clamp01(faceWeight)), 'f', -1, 32),
		"--eye-blend", strconv.FormatFloat(float64(clamp01(eyeBlend)), 'f', -1, 32),
		"--tile", strconv.Itoa(tile),
	}
	if outputBytes, err := exec.Command(command, args...).CombinedOutput(); err != nil {
		return fmt.Errorf("AI clarification failed: %w: %s", err, outputBytes)
	}
	return nil
}

// Score returns the CLI's local-detail score for an image.
func Score(binary, input string) (float64, error) {
	output, err := exec.Command(binary, "score", input).Output()
	if err != nil {
		return 0, fmt.Errorf("score failed: %w", err)
	}
	score, err := strconv.ParseFloat(strings.TrimSpace(string(output)), 64)
	if err != nil {
		return 0, fmt.Errorf("invalid score: %w", err)
	}
	return score, nil
}
