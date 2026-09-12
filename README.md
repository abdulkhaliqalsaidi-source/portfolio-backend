# Portfolio Backend (Django 5 REST Framework)

خادم الواجهات الخلفية وقاعدة البيانات لمنصة معرض الأعمال والمدونة التقنية مبني على **Django 5** و **Django REST Framework** مع توثيق JWT ودعم PostgreSQL.

---

## الميزات التقنية
- **Django 5 + DRF:** واجهات برمجة تطبيقات RESTful كاملة وسريعة.
- **SimpleJWT:** مصادقة وتوثيق عبر رموز JWT وحماية لوحة التحكم.
- **Dynamic Database Support:** دعم تلقائي لـ PostgreSQL في الإنتاج مع التبديل التلقائي لـ SQLite في التطوير.
- **WhiteNoise & Gunicorn:** جاهز تماماً للتشغيل في بيئة الإنتاج السحابية.
- **Data Templates Engine:** منظومة تصدير واستيراد بيانات المنصة بالكامل بصيغة JSON.

---

## التشغيل المحلي (Development)

```bash
# إنشاء وتفعيل البيئة الافتراضية
python -m venv venv
source venv/bin/activate  # في Linux/Mac
venv\Scripts\activate     # في Windows

# تثبيت الحزم
pip install -r requirements.txt

# تطبيق الهجرات
python manage.py migrate

# تشغيل خادم التطوير
python manage.py runserver
```

---

## متغيرات البيئة (Environment Variables)

قم بإنشاء ملف `.env` بناءً على `.env.example`:

```env
DJANGO_SECRET_KEY=your-secure-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app

# بيانات قاعدة بيانات PostgreSQL
DB_NAME=portfolio_db
DB_USER=portfolio_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=5432
```

---

## النشر على Render / Railway

1. اربط هذا المستودع في **Render.com** كـ **Web Service**.
2. **Build Command:**
   ```bash
   pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
   ```
3. **Start Command:**
   ```bash
   gunicorn core.wsgi:application
   ```
