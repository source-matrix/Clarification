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
    options=AIOptions.portrait(),
)
```

أو من سطر الأوامر:

```bash
clarification-ai input.jpg output-ai.png \
  --realesrgan-weights "$REALESRGAN_WEIGHTS" \
  --gfpgan-weights "$GFPGAN_WEIGHTS" \
  --face-weight 0.50 \
  --eye-blend 0.65 \
  --tile 128
```

ملف `AIOptions.portrait()` يستخدم `face_weight=0.50` مع `eye_blend=0.65`: يرمم الوجه عبر GFPGAN ثم يمزج تفاصيل العينين من مسار Real-ESRGAN المحافظ داخل قناع landmarks ضيق. رفع أي قيمة أكثر قد يعطي تفاصيل أقوى، لكنه يزيد خطر التجميل أو تغيير الملامح؛ خفض `eye_blend` إلى `0` يعطّل مزج العينين.

## Rust وGo وLua

تبقى النواة Rust مسؤولة عن المسار الحتمي. ويشغّل CLI الأمر الخارجي عند طلب AI صراحةً:

```bash
clarification ai input.jpg output-ai.png \
  --realesrgan-weights /models/RealESRGAN_x4plus.pth \
  --gfpgan-weights /models/GFPGANv1.4.pth \
  --face-weight 0.50 \
  --eye-blend 0.65 \
  --tile 128
```

تستطيع واجهة Go استخدام `EnhanceAI`، وتستطيع واجهة Lua استخدام `enhance_ai`. كلتاهما تمرران مسارات الأوزان وخيارات profile إلى الأمر الخارجي ولا تخزنان الأوزان داخل الحزمة.

## الاختبار الذي أُجري

استُخدمت صورة اختبار منخفضة الدقة بمقاس 447×447، وشُغّلت مسارات Real-ESRGAN وحده، وGFPGAN بوزن 0.50، وprofile portrait النهائي مع `eye_blend=0.65`. كما أُنشئت شبكة مقارنة ومقاييس PSNR وSSIM ودرجة حدة محلية، ثم جرى فحص الصور بصريًا من حيث القرب من المرجع وحفظ الهوية والهلوسة.

أظهر Real-ESRGAN وحده حدة عددية أعلى قليلًا، لكنه لا يرمم الوجه. أما GFPGAN بوزن 0.50 فيحسن بنية الوجه، ويضيف profile العينين المحافظ تفاصيل القزحية والبؤبؤ والانعكاس مع إبقاء الجلد والجفون تحت سيطرة ترميم الوجه. يجب إعادة الفحص البصري بعد كل تغيير لأن قرب الصورة لا يُحسم بوزن واحد.

في القياس الآلي الحالي على زوج الاختبار، سجل GFPGAN بوزن 0.50 حدة محلية `52.9539` وPSNR `25.7890` وSSIM `0.7547`، بينما سجل Real-ESRGAN فقط حدة `64.8688` وPSNR `25.9805` وSSIM `0.7586`. هذه الأرقام لا تقيس واقعية القزحية وحدها؛ لذلك استُخدمت مع الفحص البصري الموضعي، لا بدلًا منه.

## قرار الاعتماد

بعد فحص profile الجديد بمقاس 2048×2048، يُعتمد `AIOptions.portrait()` كنقطة البداية لتحسين تفاصيل العينين، ولا يُعتمد أي إخراج نهائي قبل فحص القزحية والبؤبؤ والانعكاس بصريًا. النتيجة أقرب بوضوح إلى المرجع من التكبير التقليدي، وتحافظ على التكوين والهوية العامة، لكنها لا تضمن أن كل رمش أو شعرة أو نسيج في القبعة كان موجودًا في المصدر. لهذا السبب يبقى backend AI اختياريًا، ويظل المسار التقليدي متاحًا للمستخدم الذي يريد عدم توليد تفاصيل جديدة.

## التدريب المخصص

لم يُدرَّب نموذج من الصفر داخل بيئة الاختبار؛ الذي استُخدم هو نموذج عام جاهز مع ترميم وجه اختياري. التدريب الحقيقي يحتاج أزواجًا مرخّصة من الصور عالية ومنخفضة الجودة، بالإضافة إلى GPU ووقت تدريب ومقاييس تحقق مستقلة. توفر صفحة DIV2K أزواجًا مناسبة للبحث، لكن شروط استخدامها يجب احترامها ولا تُنسخ الصور إلى مستودع عام دون مراجعة الترخيص [1]. يوفر Real-ESRGAN مسارًا رسميًا للتدريب على بيانات مخصصة [2].

### المراجع

[1]: https://data.vision.ee.ethz.ch/cvl/DIV2K/ "صفحة بيانات DIV2K الرسمية"
[2]: https://github.com/xinntao/Real-ESRGAN "المستودع الرسمي لـ Real-ESRGAN"
[3]: https://github.com/TencentARC/GFPGAN "المستودع الرسمي لـ GFPGAN"
[4]: https://onnxruntime.ai/docs/tutorials/mobile/superres.html "دليل ONNX Runtime لتشغيل Super-Resolution"
