from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bindings/python'))

from clarification.ai import AIOptions, clarify_ai_file

clarify_ai_file(
    ROOT / 'docs/assets/before-after/before.jpeg',
    Path('/tmp/clarification-ai-eye-blend.png'),
    Path('/tmp/clarification-models/RealESRGAN_x4plus.pth'),
    Path('/tmp/clarification-models/GFPGANv1.4.pth'),
    AIOptions.portrait(),
)
print('created /tmp/clarification-ai-eye-blend.png')
