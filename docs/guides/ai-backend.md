# AI Super-Resolution Backend

يوفر Clarification مسارين مستقلين. المسار الأساسي يعمل محليًا بالنواة Rust أو بواجهة Pillow ولا يحتاج إلى أوزان خارجية. المسار الاختياري `ai` يستخدم **Real-ESRGAN** لتكبير واقعي و**GFPGAN** لترميم الوجه، ويُشغَّل كـ backend خارجي لأن تضمين PyTorch والأوزان داخل المكتبة الأساسية سيجعل التثبيت كبيرًا وغير مناسب لكل جهاز.

> **تنبيه دقة:** النموذج AI يولّد تفاصيل مرجّحة من الأنماط التي تعلمها. لا يمكن اعتبار الرموش أو القزحية أو نسيج الشعر الناتج حقيقة مستعادة من الصورة الأصلية، لذلك يجب استخدام `face_weight` محافظًا وفحص الهوية بصريًا.

## التثبيت الاختياري

```bash
python -m pip install -e './bindings/python[ai]'
```

يجب تنزيل أوزان النموذج من مصادرها الرسمية وحفظها خارج المستودع. لا يحمّل Clarification الأوزان تلقائيًا:

```bash
export REALESRGAN_WEIGHTS=/path/to/RealESRGAN_x4plus.pth
export GFPGAN_WEIGHTS=/path/to/GFPGANv1.4.pth
```

## Python

```python
from clarification import AIOptions, clarify_ai_file

clarify_ai_file(
    'input.jpg',
    'output-ai.png',
    realesrgan_weights='/models/RealESRGAN_x4plus.pth',
    gfpgan_weights='/models/GFPGANv1.4.pth',
    options=AIOptions(tile=128, face_weight=0.25),
)
```

أو من سطر الأوامر:

```bash
clarification-ai input.jpg output-ai.png \
  --realesrgan-weights "$REALESRGAN_WEIGHTS" \
  --gfpgan-weights "$GFPGAN_WEIGHTS" \
  --face-weight 0.25 \
  --tile 128
```

القيمة `face_weight=0.25` هي الإعداد المحافظ الذي اختُبر على صورة portrait؛ رفعها إلى `0.50` يعطي وجهًا أكثر صقلًا لكنه يزيد خطر التجميل وتغيير الملامح.

## Rust وGo وLua

تبقى النواة Rust مسؤولة عن المسار الحتمي. ويشغّل CLI الأمر الخارجي عند طلب AI صراحةً:

```bash
clarification ai input.jpg output-ai.png \
  --realesrgan-weights /models/RealESRGAN_x4plus.pth \
  --gfpgan-weights /models/GFPGANv1.4.pth \
  --face-weight 0.25 \
  --tile 128
```

تستطيع واجهة Go استخدام `EnhanceAI`، وتستطيع واجهة Lua استخدام `enhance_ai`. كلتاهما تمرران مسارات الأوزان إلى الأمر الخارجي ولا تخزنانها داخل الحزمة.

## الاختبار الذي أُجري

استُخدمت صورة اختبار منخفضة الدقة بمقاس 447×447، وشُغّلت ثلاثة مسارات: Real-ESRGAN وحده، وGFPGAN بوزن 0.25، وGFPGAN بوزن 0.50. كما أُنشئت شبكة مقارنة ومقاييس PSNR وSSIM ودرجة حدة محلية، ثم راجع Claude Opus 4.7 الصور بصريًا من حيث القرب من المرجع وحفظ الهوية والهلوسة.

خلص التقييم إلى أن GFPGAN بوزن 0.25 هو أفضل المرشحين، بدرجة قرب بصرية 7.5/10 وحفظ هوية 7.5/10. أما Real-ESRGAN وحده فزاد الحدة لكنه أدخل تغييرات واضحة في العينين والقبعة والبشرة، ولذلك لم يُعتمد كإعداد portrait النهائي.

في القياس الآلي على زوج الاختبار، كانت درجة الحدة المحلية `85.57` لمسار GFPGAN-0.25 مقابل `5.37` للمسار التقليدي، بينما بلغ SSIM بالنسبة إلى المرجع `0.7766` لمسار GFPGAN-0.25 و`0.7909` للمسار التقليدي. هذا لا يعني أن المسار التقليدي أفضل بصريًا؛ فالمرجع والنسخ الناتجة مختلفة في الأبعاد والترميز، كما أن SSIM يعاقب أحيانًا التفاصيل المولدة التي تجعل الصورة أكثر وضوحًا. لذلك استُخدمت الأرقام مع الفحص البصري المستقل، لا بدلًا منه.

## قرار الاعتماد

بعد فحص `clarification-ai-final.png` بمقاس 2048×2048، اعتُمد إعداد GFPGAN المحافظ `face_weight=0.25` كأفضل نتيجة حالية. النتيجة أقرب بوضوح إلى المرجع من التكبير التقليدي، وتحافظ على التكوين والهوية العامة، لكنها لا تضمن أن كل رمش أو شعرة أو نسيج في القبعة كان موجودًا في المصدر. لهذا السبب يبقى backend AI اختياريًا، ويظل المسار التقليدي متاحًا للمستخدم الذي يريد عدم توليد تفاصيل جديدة.

## التدريب المخصص

لم يُدرَّب نموذج من الصفر داخل بيئة الاختبار؛ الذي استُخدم هو نموذج عام جاهز مع ترميم وجه اختياري. التدريب الحقيقي يحتاج أزواجًا مرخّصة من الصور عالية ومنخفضة الجودة، بالإضافة إلى GPU ووقت تدريب ومقاييس تحقق مستقلة. توفر صفحة DIV2K أزواجًا مناسبة للبحث، لكن شروط استخدامها يجب احترامها ولا تُنسخ الصور إلى مستودع عام دون مراجعة الترخيص [1]. يوفر Real-ESRGAN مسارًا رسميًا للتدريب على بيانات مخصصة [2].

### المراجع

[1]: https://data.vision.ee.ethz.ch/cvl/DIV2K/ "صفحة بيانات DIV2K الرسمية"
[2]: https://github.com/xinntao/Real-ESRGAN "المستودع الرسمي لـ Real-ESRGAN"
[3]: https://github.com/TencentARC/GFPGAN "المستودع الرسمي لـ GFPGAN"
[4]: https://onnxruntime.ai/docs/tutorials/mobile/superres.html "دليل ONNX Runtime لتشغيل Super-Resolution"
