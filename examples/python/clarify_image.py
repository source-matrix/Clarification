from clarification import Options, clarify_file, sharpness_score

input_path = "input.png"
output_path = "clarified.png"

before = sharpness_score(input_path)
clarify_file(input_path, output_path, Options(amount=1.5, contrast=10.0))
after = sharpness_score(output_path)
print(f"sharpness: {before:.4f} -> {after:.4f}")
