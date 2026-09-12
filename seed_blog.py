import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import BlogPost

sample_posts = [
    {
        "title": "دليل بناء المعماريات السحابية عالية التوفر والأداء في الأنظمة الحديثة",
        "slug": "high-availability-cloud-architecture-guide",
        "category": "هندسة البرمجيات والتطوير",
        "excerpt": "استعراض شامل لأفضل ممارسات تصميم بنية الأنظمة السحابية الموزعة، إدارة قواعد البيانات المتزامنة، وتطبيق استراتيجيات التخزين المؤقت لضمان أداء فائق.",
        "cover_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&auto=format&fit=crop&q=80",
        "tags": ["Cloud", "Microservices", "Python", "Architecture", "Redis"],
        "reading_time_minutes": 6,
        "is_featured": True,
        "is_published": True,
        "sort_order": 1,
        "meta_title": "دليل بناء المعماريات السحابية عالية التوفر",
        "meta_description": "تعلم كيفية تصميم وبناء المعماريات السحابية الموزعة لضمان أداء مستقر ومعالجة آلاف الطلبات المتزامنة.",
        "meta_keywords": "معمارية برمجية, حوسبة سحابية, قواعد بيانات, Redis",
        "content": """## مقدمة حول المعماريات السحابية الحديثة

في عصر الأنظمة الرقمية المتسارعة، لم يعد بناء التطبيقات يقتصر على كتابة كود وظيفي فقط، بل يتطلب هندسة معمارية تضمن **التوسع الأفقي (Horizontal Scalability)**، استمرارية العمل دون انقطاع (Zero Downtime)، وسرعة معالجة متناهية.

> "المعمارية الجيدة ليست التي تجعل النظام يعمل اليوم فقط، بل التي تجعل التعديل عليه وتوسيعه غداً أمراً سلساً وآمناً."

---

## 1. نموذج البناء الطبقي (Layered System Design)

تعتمد المعمارية النظيفة على فصل الاهتمامات بين طبقات النظام:

- **طبقة العرض والواجهات (Frontend Layer):** واجهات تفاعلية سريعة تعتمد على تقنيات الـ SPA/SSR.
- **طبقة الخوادم والـ API Gateway:** معالجة الطلبات، التحقق من الصلاحيات (Authentication & RBAC)، وإدارة معدل الطلبات (Rate Limiting).
- **طبقة منطق الأعمال والخدمات المصغرة (Domain & Business Logic):** خدمات مستقلة تؤدي وظائف محددة ومترابطة.
- **طبقة قواعد البيانات والتخزين المؤقت (Data & Cache Layer):** عزل عمليات القراءة عن الكتابة واستخدام محركات الكاش السريعة.

---

## 2. كود تطبيقي: إدارة الكاش الذكي باستخدام Redis

في المثال البرمجي التالي، نستعرض دالة مخصصة في Python لتطبيق نمط **Cache-Aside Pattern** مع معالجة الاستعلامات بكفاءة:

```python
import json
import redis
from typing import Optional, Any

# تهيئة اتصال الـ Cache مع معالجة مهلة الاتصال
cache_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_or_set_cache(key: str, fetch_callback, ttl_seconds: int = 3600) -> Any:
    \"\"\"
    استرجاع البيانات من الكاش إن وجدت، أو جلبها وتخزينها تلقائياً
    \"\"\"
    cached_data = cache_client.get(key)
    if cached_data:
        # استرجاع فوري من الذاكرة العشوائية
        return json.loads(cached_data)
    
    # جلب البيانات من قاعدة البيانات الأساسية
    fresh_data = fetch_callback()
    if fresh_data is not None:
        cache_client.setex(key, ttl_seconds, json.dumps(fresh_data))
        
    return fresh_data
```

---

## 3. مقارنة الأداء قبل وبعد تطبيق استراتيجيات التخزين المؤقت

| معيار القياس | قبل التحسين (Direct DB Queries) | بعد تطبيق التخزين المؤقت (Redis Cache) |
|---|---|---|
| متوسط زمن الاستجابة | 420ms | **18ms (تحسن بنسبة 95%)** |
| استهلاك موارد المعالج | 78% في أوقات الذروة | **15% كحد أقصى** |
| معدل تحمل الطلبات المتزامنة | 1,200 طلب / ثانية | **18,000+ طلب / ثانية** |

---

## 4. الخلاصة والتوصيات العملية

1. **ابدأ بالبساطة:** لا تلجأ للخدمات المصغرة (Microservices) المعقدة ما لم تكن هناك حاجة فعلية لحجم النظام وفريق العمل.
2. **عزل المهام الثقيلة:** استخدم طوابير المهام الخلفية (Background Workers مثل Celery أو RabbitMQ) للعمليات الطويلة.
3. **المراقبة الاستباقية:** اعتمد على أدوات مراقبة الأداء (APM) وسجلات التدقيق لتحديد نقاط الاختناق قبل أن يشعر بها المستخدم.
"""
    },
    {
        "title": "منهجية التفكير التصميمي وبناء أنظمة الواجهات (Design Systems) القابلة للتوسع",
        "slug": "design-thinking-and-scalable-design-systems",
        "category": "تصميم واجهات وتجربة مستخدم UI/UX",
        "excerpt": "كيف تبني نظام تصميم موحد يربط بين المصممين والمطورين، يقلل من هدر الوقت، ويخلق تجربة بصرية متسقة وهوية رقمية استثنائية لمنتجك.",
        "cover_image": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=1200&auto=format&fit=crop&q=80",
        "tags": ["UI/UX", "Design System", "Figma", "Design Thinking"],
        "reading_time_minutes": 5,
        "is_featured": True,
        "is_published": True,
        "sort_order": 2,
        "meta_title": "بناء أنظمة الواجهات وتجربة المستخدم القابلة للتوسع",
        "meta_description": "دليل بناء Design System متكامل من التفكير الأولي وحتى التسليم النهائي للواجهات.",
        "meta_keywords": "تصميم واجهات, تجربة مستخدم, Design System, Figma",
        "content": """## أهمية نظام التصميم (Design System)

أنظمة التصميم ليست مجرد مكتبة لملفات Figma أو لوحة ألوان عشوائية، بل هي **لغة تواصل مشتركة** وعقد عمل بين المصمم والمطور وفريق المنتج لضمان اتساق كافة التجارب الرقمية.

---

## 1. ركائز نظام التصميم المتكامل

1. **رموز التصميم (Design Tokens):** الوحدات الذرية الأساسية للقيم (الألوان، الخطوط، المسافات، وظلال الـ Elevation).
2. **المكونات التفاعلية (Interactive UI Components):** أزرار، حقول إدخال، نوافذ منبثقة، وبطاقات ذات حالات محددة (Default, Hover, Active, Disabled).
3. **إمكانية الوصول والشمولية (Accessibility - WCAG 2.1):** تباين ألوان مريح، دعم قارئات الشاشة، ومراعاة مختلف المستخدمين.

> "التصميم العظيم ليس ما يُرى بالعين فقط، بل ما يُشعر به من سلاسة وبساطة أثناء الاستخدام اليومي."

---

## 2. خطوات مسار التفكير التصميمي (Design Thinking Workflow)

- **الفهم والتعاطف (Empathize):** إجراء المقابلات وبناء شخصيات المستخدمين.
- **التحديد (Define):** صياغة المشكلة والتحدي بدقة.
- **التوليد والتخطيط (Ideate & Wireframe):** رسم المخططات الهيكلية منخفضة الدقة.
- **النمذجة (Prototype):** بناء واجهات تفاعلية عالية الدقة.
- **الاختبار والتحقق (Test):** قياس سهولة الاستخدام وإجراء التحسينات المستمرة.
"""
    },
    {
        "title": "استراتيجيات تحويل الأفكار إلى منتجات رقمية ناجحة ومربحة",
        "slug": "digital-product-strategy-and-growth",
        "category": "إدارة واستراتيجيات الأعمال",
        "excerpt": "خارطة طريق واضحة لرواد الأعمال وأصحاب المشاريع للتحقق من جدوى الفكرة وبناء نموذج العمل (Business Model) وتحقيق أعلى عائد استثمار.",
        "cover_image": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&auto=format&fit=crop&q=80",
        "tags": ["Business", "Startup", "Growth", "Product Management"],
        "reading_time_minutes": 4,
        "is_featured": False,
        "is_published": True,
        "sort_order": 3,
        "meta_title": "استراتيجيات بناء المنتجات الرقمية ونمو الأعمال",
        "meta_description": "دليل استراتيجي لتحويل الأفكار إلى منتجات ذات عائد استثماري ونمو مستمر.",
        "meta_keywords": "ريادة أعمال, استراتيجيات الأعمال, نمو المشاريع, إدارة المنتجات",
        "content": """## من الفكرة إلى الإطلاق الناجح

الكثير من المشاريع الرقمية تفشل ليس بسبب سوء البرمجة أو ضعف التصميم، بل بسبب بناء منتج لا يحل مشكلة حقيقية في السوق.

---

## 1. نموذج إطلاق الـ MVP (المنتج الأولي القابل للتطبيق)

- تحديد الميزة الجوهرية (Core Value Proposition) والتركيز عليها فقط.
- إطلاق سريع للتحقق من تفاعل الجمهور المستهدف (Validate Assumptions).
- جمع التغذية الراجعة (Feedback Loops) والتطوير بناءً على أرقام وسلوك المستخدمين الفعلي.

---

## 2. مؤشرات الأداء الرئيسية (KPIs) لنجاح المشاريع

- **تكلفة الاستحواذ على العميل (CAC):** كم تنفق لجلب عميل جديد؟
- **القيمة الدائمة للعميل (LTV):** كم ينفق العميل خلال فترة استخدامه للمنتج؟
- **معدل الاحتفاظ (Retention Rate):** هل يعود المستخدمون لاستخدام النظام بانتظام؟
"""
    }
]

for p_data in sample_posts:
    slug = p_data["slug"]
    post, created = BlogPost.objects.update_or_create(
        slug=slug,
        defaults=p_data
    )

print("Seeding completed successfully!")
