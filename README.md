# Portfolio Backend (Django 5 REST Framework)

خادم الواجهات الخلفية وقاعدة البيانات لمنصة معرض الأعمال والمدونة التقنية مبني على **Django 5** و **Django REST Framework** مع توثيق JWT وقاعدة بيانات **SQLite** مدمجة وجاهزة للعمل فوراً بدون أي إعدادات خارجية معقدة.

---

## الميزات التقنية
- **Django 5 + DRF:** واجهات برمجة تطبيقات RESTful كاملة وسريعة.
- **SQLite Database:** قاعدة بيانات مدمجة وخفيفة وسريعة لا تتطلب إعداد سيرفرات خارجية أو كلمات مرور.
- **SimpleJWT:** مصادقة وتوثيق عبر رموز JWT وحماية كاملة للمسارات.
- **WhiteNoise & Gunicorn:** جاهز تماماً للتشغيل في بيئة الإنتاج السحابية.
- **Data Fixtures & Backup:** نسخة احتياطية كاملة للمحتوى بصيغة `portfolio_data.json` تضمن عدم ضياع أي بيانات.

---

## التشغيل المحلي (Local Development)

```bash
# إنشاء وتفعيل البيئة الافتراضية
python -m venv venv
venv\Scripts\activate     # في Windows
source venv/bin/activate  # في Linux/Mac

# تثبيت الحزم
pip install -r requirements.txt

# تطبيق الهجرات (إذا لزم)
python manage.py migrate

# تشغيل الخادم
python manage.py runserver
```

---

## متغيرات البيئة (Environment Variables)

قم بإنشاء ملف `.env` في المجلد الرئيسي للباك إند:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:3000
MAX_UPLOAD_SIZE_MB=10
```

> **ملاحظة:** لا تحتاج إلى أي متغيرات لقاعدة البيانات مثل `DB_NAME` أو `DB_PASSWORD`، فقاعدة بيانات SQLite (`db.sqlite3`) مدمجة ومضمنة مع المشروع مباشرة!

---

## النشر على Render.com (Web Service)

1. ادخل على [Render.com](https://render.com) واضغط **New +** ثم اختر **Web Service**.
2. اختر مستودع `portfolio-backend`.
3. قم بملء الإعدادات:
   - **Environment:** `Python 3`
   - **Build Command:**
     ```bash
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command:**
     ```bash
     gunicorn core.wsgi:application
     ```
4. في قسم **Environment Variables**، أضف فقط:
   - `DJANGO_SECRET_KEY` = أي نص عشوائي قوي
   - `DJANGO_ALLOWED_HOSTS` = `*`
   - `CORS_ALLOWED_ORIGINS` = رابط موقعك على Vercel (مثال: `https://your-app.vercel.app`)

---

## استعادة أو تحديث البيانات

إذا أردت إعادة تعيين أو تحميل كل بيانات المعرض والمدونة والحسابات:
```bash
python manage.py loaddata portfolio_data.json
```
