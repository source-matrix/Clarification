from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs" / "assets"

input_image = Image.open(ASSETS / "input.png").convert("RGB")
output_image = Image.open(ASSETS / "clarified.png").convert("RGB")
width, height = input_image.size
margin = 28
label_height = 46
canvas = Image.new("RGB", (width * 2 + margin * 3, height + label_height + margin * 2), "#101827")
draw = ImageDraw.Draw(canvas)
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
font = ImageFont.truetype(font_path, 20)
small = ImageFont.truetype(font_path, 15)

left_x = margin
right_x = margin * 2 + width
image_y = label_height + margin
canvas.paste(input_image, (left_x, image_y))
canvas.paste(output_image, (right_x, image_y))
draw.text((left_x, margin), "Before", fill="#dbeafe", font=font)
draw.text((right_x, margin), "After · Clarification", fill="#86efac", font=font)
draw.text((margin, image_y + height + 8), "Same dimensions · RGBA preserved · controlled fixture", fill="#94a3b8", font=small)
canvas.save(ASSETS / "clarification-fixture.png", optimize=True)
