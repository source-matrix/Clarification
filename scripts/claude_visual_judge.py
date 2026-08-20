from __future__ import annotations

import base64
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ('Input 447x447', Path('/home/ubuntu/upload/images.jpeg')),
    ('Real-ESRGAN x4', ROOT / '.cache/realesrgan/results/clarification-ai-x4.png'),
    ('GFPGAN weight 0.25', ROOT / '.cache/realesrgan/results/clarification-ai-gfpgan-w025.png'),
    ('GFPGAN weight 0.50', ROOT / '.cache/realesrgan/results/clarification-ai-gfpgan.png'),
    ('Reference 2048x2048', Path('/home/ubuntu/upload/1787205842197-01a01dc4-3f37-75ef-9f0d-f8ed14981081.jpeg')),
]


def data_url(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:image/{path.suffix.lstrip(".").lower()};base64,{encoded}'


content = [
    {
        'type': 'text',
        'text': (
            'راجع هذه المجموعة كمحكّم جودة مستقل. الهدف ليس اختيار الصورة الأكثر حدة فقط، بل اختيار '
            'ناتج AI يشبه المرجع في التكوين والوجه والشعر والقبعة، مع أقل تغيير غير مبرر في هوية الشخص. '
            'قارن كل نسخة بالمرجع، واذكر بوضوح: ترتيب المرشحين، درجة القرب من 10، درجة الحفاظ على الهوية من 10، '
            'مؤشرات الهلوسة، وهل النتيجة مرضية للاستخدام العملي أم لا. لا تعتبر المرجع حقيقة أرضية؛ هو مرجع بصري فقط. '
            'أخرج تقريرًا بالعربية منظمًا بعناوين وجدول وحكم نهائي صريح، ولا تدّع أن أي تفاصيل مولّدة هي حقيقة أصلية.'
        ),
    }
]
for label, path in FILES:
    content.append({'type': 'text', 'text': label})
    content.append({'type': 'image_url', 'image_url': {'url': data_url(path), 'detail': 'high'}})

client = OpenAI()
response = client.chat.completions.create(
    model='claude-opus-4-7',
    messages=[
        {'role': 'system', 'content': 'أنت مراجع صور صريح، ولا تمنح قبولًا إذا ظهرت هلوسة واضحة أو تغيير هوية.'},
        {'role': 'user', 'content': content},
    ],
    max_tokens=4500,
)
report = response.choices[0].message.content or ''
out = ROOT / 'docs/guides/claude-visual-evaluation.md'
out.write_text('# تقييم Claude Opus 4.7 البصري للنتائج\n\n' + report + '\n', encoding='utf-8')
print(out)
