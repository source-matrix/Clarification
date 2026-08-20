# مراجعة Claude Opus 4.7 لمسار AI super-resolution

> هذا التقرير استشارة هندسية لتصميم التنفيذ والاختبار، وليس دليلًا على أن النموذج نفسه عالج الصور.

# تقرير هندسي: ترقية مكتبة Clarification لدعم مسار AI Super-Resolution اختياري

**المُعِدّ:** مراجعة هندسة رؤية حاسوبية وضمان جودة
**النطاق:** تقييم الفجوة الحالية، واقتراح بنية قابلة للصيانة عبر Rust/Python/Go/Lua، مع الحفاظ على هوية الوجه ومنع الهلوسة.

---

## 1) تقييم الفجوة بين الناتج الحالي والمرجع

### 1.1 ما تفعله المكتبة اليوم فعليًا (بحسب README والكود المشار إليه)
- نواة Rust تنفّذ: **Unsharp Mask** بنصف قطر `radius` وقوة `amount`، وضبط تباين محلي بنسبة مئوية (`contrast`)، وعتبة `threshold`.
- تكبير عبر **Lanczos** عندما تكون `scale > 1.0` (البروفايل `portrait` يستخدم ‎4× Lanczos).
- تقليل بقع معزولة (`denoise`) وحماية بشرة بسيطة قائمة على اللون/التدرج (`skin-protection`).
- مقياس محلي خفيف لـ "detail score" (يظهر أنه مقياس تباين/تدرج محلي وليس مقياس جودة إدراكيّ).

هذه كلها **عمليات إشارة تقليدية Deterministic DSP**. لا يوجد أي نموذج تعلّم عميق في المسار الحالي. أي وصف يوحي بأن هذا "super-resolution بالذكاء الاصطناعي" سيكون غير دقيق ويجب تجنّبه في التسويق والوثائق.

### 1.2 الفجوة البصرية بين إدخال ‎448×448 تقريبًا ومرجع ‎2048×2048 تقريبًا

| المحور | الإدخال منخفض الدقة | المرجع عالي الدقة | الفجوة التي لا يستطيع Lanczos+Unsharp سدّها |
|---|---|---|---|
| الرموش والحواجب | كتلة داكنة بلا شعيرات مفردة | شعيرات مفردة مفصولة | معلومات ترددية عالية **مفقودة** في الإدخال؛ Unsharp يضخّم فقط ما هو موجود ولا يستطيع توليد شعيرات جديدة. |
| قزحية العين | تدرّج ناعم أزرق | ألياف قزحية شعاعية، انعكاسات محددة | يتطلّب استعادة تفاصيل غير موجودة → مهمة SR حقيقية. |
| نسيج قش القبعة | تكرار خشن بتشويش JPEG | ضفائر مضفورة واضحة + ثقوب سوداء منتظمة | نمط تكراري خفيف على حافة نايكويست؛ Lanczos يُبقيه ضبابيًا. |
| الشعر | كتل بنية مع aliasing | خصلات فردية بحواف نظيفة | يحتاج توليد ترددات عالية ذات اتساق موجّه. |
| الشفاه/البشرة | ناعم قليل التدرج | مسامّ خفيفة، حدود شفاه دقيقة | Unsharp يميل لإبراز ضوضاء JPEG قبل أن يبرز مسامًا حقيقية. |
| الخلفية (النافذة) | ألوان مطموسة | أطر واضحة، حواف مستقيمة | Lanczos يعطي حوافّ مستقيمة أنظف لكن دون استعادة تفاصيل الإطار. |

**الخلاصة:** المرجع يُظهر معلومات ترددية عالية **غير موجودة** في الإدخال (شعيرات، ألياف قزحية، نسيج قش). أي مرشح خطّي/غير خطّي محلي — بما في ذلك Lanczos وUnsharp وCLAHE — لن يسدّ هذه الفجوة مبدئيًّا. سدّها يتطلب **نموذج توليدي مُدرَّب** يُنشئ ترددات جديدة معقولة إحصائيًا. وهذا بالضبط ما يفتح باب **الهلوسة**، وهو ما يجب هندسته بحذر.

### 1.3 حكم عادل على الحالة الحالية
- ما تقدّمه المكتبة اليوم مقبول كطبقة **presentation enhancement** كما ينصّ README نفسه.
- المرجع المرفق في `docs/assets/before-after/` **لا يمكن اعتباره ground truth** يمكن الاقتراب منه بمرشحات تقليدية. ينبغي إعادة صياغة سطر التوصيف تحت الجدول ليؤكد أن الفارق في الأبعاد وترميز JPEG، **ومصدر المرجع نفسه** (على الأرجح خرج نموذج توليدي)، يجعل المطابقة البكسلية أو الملمسية غير قابلة للتحقيق دون AI حقيقي، وأن النتيجة لن تكون بالضرورة **نفس الشخص**.

> ⚠️ ملاحظة مهمة على المرجع المرفق ذاته: عند فحص العين والرموش والقزحية في صورة "بعد"، تظهر خصائص مميّزة لخرج نماذج SR/توليدية (ألياف قزحية شديدة الانتظام، ورموش متماثلة أكثر من الطبيعي). لذلك لا يجوز تقديمه على أنه "الحقيقة"، بل كتوجّه بصري فقط، مع تنبيه صريح بأنه قد يكون خرج نموذج ذاته.

---

## 2) أفضل بنية قابلة للصيانة لدعم Rust وPython وGo وLua

### 2.1 المبدأ التصميمي
- **نواة واحدة، مسارات اختيارية، عقد بيانات صارم.** Rust يبقى مصدر الحقيقة للـ DSP. طبقة SR تُضاف كـ **backend اختياري** خلف واجهة `trait` واحدة.
- **الاستدلال (Inference) لا يُنفَّذ في Rust ابتداءً** لأن أطر التعلّم العميق في Rust (`tract`, `ort`, `candle`) متفاوتة النضج ومكلفة الصيانة عبر منصّات متعددة. نستخدم بدلًا من ذلك **ONNX Runtime** كتنفيذ مرجعي، واستدعاءه من Rust عبر crate `ort` عندما يُبنى الميزة `--features onnx`.
- الروابط الأخرى (Python/Go/Lua) تستمر عبر CLI أو FFI، لكن **لا تكرر منطق SR**.

### 2.2 المخطط الطبقيّ

```
┌─────────────────────────────────────────────────────────────┐
│                     واجهات اللغات                            │
│   Rust API   │   Python (Pillow)   │   Go bridge   │  Lua   │
└──────┬───────┴──────────┬──────────┴───────┬───────┴────┬───┘
       │                  │                  │            │
       └──────────────────┴───── CLI ────────┴────────────┘
                              │
                    ┌─────────▼──────────┐
                    │ clarification-core │  (Rust)
                    │   Pipeline Orchestrator │
                    └─────────┬──────────┘
              ┌───────────────┼────────────────┐
              │               │                │
       ┌──────▼─────┐  ┌──────▼──────┐  ┌──────▼───────┐
       │  DSP ops   │  │ Face Guard  │  │ SR Backend   │
       │ (current)  │  │ (identity)  │  │  (trait)     │
       └────────────┘  └─────────────┘  └──────┬───────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                      ┌───────▼──────┐  ┌──────▼─────┐  ┌───────▼──────┐
                      │ Lanczos      │  │ ONNX (ort) │  │ External CLI │
                      │ (fallback,   │  │ optional   │  │ adapter      │
                      │  default)    │  │ feature    │  │ (user model) │
                      └──────────────┘  └────────────┘  └──────────────┘
```

### 2.3 قرارات جوهرية
1. **`SrBackend` trait** في `clarification-core` مع ثلاثة تنفيذات مبدئية:
   - `LanczosBackend` (الافتراضي، لا يعتمد شبكات).
   - `OnnxBackend` (خلف feature-flag `onnx`، يعتمد `ort`).
   - `ExternalBackend` (يستدعي ثنائيًّا خارجيًا يوفّره المستخدم؛ مفيد للـ Real-ESRGAN/GFPGAN المُثبّتة محليًا).
2. **إدارة النماذج**: المكتبة **لا تُنزّل** أي نموذج تلقائيًّا. يوفّر المستخدم مسار `.onnx` صراحةً عبر `--sr-model` أو متغيّر بيئة `CLARIFICATION_SR_MODEL`. يُوثَّق في `docs/guides/models.md` قائمة نماذج مقترحة **مع تراخيصها** ومسؤولية المستخدم في قبولها (مثال: Real-ESRGAN تحت BSD-3-Clause، GFPGAN تحت Apache-2.0 لكن يتطلّب فحص كل إصدار). لا يُدرج أي نموذج داخل المستودع أو الحزم.
3. **Face Guard وحدة مستقلّة**: تقارن embeddings الوجه قبل/بعد المعالجة وترفض الناتج إذا تجاوز الفارق عتبة معيّنة (تفصيل في القسم 5).
4. **CLI هو عقد الاستقرار عبر اللغات.** أي حقل جديد في `ClarificationOptions` يُضاف بشكل additive (Backwards compatible) مع قيم افتراضية آمنة.

---

## 3) خطة الملفات وواجهات API

### 3.1 التعديلات على شجرة المستودع

```text
Clarification/
├── crates/
│   ├── clarification-core/
│   │   ├── src/
│   │   │   ├── lib.rs
│   │   │   ├── options.rs                # امتداد ClarificationOptions
│   │   │   ├── dsp/                      # كل ما هو حالي (unsharp, contrast, denoise…)
│   │   │   ├── sr/
│   │   │   │   ├── mod.rs                # trait SrBackend
│   │   │   │   ├── lanczos.rs            # backend افتراضي
│   │   │   │   ├── onnx.rs               # خلف feature = "onnx"
│   │   │   │   └── external.rs           # adapter لثنائي خارجي
│   │   │   ├── face/
│   │   │   │   ├── mod.rs                # trait FaceGuard
│   │   │   │   ├── detect.rs             # كشف صندوق الوجه (اختياري)
│   │   │   │   └── identity.rs           # مقارنة embeddings + عتبات
│   │   │   └── pipeline.rs               # ترتيب DSP → SR → Face Guard → DSP نهائي
│   │   └── Cargo.toml                    # features: ["default", "onnx", "face-guard"]
│   └── clarification-cli/
│       └── src/main.rs                   # أعلام جديدة (انظر 3.3)
├── bindings/
│   ├── python/clarification/
│   │   ├── __init__.py                   # Options.sr(...), Options.face_guard(...)
│   │   └── sr.py                         # غلاف رفيع فوق CLI
│   ├── go/
│   │   └── sr.go                         # SROptions, FaceGuardOptions
│   └── lua/
│       └── clarification.lua             # حقول جديدة في defaults/portrait
├── docs/guides/
│   ├── sr.md                             # كيفية توفير نموذج ONNX
│   ├── models.md                         # قائمة نماذج مقترحة + التراخيص
│   ├── face-guard.md                     # كيفية عمل الحارس وحدوده
│   └── validation.md                     # مقاييس + بروتوكول القبول
└── tests/
    ├── fixtures/sr/                      # أزواج LR/HR مرخّصة صراحةً
    ├── rust/sr_lanczos.rs
    ├── rust/sr_onnx_gated.rs             # يعمل فقط إذا CLARIFICATION_SR_MODEL موجود
    ├── python/test_sr_cli.py
    └── objective/                        # سكربتات المقاييس (PSNR/SSIM/LPIPS/ArcFace)
```

### 3.2 امتداد `ClarificationOptions` (Rust)

```rust
#[derive(Debug, Clone)]
pub struct ClarificationOptions {
    // الحقول الحالية
    pub radius: f32,
    pub amount: f32,
    pub contrast: f32,
    pub threshold: u8,
    pub scale: f32,
    pub denoise: f32,
    pub skin_protection: f32,

    // جديد: مسار SR اختياري
    pub sr: Option<SrOptions>,
    pub face_guard: Option<FaceGuardOptions>,
}

#[derive(Debug, Clone)]
pub struct SrOptions {
    pub backend: SrBackendKind,     // Lanczos | Onnx | External
    pub model_path: Option<PathBuf>,// إلزامي لـ Onnx/External
    pub target_scale: f32,          // 2.0 أو 4.0
    pub tile: u32,                  // مثال 256، لتفادي OOM
    pub tile_overlap: u32,          // مثال 16
    pub device: SrDevice,           // Cpu | Cuda | CoreML (حسب ort features)
    pub fidelity: f32,              // 0.0..1.0 وزن مزج SR مع Lanczos
}

#[derive(Debug, Clone)]
pub struct FaceGuardOptions {
    pub enabled: bool,
    pub embedder_model: Option<PathBuf>, // ArcFace ONNX يوفّره المستخدم
    pub max_cosine_distance: f32,        // مثال 0.35
    pub on_violation: GuardAction,       // FallbackToLanczos | Reject | WarnOnly
}
```

القيم الافتراضية: `sr = None`، `face_guard = None`. السلوك الحالي للمكتبة **لا يتغيّر مطلقًا** لمن لا يفعّل الميزة.

### 3.3 امتداد CLI

```
clarification clarify input.png output.png \
  --preset portrait \
  --sr-backend onnx \
  --sr-model ~/models/realesrgan-x4.onnx \
  --sr-scale 4 \
  --sr-tile 256 --sr-tile-overlap 16 \
  --sr-fidelity 0.7 \
  --face-guard on \
  --face-embedder ~/models/arcface.onnx \
  --face-max-distance 0.35 \
  --on-guard-violation fallback-lanczos
```

قواعد صارمة:
- إذا `--sr-backend onnx` ولم يُبنَ المشروع بـ `--features onnx`، ترجع رسالة خطأ واضحة **لا صمت ولا إسقاط تلقائي إلى Lanczos** ما لم يطلب المستخدم `--on-missing-backend=fallback`.
- إذا لم يُقدَّم `--sr-model` للـ backend الذي يتطلّبه، يفشل الأمر بمخرج غير صفري.

### 3.4 Python

```python
from clarification import Options, SrOptions, FaceGuardOptions, clarify_file

opts = Options.portrait().with_sr(
    SrOptions(
        backend="onnx",
        model_path="~/models/realesrgan-x4.onnx",
        target_scale=4.0,
        tile=256,
        fidelity=0.7,
    )
).with_face_guard(
    FaceGuardOptions(
        embedder_model="~/models/arcface.onnx",
        max_cosine_distance=0.35,
        on_violation="fallback_lanczos",
    )
)

clarify_file("input.png", "output.png", opts)
```

Python يبقى غلافًا فوق CLI للحقول الجديدة (حتى لا نُدخل tract/ort عبر PyO3 في هذه المرحلة).

### 3.5 Go

```go
sr := clarification.SROptions{
    Backend:   "onnx",
    ModelPath: "/models/realesrgan-x4.onnx",
    Scale:     4.0,
    Tile:      256,
    Fidelity:  0.7,
}
guard := clarification.FaceGuardOptions{
    EmbedderModel:    "/models/arcface.onnx",
    MaxCosineDist:    0.35,
    OnViolation:      clarification.FallbackLanczos,
}
opts := clarification.PortraitOptions().WithSR(sr).WithFaceGuard(guard)
err := clarification.Enhance("clarification", "in.png", "out.png", opts)
```

### 3.6 Lua

```lua
local c = require("clarification")
local opts = c.portrait()
opts.sr = { backend="onnx", model="~/models/x4.onnx", scale=4, tile=256, fidelity=0.7 }
opts.face_guard = { embedder="~/models/arcface.onnx", max_distance=0.35, on_violation="fallback_lanczos" }
c.enhance("clarification", "in.png", "out.png", opts)
```

---

## 4) اختبارات موضوعية للمقارنة

هذه الاختبارات **بروتوكول قياس مقترح**، لا ادعاء بأنها ستُنفَّذ فورًا في CI بدون توفير نماذج ومجموعات بيانات مرخّصة. ملفّاتها ستوضع تحت `tests/objective/` مع أعلام `--skip` عند غياب النماذج.

### 4.1 مجموعة تقييم
- 50–100 صورة LR/HR مرخّصة صراحةً (مثال: DIV2K subset تحت رخصتها، أو صور اُلتُقطت داخليًا بموافقة).
- **عدم استخدام** صورة الطفلة المرفقة كـ ground truth في CI؛ تُستخدم كـ visual sanity check يدوي فقط لأن مصدر مرجعها غير موثّق.

### 4.2 المقاييس

| المقياس | ما يقيسه | استخدامه |
|---|---|---|
| **PSNR** | خطأ بكسليّ | خط أساس، ضعيف للـ SR لكنه يُبلَّغ لأغراض المقارنة. |
| **SSIM / MS-SSIM** | تشابه بنيوي | مقياس محافظ مقبول. |
| **LPIPS** (VGG/AlexNet backbone) | تشابه إدراكيّ مُتعلَّم | المقياس الأهم للـ SR الإدراكيّ. اختياريّ لأنه يعتمد نموذجًا. |
| **DISTS** | جودة إدراكية | بديل/مكمّل لـ LPIPS. |
| **NIQE / BRISQUE** | جودة بدون مرجع | مفيد عند غياب HR. |
| **ArcFace cosine distance** بين LR-upscaled وHR | حفاظ على الهوية | **حاسم**: يجب أن تكون المسافة ≤ عتبة القبول (انظر 6). |
| **Landmark drift** (5 نقاط: عينان، أنف، زاويتا الفم) بـ px بعد التطبيع | تشوّه هندسي للوجه | كاشف مبكّر للهلوسة الشكلية. |
| **Detail score الداخلي** | التباين المحلي | يبقى للتوافق الخلفي فقط، لا يُستخدم كمقياس جودة. |

### 4.3 اختبارات مقارنة إلزامية في CI (للـ backends المتوفّرة)
1. **A/B ضد Lanczos**: يجب أن يحقّق backend الـ ONNX تحسّنًا في LPIPS بمقدار محدّد على الأقل (انظر معايير القبول) دون تدهور في ArcFace distance.
2. **اختبار Determinism**: نفس المدخل + نفس البذور + نفس backend → نفس المخرج بايتًا-ببايت (على CPU على الأقل).
3. **اختبار Tile-seams**: تشغيل بـ `tile=256` و`tile=192` يجب ألا يُنتج فارقًا محسوسًا (SSIM ≥ 0.995 بين الناتجين).
4. **اختبار Alpha preservation**: صورة بقناة alpha تخرج بنفس قناة alpha بعد المسار الكامل.
5. **اختبار Face Guard trigger**: صورة مُعدَّة صناعيًا (تشويه هويّة متعمّد بعد SR) يجب أن تُطلق الحارس.

### 4.4 مقارنة بصرية موحّدة
سكربت `scripts/compare_grid.py` يُنتج شبكة 3×N: (LR bicubic upscale | Clarification output | HR reference) مع طباعة المقاييس تحت كل صف، ليُراجَع بشريًا في مراجعات الـ PR.

---

## 5) مخاطر الهلوسة وطرق الحدّ منها

### 5.1 لماذا الهلوسة خطر جوهري
نماذج SR التوليدية (Real-ESRGAN, SwinIR-GAN, GFPGAN, CodeFormer…) تُنشئ ترددات عالية **من التوزيع الذي دُرّبت عليه**. عند تطبيقها على وجه شخص محدد قد:
- تُغيّر شكل القزحية والحدقة (كما يظهر ذلك في المرجع المرفق).
- تُنشئ رموشًا متماثلة صناعية.
- تُنعّم أو تُعيد رسم ملامح (شفاه، فتحتَي أنف) بما يُخلّ بالهوية.
- تُغيّر عمر الشخص الظاهر — **خطر إضافي حين يكون الشخص طفلًا**، ويجب معاملته باعتباره ضابطًا أخلاقيًّا وليس مجرد ضابط جودة.

### 
