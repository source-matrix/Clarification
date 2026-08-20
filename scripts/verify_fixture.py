from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
src = Image.open(root / "tests" / "fixtures" / "input.png")
out = Image.open("/tmp/clarification-final.png")
assert src.size == out.size, (src.size, out.size)
if "A" in src.mode:
    assert "A" in out.mode, (src.mode, out.mode)
    assert list(src.getchannel("A").getdata()) == list(out.getchannel("A").getdata())
else:
    assert "A" in out.mode, out.mode
    assert min(out.getchannel("A").getdata()) == 255
print(f"dimensions={out.size[0]}x{out.size[1]}")
print(f"input_mode={src.mode}")
print(f"output_mode={out.mode}")
print("alpha_semantics=preserved")
