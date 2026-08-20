from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

root = Path(__file__).resolve().parent
size = 256
image = Image.new("RGB", (size, size), (105, 108, 112))
draw = ImageDraw.Draw(image)
draw.rectangle((24, 24, 232, 232), outline=(188, 190, 192), width=3)
draw.ellipse((58, 58, 198, 198), outline=(214, 214, 214), width=4)
draw.line((28, 204, 228, 44), fill=(232, 190, 90), width=4)
draw.text((78, 116), "CLARIFY", fill=(235, 235, 235))
image = image.filter(ImageFilter.GaussianBlur(2.4))
image.save(root / "fixtures" / "input.png")
