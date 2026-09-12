from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    full_name = models.CharField(max_length=150, verbose_name="الاسم الكامل", blank=True, default="")
    title = models.CharField(max_length=150, verbose_name="المسمى الوظيفي", blank=True, default="")
    tagline = models.CharField(max_length=255, verbose_name="الشعار / العبارة التعريفية", blank=True, default="")
    bio = models.TextField(verbose_name="نبذة عني", blank=True, default="")
    email = models.EmailField(verbose_name="البريد الإلكتروني", blank=True, default="")
    phone = models.CharField(max_length=30, verbose_name="رقم الهاتف", blank=True, default="")
    whatsapp = models.CharField(max_length=30, verbose_name="رقم الواتساب", blank=True, default="")
    github = models.URLField(verbose_name="رابط GitHub / المستودع", blank=True, default="")
    linkedin = models.URLField(verbose_name="رابط LinkedIn", blank=True, default="")
    twitter = models.URLField(verbose_name="رابط منصة X/Twitter", blank=True, default="")
    instagram = models.URLField(verbose_name="رابط Instagram", blank=True, default="")
    behance = models.URLField(verbose_name="رابط Behance", blank=True, default="")
    dribbble = models.URLField(verbose_name="رابط Dribbble", blank=True, default="")
    youtube = models.URLField(verbose_name="رابط YouTube", blank=True, default="")
    website = models.URLField(verbose_name="رابط الموقع / المعرض الشخصي", blank=True, default="")
    location = models.CharField(max_length=100, verbose_name="الموقع الجغرافي", blank=True, default="")
    avatar = models.CharField(max_length=500, verbose_name="رابط صورة الملف الشخصي", blank=True, default="")
    resume = models.CharField(max_length=500, verbose_name="رابط ملف السيرة الذاتية (PDF)", blank=True, default="")
    available_for_work = models.BooleanField(verbose_name="متاح للعمل الحر والمشاريع", default=True)
    years_of_experience = models.PositiveIntegerField(verbose_name="سنوات الخبرة", default=0)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    class Meta:
        verbose_name = "الملف الشخصي"
        verbose_name_plural = "الملف الشخصي"

    def __str__(self):
        return self.full_name


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم التصنيف", unique=True)
    icon = models.CharField(max_length=50, verbose_name="أيقونة التصنيف", default="mdi-code-braces")
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)

    class Meta:
        verbose_name = "تصنيف مهارات"
        verbose_name_plural = "تصنيفات المهارات"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.name


class Skill(models.Model):
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills', verbose_name="التصنيف")
    name = models.CharField(max_length=100, verbose_name="اسم المهارة / التقنية")
    icon = models.CharField(max_length=50, verbose_name="الأيقونة", default="mdi-code-tags")
    color = models.CharField(max_length=30, verbose_name="لون العلامة", default="#7B6EF6")
    proficiency_percentage = models.PositiveIntegerField(verbose_name="نسبة الإتقان (%)", default=85)
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    is_visible = models.BooleanField(verbose_name="ظاهر في الموقع", default=True)

    class Meta:
        verbose_name = "مهارة تقنية"
        verbose_name_plural = "المهارات التقنية"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Service(models.Model):
    title = models.CharField(max_length=150, verbose_name="عنوان الخدمة")
    description = models.TextField(verbose_name="وصف الخدمة")
    icon = models.CharField(max_length=50, verbose_name="الأيقونة", default="mdi-monitor-dashboard")
    color = models.CharField(max_length=30, verbose_name="اللون المميز", default="#7B6EF6")
    features = models.JSONField(verbose_name="مميزات الخدمة", default=list, blank=True)
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    is_active = models.BooleanField(verbose_name="مفعل", default=True)

    class Meta:
        verbose_name = "خدمة"
        verbose_name_plural = "الخدمات"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return self.title


class Project(models.Model):
    slug = models.SlugField(max_length=120, unique=True, verbose_name="المعرف اللطيف (Slug)")
    title = models.CharField(max_length=200, verbose_name="عنوان المشروع")
    category = models.CharField(max_length=150, verbose_name="تصنيف أو نطاق المشروع", blank=True, default="")
    role = models.CharField(max_length=150, verbose_name="الدور المهني / الهندسي", blank=True, default="")
    year = models.CharField(max_length=50, verbose_name="سنة التنفيذ", blank=True, default="")
    short_description = models.TextField(verbose_name="وصف مختصر")
    full_description = models.TextField(verbose_name="الوصف الكامل للمشروع", blank=True, default="")
    problem = models.TextField(verbose_name="المشكلة والتحدي", blank=True, default="")
    architecture = models.TextField(verbose_name="المعمارية والحل", blank=True, default="")
    features = models.JSONField(verbose_name="أبرز مميزات المشروع", default=list, blank=True)
    objectives = models.JSONField(verbose_name="الأهداف المحددة", default=list, blank=True)
    metrics = models.JSONField(verbose_name="النتائج والقياس الفعلي", default=list, blank=True)
    tags = models.JSONField(verbose_name="التقنيات / الأدوات المستخدمة", default=list, blank=True)
    image = models.CharField(max_length=500, verbose_name="رابط الصورة الرئيسية", blank=True, default="")
    before_image = models.CharField(max_length=500, verbose_name="صورة قبل التنفيذ (Before)", blank=True, default="")
    after_image = models.CharField(max_length=500, verbose_name="صورة بعد التنفيذ (After)", blank=True, default="")
    client_name = models.CharField(max_length=200, verbose_name="اسم العميل / الشريك", blank=True, default="")
    testimonial_quote = models.TextField(verbose_name="اقتباس أو شهادة العميل", blank=True, default="")
    before_notes = models.JSONField(verbose_name="ملاحظات وتحديات الوضع السابق", default=list, blank=True)
    after_notes = models.JSONField(verbose_name="مخرجات وحلول الوضع بعد التطوير", default=list, blank=True)
    architecture_stages = models.JSONField(verbose_name="مراحل المعمارية ومسار العمل", default=list, blank=True)
    demo_url = models.CharField(max_length=500, verbose_name="رابط المعاينة الحية", blank=True, default="")
    github_url = models.CharField(max_length=500, verbose_name="رابط GitHub / المستودع", blank=True, default="")
    accent_color = models.CharField(max_length=30, verbose_name="اللون التمييزي للمشروع", default="#7B6EF6")
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    is_featured = models.BooleanField(verbose_name="مشروع مميز (Featured)", default=False)
    is_published = models.BooleanField(verbose_name="منشور في الموقع", default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "مشروع"
        verbose_name_plural = "المشاريع"
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='gallery', verbose_name="المشروع")
    image_url = models.CharField(max_length=500, verbose_name="رابط الصورة")
    caption = models.CharField(max_length=200, verbose_name="وصف توضيحي", blank=True)
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)

    class Meta:
        verbose_name = "صورة للمشروع"
        verbose_name_plural = "معرض صور المشاريع"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.project.title} - {self.caption or 'صورة'}"


class Experience(models.Model):
    year = models.CharField(max_length=50, verbose_name="السنة / الفترة الزمنية", default="")
    title = models.CharField(max_length=200, verbose_name="المسمى / المحطة")
    organization = models.CharField(max_length=200, verbose_name="الجهة / المنظمة", blank=True, default="")
    description = models.TextField(verbose_name="تفاصيل الإنجاز والخبرة")
    icon = models.CharField(max_length=50, verbose_name="الأيقونة", default="mdi-briefcase")
    color = models.CharField(max_length=30, verbose_name="اللون المميز", default="#7B6EF6")
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    is_active = models.BooleanField(verbose_name="مفعل", default=True)

    class Meta:
        verbose_name = "خبرة مهنية"
        verbose_name_plural = "الخبرات والخط الزمني"
        ordering = ['sort_order', '-id']

    def __str__(self):
        return f"{self.year} - {self.title}"


class Testimonial(models.Model):
    client_name = models.CharField(max_length=150, verbose_name="اسم العميل")
    client_role = models.CharField(max_length=150, verbose_name="المنصب والشركة")
    client_company = models.CharField(max_length=150, verbose_name="اسم الشركة", blank=True, default="")
    client_avatar = models.CharField(max_length=500, verbose_name="صورة العميل", blank=True, default="")
    feedback_text = models.TextField(verbose_name="نص الشهادة والتقييم")
    rating = models.PositiveSmallIntegerField(verbose_name="التقييم (1-5)", default=5)
    color = models.CharField(max_length=50, verbose_name="لون الخلفية التمييزي", default="rgba(123,110,246,0.2)")
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    is_published = models.BooleanField(verbose_name="منشور", default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإضافة")

    class Meta:
        verbose_name = "رأي عميل"
        verbose_name_plural = "آراء وشهادات العملاء"
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return f"{self.client_name} ({self.client_role})"


class Statistic(models.Model):
    label = models.CharField(max_length=100, verbose_name="العنوان التوضيحي")
    value = models.PositiveIntegerField(verbose_name="القيمة الرقمية", default=0)
    suffix = models.CharField(max_length=10, verbose_name="اللاحقة (مثل + أو %)", blank=True, default="+")
    description = models.CharField(max_length=255, verbose_name="الوصف التوضيحي", blank=True, default="")
    icon = models.CharField(max_length=50, verbose_name="الأيقونة", default="mdi-rocket-launch")
    color = models.CharField(max_length=30, verbose_name="اللون", default="#7B6EF6")
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    is_active = models.BooleanField(verbose_name="مفعل", default=True)

    class Meta:
        verbose_name = "إحصائية"
        verbose_name_plural = "الإحصائيات والأرقام"
        ordering = ['sort_order', 'id']

    def __str__(self):
        return f"{self.value}{self.suffix} {self.label}"


class ContactMessage(models.Model):
    STATUS_CHOICES = [
        ('new', 'جديدة'),
        ('read', 'مقروءة'),
        ('archived', 'مؤرشفة'),
    ]

    sender_name = models.CharField(max_length=150, verbose_name="اسم المرسل")
    sender_email = models.EmailField(verbose_name="البريد الإلكتروني")
    sender_phone = models.CharField(max_length=50, verbose_name="رقم الهاتف", blank=True)
    subject = models.CharField(max_length=200, verbose_name="الموضوع")
    message = models.TextField(verbose_name="نص الرسالة")
    ip_address = models.GenericIPAddressField(verbose_name="عنوان IP", null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="حالة الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="تمت القراءة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الاستلام")

    class Meta:
        verbose_name = "رسالة تواصل"
        verbose_name_plural = "رسائل التواصل الواردة"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender_name} - {self.subject}"


class SiteSetting(models.Model):
    key = models.CharField(max_length=100, primary_key=True, verbose_name="مفتاح الإعداد")
    value = models.TextField(verbose_name="القيمة", blank=True)
    group_name = models.CharField(max_length=50, default="general", verbose_name="المجموعة")
    setting_type = models.CharField(max_length=20, default="text", verbose_name="نوع الحقل")
    description = models.CharField(max_length=255, verbose_name="وصف الإعداد", blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        verbose_name = "إعداد عام"
        verbose_name_plural = "إعدادات الموقع العامة"
        ordering = ['group_name', 'key']

    def __str__(self):
        return f"{self.key}: {self.value}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم")
    action = models.CharField(max_length=100, verbose_name="الإجراء")
    entity_type = models.CharField(max_length=100, verbose_name="نوع الكيان")
    entity_id = models.CharField(max_length=100, blank=True, verbose_name="معرف الكيان")
    details = models.JSONField(default=dict, blank=True, verbose_name="التفاصيل")
    ip_address = models.CharField(max_length=50, blank=True, verbose_name="عنوان IP")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="التاريخ والوقت")

    class Meta:
        verbose_name = "سجل رقابة"
        verbose_name_plural = "سجلات الرقابة والعمليات"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.user} - {self.action} ({self.entity_type})"


class MediaFile(models.Model):
    title = models.CharField(max_length=200, verbose_name="اسم الملف")
    file = models.FileField(upload_to='uploads/', verbose_name="الملف")
    file_type = models.CharField(max_length=50, default='image', verbose_name="نوع الملف")
    file_size = models.PositiveIntegerField(default=0, verbose_name="حجم الملف بالبايت")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")

    class Meta:
        verbose_name = "ملف وسائط"
        verbose_name_plural = "مكتبة الوسائط"
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title


class DataImportHistory(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'ناجح'),
        ('FAILED', 'فشل'),
        ('PARTIAL', 'جزئي'),
        ('VALIDATING', 'قيد الفحص'),
    ]
    MODE_CHOICES = [
        ('CREATE_ONLY', 'إنشاء الجديد فقط'),
        ('UPSERT', 'تحديث أو إنشاء'),
        ('SKIP_EXISTING', 'تجاهل الموجود'),
        ('REPLACE', 'استبدال شامل'),
    ]

    filename = models.CharField(max_length=255, verbose_name="اسم الملف")
    version = models.CharField(max_length=30, default="1.0.0", verbose_name="إصدار القالب")
    import_mode = models.CharField(max_length=30, choices=MODE_CHOICES, default='UPSERT', verbose_name="طريقة الاستيراد")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SUCCESS', verbose_name="حالة العملية")
    summary = models.JSONField(default=dict, blank=True, verbose_name="إحصائيات الكيانات")
    created_count = models.PositiveIntegerField(default=0, verbose_name="العناصر المنشأة")
    updated_count = models.PositiveIntegerField(default=0, verbose_name="العناصر المحدثة")
    skipped_count = models.PositiveIntegerField(default=0, verbose_name="العناصر المتخطاة")
    error_count = models.PositiveIntegerField(default=0, verbose_name="عدد الأخطاء")
    warning_count = models.PositiveIntegerField(default=0, verbose_name="عدد التحذيرات")
    errors_log = models.JSONField(default=list, blank=True, verbose_name="سجل تفاصيل الأخطاء")
    warnings_log = models.JSONField(default=list, blank=True, verbose_name="سجل تفاصيل التحذيرات")
    imported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المستخدم المنفذ")
    duration_ms = models.PositiveIntegerField(default=0, verbose_name="مدة التنفيذ (مللي ثانية)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ وتوقيت العملية")

    class Meta:
        verbose_name = "سجل استيراد بيانات"
        verbose_name_plural = "سجل عمليات استيراد البيانات"
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.filename} ({self.get_status_display()})"


class BlogPost(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان المقال")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="الرابط الدائم (Slug)", allow_unicode=True)
    category = models.CharField(max_length=100, default="عام", verbose_name="التصنيف / التخصص")
    excerpt = models.TextField(verbose_name="المقتطف / النبذة المختصرة", blank=True, default="")
    content = models.TextField(verbose_name="محتوى المقال (Markdown / Rich Text)")
    cover_image = models.CharField(max_length=500, verbose_name="صورة الغلاف", blank=True, default="")
    tags = models.JSONField(verbose_name="الوسوم والكلمات المفتاحية", default=list, blank=True)
    reading_time_minutes = models.PositiveIntegerField(verbose_name="وقت القراءة المقدر (بالدقائق)", default=3)
    views_count = models.PositiveIntegerField(verbose_name="عدد المشاهدات", default=0)
    likes_count = models.PositiveIntegerField(verbose_name="عدد الإعجابات", default=0)
    is_featured = models.BooleanField(verbose_name="مقال مميز", default=False)
    is_published = models.BooleanField(verbose_name="منشور في الموقع", default=True)
    sort_order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    meta_title = models.CharField(max_length=255, verbose_name="عنوان الـ SEO (Meta Title)", blank=True, default="")
    meta_description = models.TextField(verbose_name="وصف الـ SEO (Meta Description)", blank=True, default="")
    meta_keywords = models.CharField(max_length=255, verbose_name="الكلمات المفتاحية للـ SEO", blank=True, default="")
    published_at = models.DateTimeField(verbose_name="تاريخ النشر", auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name="آخر تحديث", auto_now=True)

    class Meta:
        verbose_name = "مقال / تدوينة"
        verbose_name_plural = "المدونة والمقالات"
        ordering = ['-is_featured', 'sort_order', '-published_at']

    def calculate_reading_time(self):
        text = self.content or ""
        words = len(text.split())
        # Roughly 180 words per minute
        minutes = max(1, round(words / 180))
        return minutes

    def save(self, *args, **kwargs):
        if not self.reading_time_minutes or self.reading_time_minutes == 0:
            self.reading_time_minutes = self.calculate_reading_time()
        if not self.slug and self.title:
            import re
            cleaned = re.sub(r'[^\w\s-]', '', self.title).strip().lower()
            self.slug = re.sub(r'[-\s]+', '-', cleaned) or f"post-{self.pk or 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
