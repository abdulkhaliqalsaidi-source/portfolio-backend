from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from api.models import (
    Profile, SkillCategory, Skill, Service, Project,
    Experience, Testimonial, Statistic, SiteSetting
)

class Command(BaseCommand):
    help = 'Seeds initial portfolio data and admin user'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting database seeding...'))

        # 1. Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@portfolio.dev',
                'first_name': 'مدير',
                'last_name': 'النظام',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123456')
        admin_user.save()
        self.stdout.write(self.style.SUCCESS(f'Admin user: admin / admin123456 ({"Created" if created else "Updated password"})'))

        # 2. Profile
        Profile.objects.update_or_create(
            id=1,
            defaults={
                'full_name': 'عبد الخالق الصايدي',
                'title': 'مطور Full Stack Engineer',
                'tagline': 'أبني أنظمة قابلة للتوسع وواجهات أنيقة تُشحن للإنتاج.',
                'bio': 'مهندس برمجيات ومطور Full Stack ذو خبرة تفوق 3 سنوات في بناء أنظمة مؤسسية معقدة (ERP)، منصات ويب تفاعلية، وواجهات RESTful APIs عالية الأداء باستخدام Vue 3 وDjango وPostgreSQL.',
                'email': 'abdul.khaliq.al.saidi@gmail.com',
                'phone': '+967 771 523 243',
                'whatsapp': '967771523243',
                'github': 'https://github.com',
                'linkedin': 'https://linkedin.com',
                'behance': 'https://behance.net',
                'dribbble': '',
                'instagram': '',
                'youtube': '',
                'website': '',
                'twitter': '',
                'location': 'اليمن',
                'avatar': '/avatar.jpg',
                'resume': '/resume.pdf',
                'available_for_work': True,
                'years_of_experience': 3,
            }
        )
        self.stdout.write(self.style.SUCCESS('Profile created/updated.'))

        # 3. Statistics
        stats_data = [
            {'label': 'مشروع منجز', 'value': 30, 'suffix': '+', 'description': 'أنظمة ويب وتطبيقات متكاملة تم شحنها للإنتاج الفعلي.', 'icon': 'mdi-rocket-launch', 'color': '#7B6EF6', 'sort_order': 1},
            {'label': 'نظام مؤسسي', 'value': 8, 'suffix': '', 'description': 'حلول شاملة لإدارة المخازن، الرواتب، وسير العمليات.', 'icon': 'mdi-domain', 'color': '#06B6D4', 'sort_order': 2},
            {'label': 'سنوات خبرة', 'value': 3, 'suffix': '+', 'description': 'تطوير متواصل وخبرة متراكمة في بيئات العمل الحقيقية.', 'icon': 'mdi-calendar-star', 'color': '#EC4899', 'sort_order': 3},
            {'label': 'عميل راضٍ', 'value': 15, 'suffix': '+', 'description': 'ثقة مبنية على الالتزام بالمواعيد وجودة المعمارية.', 'icon': 'mdi-account-group', 'color': '#10B981', 'sort_order': 4},
        ]
        Statistic.objects.all().delete()
        for item in stats_data:
            Statistic.objects.create(**item)
        self.stdout.write(self.style.SUCCESS('Statistics created.'))

        # 4. Skill Categories & Skills
        SkillCategory.objects.all().delete()
        Skill.objects.all().delete()

        cats_data = [
            {
                'name': 'الواجهة الأمامية',
                'icon': 'mdi-monitor',
                'sort_order': 1,
                'skills': [
                    {'name': 'Vue 3', 'icon': 'mdi-vuejs', 'color': '#42b883', 'proficiency_percentage': 95, 'sort_order': 1},
                    {'name': 'Vuetify 3', 'icon': 'mdi-vuetify', 'color': '#1867C0', 'proficiency_percentage': 90, 'sort_order': 2},
                    {'name': 'Vite', 'icon': 'mdi-lightning-bolt', 'color': '#646cff', 'proficiency_percentage': 90, 'sort_order': 3},
                    {'name': 'TypeScript', 'icon': 'mdi-language-typescript', 'color': '#3178c6', 'proficiency_percentage': 85, 'sort_order': 4},
                    {'name': 'Tailwind CSS', 'icon': 'mdi-tailwind', 'color': '#38bdf8', 'proficiency_percentage': 88, 'sort_order': 5},
                    {'name': 'Pinia & Router', 'icon': 'mdi-state-machine', 'color': '#ffe066', 'proficiency_percentage': 92, 'sort_order': 6},
                ]
            },
            {
                'name': 'الواجهة الخلفية',
                'icon': 'mdi-server',
                'sort_order': 2,
                'skills': [
                    {'name': 'Django', 'icon': 'mdi-language-python', 'color': '#092e20', 'proficiency_percentage': 95, 'sort_order': 1},
                    {'name': 'Django REST', 'icon': 'mdi-api', 'color': '#a30000', 'proficiency_percentage': 92, 'sort_order': 2},
                    {'name': 'PostgreSQL', 'icon': 'mdi-database', 'color': '#336791', 'proficiency_percentage': 90, 'sort_order': 3},
                    {'name': 'Redis Caching', 'icon': 'mdi-memory', 'color': '#dc382d', 'proficiency_percentage': 85, 'sort_order': 4},
                    {'name': 'Celery Queues', 'icon': 'mdi-cog-sync', 'color': '#37814a', 'proficiency_percentage': 82, 'sort_order': 5},
                    {'name': 'JWT & OAuth', 'icon': 'mdi-shield-key', 'color': '#f59e0b', 'proficiency_percentage': 90, 'sort_order': 6},
                ]
            },
            {
                'name': 'الأدوات والـ DevOps',
                'icon': 'mdi-wrench',
                'sort_order': 3,
                'skills': [
                    {'name': 'Git & GitHub', 'icon': 'mdi-git', 'color': '#f05032', 'proficiency_percentage': 92, 'sort_order': 1},
                    {'name': 'Docker & Compose', 'icon': 'mdi-docker', 'color': '#2496ed', 'proficiency_percentage': 88, 'sort_order': 2},
                    {'name': 'Linux (Ubuntu)', 'icon': 'mdi-linux', 'color': '#fcc624', 'proficiency_percentage': 85, 'sort_order': 3},
                    {'name': 'Nginx Reverse Proxy', 'icon': 'mdi-server-network', 'color': '#009639', 'proficiency_percentage': 84, 'sort_order': 4},
                    {'name': 'CI/CD Pipelines', 'icon': 'mdi-pipe', 'color': '#6C63FF', 'proficiency_percentage': 80, 'sort_order': 5},
                ]
            }
        ]

        for cat_info in cats_data:
            skills = cat_info.pop('skills')
            cat = SkillCategory.objects.create(**cat_info)
            for skill_info in skills:
                Skill.objects.create(category=cat, **skill_info)

        self.stdout.write(self.style.SUCCESS('Skill categories and skills created.'))

        # 5. Services
        services_data = [
            {
                'title': 'تطوير تطبيقات Full Stack متكاملة',
                'description': 'بناء تطبيقات ويب متكاملة من الصفر وحتى النشر، تجمع بين واجهات Vue 3 التفاعلية وخلفيات Django السريعة والآمنة.',
                'icon': 'mdi-monitor-dashboard',
                'color': '#7B6EF6',
                'features': ['Vue 3 + Composition API', 'معمارية RESTful API نظيفة', 'قواعد بيانات علائقية عالية الأداء', 'تصميم متجاوب وسهل الاستخدام'],
                'sort_order': 1
            },
            {
                'title': 'أنظمة تخطيط الموارد المؤسسية (ERP)',
                'description': 'تطوير أنظمة إدارة شاملة ومخصصة للمصانع والشركات تشمل المخزون، الإنتاج، الموارد البشرية، والمالية.',
                'icon': 'mdi-domain',
                'color': '#06B6D4',
                'features': ['لوحات تحكم لحظية (Real-time)', 'إدارة الصلاحيات والأدوار بدقة', 'تقارير مالية وجداول بيانات متقدمة', 'أتمتة سير العمل وسجلات النشاط'],
                'sort_order': 2
            },
            {
                'title': 'بناء وتطوير الـ RESTful APIs',
                'description': 'تصميم وبرمجة واجهات برمجية آمنة وقابلة للتوسع باستخدام Django REST Framework مع توثيق احترافي.',
                'icon': 'mdi-api',
                'color': '#EC4899',
                'features': ['مصادقة آمنة عبر JWT', 'تخزين مؤقت عالي السرعة عبر Redis', 'معالجة المهام الخلفية عبر Celery', 'حماية متقدمة من الهجمات'],
                'sort_order': 3
            },
            {
                'title': 'تحسين الأداء وDevOps',
                'description': 'نشر وإعداد الخوادم، احتواء التطبيقات باستخدام Docker، وإعداد Reverse Proxy وشهادات SSL.',
                'icon': 'mdi-server-network',
                'color': '#10B981',
                'features': ['حاويات Docker و Docker Compose', 'إعداد Nginx و Gunicorn', 'تحسين سرعة الاستعلامات وفهارس DB', 'خطوط الأتمتة CI/CD'],
                'sort_order': 4
            },
        ]
        Service.objects.all().delete()
        for item in services_data:
            Service.objects.create(**item)
        self.stdout.write(self.style.SUCCESS('Services created.'))

        # 6. Projects
        projects_data = [
            {
                'slug': 'erp-system',
                'title': 'نظام ERP متكامل لإدارة المصانع والإنتاج',
                'category': 'أنظمة مؤسسية (ERP)',
                'role': 'Lead Full Stack Engineer & Architect',
                'year': '2024 - 2025',
                'short_description': 'نظام تخطيط موارد مؤسسي متكامل لشركة تصنيع يدير خطوط الإنتاج، تتبع المخزون، الموارد البشرية، والتقارير المالية.',
                'full_description': 'حل ERP شامل لرقمنة وأتمتة سير عمل التصنيع بالكامل. يتولى النظام تخطيط خطوط الإنتاج، تتبع المواد الخام والموردين، إدارة الموظفين والرواتب، والتقارير المالية والتحليلات اللحظية.',
                'tags': ['Vue 3', 'Django', 'PostgreSQL', 'Docker', 'Redis', 'Vuetify 3'],
                'github_url': 'https://github.com',
                'demo_url': 'https://demo.example.com',
                'image': '/projects/erp.jpg',
                'accent_color': '#3B82F6',
                'problem': 'كان العميل يعتمد على جداول بيانات مبعثرة وعمليات ورقية يدوية، مما تسبب في تناقضات بيانات المخزون، وتأخير دورات الإنتاج، وغياب رؤية مالية دقيقة.',
                'architecture': 'معمارية Modulith متقدمة مع Django REST Framework في الخلفية، واجهة Vue 3 SPA متجاوبة، قاعدة بيانات PostgreSQL مع فهارس مخصصة، تخزين مؤقت عبر Redis، وCelery لمعالجة المهام الثقيلة وإرسال الفواتير. نُشر عبر Docker Compose على خوادم Linux.',
                'features': [
                    'لوحة تحكم تفاعلية لمتابعة خطوط الإنتاج في الوقت الفعلي',
                    'إدارة المخزون متعدد المستودعات مع تنبيهات النقص الآلية',
                    'وحدة الموارد البشرية، الرواتب، وسجلات الحضور والغياب',
                    'التقارير المالية المتقدمة وتصدير ملفات PDF و Excel',
                    'نظام صلاحيات وأدوار متدرج مع سجل تدقيق لكل عملية (Audit Trail)',
                    'واجهة باللغة العربية متوافقة بالكامل مع مختلف الأجهزة'
                ],
                'objectives': [
                    'بناء مصدر مركزي موثوق للبيانات (Single Source of Truth) بقاعدة بيانات PostgreSQL.',
                    'تقليل زمن الاستعلامات وتوليد التقارير المالية لأقل من ثانية واحدة.',
                    'تصميم واجهات مستخدم تفاعلية وسريعة الاستجابة بأحدث معايير Vue 3.',
                    'تطبيق نظام صلاحيات صارم (RBAC) يضمن سرية السجلات المالية والإدارية.'
                ],
                'metrics': [
                    {'label': 'استقرار وجاهزية النظام (Uptime)', 'value': '99.9%', 'desc': 'أداء متواصل دون انقطاعات بفضل بنية Docker و Nginx.'},
                    {'label': 'متوسط استجابة الواجهات البرمجية (API Latency)', 'value': '< 250ms', 'desc': 'تحسين الاستعلامات والتخزين المؤقت للبيانات المتكررة.'},
                    {'label': 'دقة السجلات والتدقيق المالي (Audit Trail)', 'value': '100%', 'desc': 'توثيق كامل لكل عملية إضافة أو تعديل أو اعتماد فوري.'}
                ],
                'is_featured': True,
                'sort_order': 1,
            },
            {
                'slug': 'survey-platform',
                'title': 'منصة جمع البيانات والمسوحات الميدانية',
                'category': 'تطبيقات الويب المتقدمة (PWA)',
                'role': 'Frontend Architect',
                'year': '2024',
                'short_description': 'منصة استبيانات للهاتف المحمول أولاً مع دعم العمل دون اتصال وتحديد الموقع الجغرافي وتحليلات فورية.',
                'full_description': 'منصة قوية لجمع البيانات مصممة للباحثين والفرق الميدانية في البيئات الصعبة. تدعم منطق الاستبيانات الديناميكية، التقاط البيانات دون اتصال، إحداثيات GPS، ومرفقات الصور ولوحات التحليلات المباشرة.',
                'tags': ['Vue 3', 'Django REST', 'PostgreSQL', 'PWA', 'Leaflet', 'IndexedDB'],
                'github_url': 'https://github.com',
                'demo_url': 'https://demo.example.com',
                'image': '/projects/survey.jpg',
                'accent_color': '#06B6D4',
                'problem': 'لم يكن لدى الفرق الميدانية وسيلة موثوقة لجمع البيانات في المناطق النائية ضعيفة الاتصال بالإنترنت، مما تسبب في فقدان الاستمارات وتأخير تحليل البيانات لأسابيع.',
                'architecture': 'تطبيق Progressive Web App (PWA) مع Service Workers ومزامنة IndexedDB للعمل بدون إنترنت. واجهة خلفية Django REST API مع JWT Authentication. قاعدة بيانات PostgreSQL مدعومة بـ PostGIS للاستعلامات المكانية والخرائط.',
                'features': [
                    'تطبيق PWA يعمل بدون اتصال بالإنترنت مع مزامنة تلقائية فور توفر الشبكة',
                    'التقاط إحداثيات GPS والصور مع التشفير المحلي',
                    'منشئ استمارات ديناميكي يدعم المنطق الشرطي والتفرعات',
                    'لوحة تحليلات وإحصاءات مكانية وخرائط حرارية تفاعلية',
                    'تصدير البيانات بصيغ متعددة CSV, Excel, GeoJSON',
                    'دعم متعدد اللغات مع واجهة RTL احترافية'
                ],
                'objectives': [
                    'دعم العمل بدون اتصال بالإنترنت Offline-First مع المزامنة الذكية.',
                    'التقاط الإحداثيات والخرائط الجغرافية بدقة عالية.',
                    'معالجة استمارات الاستبيان وتصديرها بصيغ متعددة.'
                ],
                'metrics': [
                    {'label': 'جاهزية العمل الميداني', 'value': '100%', 'desc': 'عمل كامل دون اتصال بالإنترنت مع مزامنة فورية.'},
                    {'label': 'سرعة جمع الاستمارات', 'value': '3x', 'desc': 'مضاعفة سرعة إدخال وتحليل البيانات الميدانية.'}
                ],
                'is_featured': False,
                'sort_order': 2,
            },
            {
                'slug': 'report-builder',
                'title': 'منشئ التقارير المرئي بالسحب والإفلات',
                'category': 'أدوات ذكاء الأعمال (BI Tools)',
                'role': 'Full Stack Engineer',
                'year': '2024',
                'short_description': 'منشئ تقارير مرئي يتيح لمستخدمي الأعمال تصميم وجدولة وتصدير تقارير مخصصة من أي مصدر بيانات بدون كتابة كود.',
                'full_description': 'أداة ذكاء أعمال (BI) مرئية تمكن مدراء الشركات ومحللي الأعمال من إنشاء تقارير ورسوم بيانية ولوحات تحكم معقدة عبر السحب والإفلات وتصديرها وجدولتها آلياً.',
                'tags': ['Vue 3', 'Vuedraggable', 'Django', 'Chart.js', 'Celery', 'Redis'],
                'github_url': 'https://github.com',
                'demo_url': 'https://demo.example.com',
                'image': '/projects/reports.jpg',
                'accent_color': '#EC4899',
                'problem': 'كان محللو الأعمال يعتمدون دائماً على فريق البرمجة لكل تعديل بسيط في التقارير، مما تسبب في اختناق تشغيلي وبطء اتخاذ القرارات الإدارية.',
                'architecture': 'لوحة سحب وإفلات سريعة مبنية بـ Vue 3 و Vuedraggable. محرك استعلامات SQL ديناميكي آمن في Django لمنع SQL Injection. مكتبات رسوم بيانية تفاعلية مع Chart.js، وجدولة تسليم التقارير عبر البريد باستخدام Celery Beat.',
                'features': [
                    'لوحة تصميم تفاعلية بالكامل بنظام السحب والإفلات (Drag & Drop)',
                    'أدوات متنوعة للمخططات البيانية (Bar, Line, Pie, Radar) والجداول المجمعة',
                    'منشئ فلاتر وشروط ديناميكية مخصصة لكل حقل بيانات',
                    'جدولة إرسال التقارير الدورية تلقائياً بصيغة PDF و Excel عبر البريد',
                    'مكتبة قوالب تقارير جاهزة للاستخدام وإعادة التخصيص',
                    'التحكم في صلاحيات الوصول ومشاركة التقارير مع الفريق'
                ],
                'objectives': [
                    'تمكين المستخدمين غير التقنيين من بناء تقارير مخصصة بالسحب والإفلات.',
                    'أتمتة جدولة التقارير وتصديرها عبر البريد الإلكتروني.',
                    'تأمين استعلامات البيانات من ثغرات الحقن البرمجي.'
                ],
                'metrics': [
                    {'label': 'توفير وقت التقارير', 'value': '80%', 'desc': 'تقليص وقت استخراج التقارير اليدوية لعدة دقائق.'},
                    {'label': 'تصدير دوري مؤتمت', 'value': '100%', 'desc': 'جدولة دقيقة وتسليم منتظم للإدارات المعنية.'}
                ],
                'is_featured': False,
                'sort_order': 3,
            }
        ]
        Project.objects.all().delete()
        for p_data in projects_data:
            Project.objects.create(**p_data)
        self.stdout.write(self.style.SUCCESS('Projects created.'))

        # 7. Timeline / Experience
        timeline_data = [
            {
                'year': '2025 - الآن',
                'title': 'تطوير وتوسيع أنظمة الـ ERP المؤسسية',
                'organization': 'مشاريع مؤسسية مستقلة',
                'description': 'تصميم وتسليم نظام ERP متكامل لإدارة عمليات التصنيع، المخازن، والرواتب لعدة مصانع وشركات مع تطبيق أفضل معايير الأمان وقابلية التوسع.',
                'icon': 'mdi-factory',
                'color': '#7B6EF6',
                'sort_order': 1
            },
            {
                'year': '2024',
                'title': 'بناء منصة جمع البيانات الميدانية',
                'organization': 'مشاريع أبحاث وبيانات',
                'description': 'تطوير منصة PWA متقدمة تدعم العمل في وضع عدم الاتصال وتلتقط الإحداثيات الجغرافية مع واجهات تحليل فورية.',
                'icon': 'mdi-map-marker-check',
                'color': '#06B6D4',
                'sort_order': 2
            },
            {
                'year': '2024',
                'title': 'إطلاق منشئ التقارير المرئي Drag & Drop',
                'organization': 'منصات ذكاء الأعمال',
                'description': 'بناء أداة بصرية تخدم أكثر من 200 مستخدم أعمال لتوليد التقارير المخصصة وتصديرها آلياً.',
                'icon': 'mdi-chart-bar',
                'color': '#EC4899',
                'sort_order': 3
            },
            {
                'year': '2023',
                'title': 'الانطلاق في هندسة وتطوير الـ Full Stack',
                'organization': 'تطوير وتدريب مهني مكثف',
                'description': 'إتقان منظومة Vue 3 وDjango REST Framework وتصميم قواعد البيانات العلائقية المعقدة في PostgreSQL.',
                'icon': 'mdi-code-braces',
                'color': '#10B981',
                'sort_order': 4
            }
        ]
        Experience.objects.all().delete()
        for item in timeline_data:
            Experience.objects.create(**item)
        self.stdout.write(self.style.SUCCESS('Timeline experiences created.'))

        # 8. Testimonials
        testimonials_data = [
            {
                'client_name': 'محمد العمري',
                'client_role': 'المدير التنفيذي',
                'client_company': 'شركة التصنيع المتقدم',
                'feedback_text': 'عبد الخالق مهندس استثنائي، سلّم نظام الـ ERP في الوقت المحدد وبجودة فاقت توقعاتنا. أسلوبه في حل المشكلات البرمجية وفهم سير العمل المعقد أحدث نقلة نوعية في كفاءة مصنعنا.',
                'rating': 5,
                'color': 'rgba(123,110,246,0.2)',
                'sort_order': 1
            },
            {
                'client_name': 'سارة الزهراني',
                'client_role': 'مديرة العمليات والمسوحات',
                'client_company': 'مركز أبحاث التنمية',
                'feedback_text': 'تعاملنا مع عبد الخالق في بناء منصة المسوحات الميدانية. ميزتا العمل بدون إنترنت والمزامنة الذكية حلتا لنا أكبر عائق كان يواجه الباحثين. الكود نظيف جداً والتعاون كان في قمة الاحترافية.',
                'rating': 5,
                'color': 'rgba(6,182,212,0.2)',
                'sort_order': 2
            },
            {
                'client_name': 'م. فهد السبيعي',
                'client_role': 'مدير التقنية (CTO)',
                'client_company': 'حلول الأعمال الذكية',
                'feedback_text': 'منشئ التقارير الذي بناه عبد الخالق وفّر على فريقنا عشرات الساعات أسبوعياً. دمج Vue 3 مع Django كان سلساً وسريع الاستجابة، والدعم الفني والمتابعة بعد التسليم كانت ممتازة.',
                'rating': 5,
                'color': 'rgba(236,72,153,0.2)',
                'sort_order': 3
            }
        ]
        Testimonial.objects.all().delete()
        for item in testimonials_data:
            Testimonial.objects.create(**item)
        self.stdout.write(self.style.SUCCESS('Testimonials created.'))

        # 9. Site Settings
        settings_defaults = {
            'site_title': 'عبد الخالق الصايدي | Full Stack Engineer',
            'meta_description': 'عبد الخالق الصايدي — مطور Full Stack متخصص في Vue 3 وDjango وPostgreSQL. أبني أنظمة مؤسسية وتطبيقات ويب عالية الأداء.',
            'hero_role_typing': 'Full Stack,Vue 3,Django,Backend,Frontend,ERP Systems',
            'threejs_enabled': 'true',
            'animations_enabled': 'true',
            'maintenance_mode': 'false',
            'contact_email_notifications': 'true',
            'whatsapp_number': '967771523243',
        }
        for key, val in settings_defaults.items():
            SiteSetting.objects.update_or_create(key=key, defaults={'value': val, 'group_name': 'general'})
        self.stdout.write(self.style.SUCCESS('Site settings created.'))

        self.stdout.write(self.style.SUCCESS('Database successfully seeded with complete production-ready data!'))
