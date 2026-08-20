# مصادر بيانات ونماذج لمسار AI super-resolution

تم العثور على المصادر التالية أثناء البحث الأولي في 20 أغسطس 2026:

| المصدر | الاستخدام | ملاحظة الترخيص/الموثوقية |
|---|---|---|
| [DIV2K الرسمي](https://data.vision.ee.ethz.ch/cvl/DIV2K/) | صور عالية الدقة لتدريب واختبار single-image super-resolution | المصدر الأكاديمي الرسمي لبيانات DIV2K؛ يجب قراءة شروط الاستخدام قبل إعادة التوزيع. |
| [TensorFlow Datasets: DIV2K](https://www.tensorflow.org/datasets/catalog/div2k) | تنزيل/تجهيز DIV2K بطريقة قابلة لإعادة الإنتاج | صفحة موثقة تذكر تقسيم البيانات وتفاصيل الحزمة؛ لا يُفترض إعادة نشر الصور داخل المستودع دون مراجعة الشروط. |
| [Real-ESRGAN الرسمي](https://github.com/xinntao/Real-ESRGAN) | نموذج واستدلال عملي للصور الواقعية | يجب استخدام الأوزان الرسمية ومراجعة LICENSE قبل تضمين أو توزيع أي وزن. |
| [Real-ESRGAN x4plus على Hugging Face](https://huggingface.co/amd/realesrgan-x4plus) | مصدر محتمل لوزن جاهز للاستدلال | صفحة النموذج تشير إلى BSD 3-Clause؛ يجب الاحتفاظ بنسخة الترخيص وبيانات المصدر مع أي توزيع. |
| [ONNX Runtime super-resolution tutorial](https://onnxruntime.ai/docs/tutorials/mobile/superres.html) | مرجع لتشغيل نموذج SR بصيغة ONNX | مسار مناسب لتصميم backend اختياري لا يفرض إطار تعلم عميق على نواة Rust الأساسية. |
| [ONNX Model Zoo](https://github.com/onnx/models) | نماذج ONNX مرجعية | مصدر رسمي لمجموعة نماذج؛ يلزم فحص ترخيص كل نموذج على حدة. |

## قرار أولي

لن تُضمّن صور DIV2K أو أوزان النماذج داخل مستودع Clarification تلقائيًا. سيُضاف مسار تنزيل/تحقق اختياري مع حفظ checksum ورابط الترخيص، ويُستخدم نموذج AI للاختبار المحلي فقط بعد التأكد من مصدره. صورة الطفلة تُستخدم كفحص بصري يدوي، لا كبيانات تدريب أو ground truth منشورة.

## ملاحظات التحقق من الصفحات الرسمية

توضح صفحة DIV2K الرسمية أن البيانات موجهة للبحث الأكاديمي فقط، وأن حقوق الصور تعود إلى ملاكها الأصليين؛ لذلك لن تُضمّن الصور في مستودع عام أو تدريب موزع دون مراجعة الشروط [1]. كما توضح الصفحة أن هناك أزواجًا HR/LR لعوامل تصغير x2 وx3 وx4، مع مسارات bicubic وunknown degradation، وهو مناسب لتقييم الاستدلال دون استخدام صورة الطفلة كحقيقة أرضية.

يذكر مستودع Real-ESRGAN الرسمي أن المشروع مخصص لاستعادة الصور والفيديو الواقعيين، وأن لديه نماذج عامة مثل `realesrgan-x4plus`، وخيار `--face_enhance`، ودعم التدريب على بيانات مخصصة. كما يوفر تنفيذًا محمولًا لا يحتاج إلى PyTorch أو CUDA، لكن الأوزان والشفرة يجب أن تبقى مرتبطة بالمصدر والترخيص الأصلي [2].

يوضح دليل ONNX Runtime الرسمي أن نموذج super-resolution يمكن تصديره إلى ONNX وتشغيله عبر ONNX Runtime، مع توصية باستخدام opset 18 ونسخ حديثة من onnx وonnxruntime، ما يدعم تصميم backend اختياري مستقل عن نواة Rust [3].

[1]: https://data.vision.ee.ethz.ch/cvl/DIV2K/
[2]: https://github.com/xinntao/Real-ESRGAN
[3]: https://onnxruntime.ai/docs/tutorials/mobile/superres.html

## توسيع مجموعة الاختبار

تؤكد صفحة DIV2K الرسمية أن المجموعة تتكون من 1000 صورة عالية الدقة موزعة إلى 800 تدريب و100 تحقق و100 اختبار، مع أزواج HR/LR لعوامل التصغير [1]. ستُستخدم عينات التحقق محليًا فقط إذا نُزّلت، ولن تُنسخ ملفات الصور إلى المستودع العام. نتائج DIV2K تقيس جودة super-resolution العامة، لكنها لا تثبت وحدها جودة ترميم الوجوه.

[1]: https://data.vision.ee.ethz.ch/cvl/DIV2K/ "صفحة DIV2K الرسمية"

## تصحيح روابط الأوزان

الرابط القديم لإصدار Real-ESRGAN أعاد 404. صفحة المستودع الرسمي الحالية تشير إلى تنزيل `RealESRGAN_x4plus.pth` من إصدار `v0.1.0`: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth. كما أن صفحة GFPGAN الرسمية تشير إلى روابط الأوزان من مستودع TencentARC: https://github.com/TencentARC/GFPGAN/releases، وتبقى الأوزان خارج مستودع Clarification. تمت مراجعة هذه الروابط في 20 أغسطس 2026.
