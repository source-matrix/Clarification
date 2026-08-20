from __future__ import annotations

import base64
import json
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
INPUT = Path('/home/ubuntu/upload/images.jpeg')
REFERENCE = Path('/home/ubuntu/upload/1787205842197-01a01dc4-3f37-75ef-9f0d-f8ed14981081.jpeg')
README = ROOT / 'README.md'


def data_url(path: Path) -> str:
    suffix = path.suffix.lower()
    mime = 'image/png' if suffix == '.png' else 'image/jpeg'
    encoded = base64.b64encode(path.read_bytes()).decode('ascii')
    return f'data:{mime};base64,{encoded}'


client = OpenAI()
content = [
    {
        'type': 'text',
        'text': (
            'أنت مهندس رؤية حاسوبية ومراجع جودة لمكتبة مفتوحة المصدر اسمها Clarification. '
            'المطلوب ترقية المكتبة من مرشحات تقليدية إلى مسار اختياري حقيقي لـ AI super-resolution، '
            'مع الحفاظ على هوية الوجه وعدم اختلاق ملامح غير موثوقة. راجع README التالي، ثم قارن بصريًا '
            'بين صورة الإدخال منخفضة الدقة وصورة المرجع عالية الدقة. أخرج تقريرًا عمليًا بالعربية يتضمن: '
            '1) تقييم الفجوة بين الناتج الحالي والمرجع، 2) أفضل بنية قابلة للصيانة لدعم Rust وPython وGo وLua، '
            '3) خطة ملفات وواجهات API، 4) اختبارات موضوعية للمقارنة، 5) مخاطر الهلوسة وطرق الحد منها، '
            '6) معايير قبول واضحة. لا تدّع أن Lanczos أو Unsharp هو AI، ولا تقترح تنزيل نموذج غير مرخص. '
            'README الحالي:\n\n' + README.read_text(encoding='utf-8')
        ),
    },
    {'type': 'text', 'text': 'صورة الإدخال الأصلية منخفضة الدقة:'},
    {'type': 'image_url', 'image_url': {'url': data_url(INPUT), 'detail': 'high'}},
    {'type': 'text', 'text': 'صورة المرجع عالية الدقة المراد الاقتراب منها:'},
    {'type': 'image_url', 'image_url': {'url': data_url(REFERENCE), 'detail': 'high'}},
]

response = client.chat.completions.create(
    model='claude-opus-4-7',
    messages=[
        {
            'role': 'system',
            'content': 'اكتب تقريرًا هندسيًا دقيقًا، ولا تنسب للمكتبة قدرات لم تُنفّذ بعد.',
        },
        {'role': 'user', 'content': content},
    ],
    max_tokens=8000,
)

result = response.choices[0].message.content or ''
out = ROOT / 'docs' / 'guides' / 'claude-opus-ai-upgrade-review.md'
out.write_text(
    '# مراجعة Claude Opus 4.7 لمسار AI super-resolution\n\n'
    '> هذا التقرير استشارة هندسية لتصميم التنفيذ والاختبار، وليس دليلًا على أن النموذج نفسه عالج الصور.\n\n'
    + result + '\n',
    encoding='utf-8',
)
print(json.dumps({'output': str(out), 'model': 'claude-opus-4-7', 'usage': response.usage.model_dump()}, ensure_ascii=False, indent=2))
