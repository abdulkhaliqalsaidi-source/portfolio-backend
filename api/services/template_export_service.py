"""
Portfolio Data Template - Export Service
Generates structured, database-ID-free JSON templates with Natural Keys.
"""

from datetime import datetime
from django.utils import timezone
from api.models import (
    Profile, SkillCategory, Skill, Service, Project,
    ProjectImage, Experience, Testimonial, Statistic, SiteSetting
)


EXAMPLE_DATA = {
    "profile": {
        "full_name": "عبد الخالق الصايدي",
        "title": "مطور Full Stack Engineer",
        "tagline": "أبني أنظمة قابلة للتوسع وواجهات أنيقة تُشحن للإنتاج.",
        "bio": "مهندس برمجيات ومطور Full Stack ذو خبرة تفوق 3 سنوات في بناء أنظمة مؤسسية معقدة (ERP)، منصات ويب تفاعلية، وواجهات RESTful APIs عالية الأداء باستخدام Vue 3 وDjango وPostgreSQL.",
        "email": "abdul.khaliq.al.saidi@gmail.com",
        "phone": "+967 771 523 243",
        "whatsapp": "967771523243",
        "github": "https://github.com",
        "linkedin": "https://linkedin.com",
        "twitter": "https://x.com",
        "instagram": "https://instagram.com",
        "behance": "https://behance.net",
        "dribbble": "https://dribbble.com",
        "youtube": "https://youtube.com",
        "website": "https://myportfolio.dev",
        "location": "اليمن",
        "avatar": "/media/uploads/avatar.webp",
        "resume": "/media/uploads/resume.pdf",
        "available_for_work": True,
        "years_of_experience": 3
    },
    "skill_categories": [
      {
        "name": "تطوير الواجهات الأمامية (Frontend)",
        "icon": "mdi-monitor",
        "sort_order": 1,
        "skills": [
          {
            "name": "Vue.js 3 / Composition API",
            "icon": "mdi-vuejs",
            "color": "#42B883",
            "proficiency_percentage": 95,
            "sort_order": 1,
            "is_visible": True
          },
          {
            "name": "Pinia & Vue Router",
            "icon": "mdi-fruit-pineapple",
            "color": "#FBBF24",
            "proficiency_percentage": 90,
            "sort_order": 2,
            "is_visible": True
          }
        ]
      },
      {
        "name": "تطوير الواجهات الخلفية (Backend)",
        "icon": "mdi-server",
        "sort_order": 2,
        "skills": [
          {
            "name": "Django & Django REST Framework",
            "icon": "mdi-language-python",
            "color": "#092E20",
            "proficiency_percentage": 92,
            "sort_order": 1,
            "is_visible": True
          },
          {
            "name": "PostgreSQL & Database Design",
            "icon": "mdi-database",
            "color": "#336791",
            "proficiency_percentage": 88,
            "sort_order": 2,
            "is_visible": True
          }
        ]
      }
    ],
    "services": [
      {
        "title": "تطوير الأنظمة المؤسسية (ERP)",
        "description": "بناء أنظمة إدارة الموارد والمخازن والحسابات للشركات والمصانع بمعمارية قوية.",
        "icon": "mdi-domain",
        "color": "#7B6EF6",
        "features": [
          "إدارة المستودعات وسلاسل الإمداد",
          "نظام فواتير وضريبة إلكترونية متوافق",
          "لوحة تحكم وتحليلات بيانية فورية"
        ],
        "sort_order": 1,
        "is_active": True
      }
    ],
    "projects": [
      {
        "slug": "smart-erp-platform",
        "title": "منصة ERP الذكية للمصانع والشركات",
        "category": "أنظمة مؤسسية (ERP)",
        "role": "Lead Architect & Full Stack",
        "year": "2025",
        "short_description": "نظام مؤسسي شامل لإدارة المبيعات، المخازن، والإنتاج بدقة عالية وتزامن لحظي.",
        "full_description": "تم تصميم وتطوير النظام لخدمة أكثر من 15 فرعاً تجارياً، مع معالجة ما يزيد عن 50,000 عملية يومياً بزمن استجابة أقل من 80ms.",
        "problem": "كانت الشركة تعاني من بطء في ترحيل قيود المخزون وتشتت البيانات بين الفروع.",
        "architecture": "تم بناء النظام بمعمارية Modular منفصلة باستخدام Vue 3 و Django REST مع قاعدة بيانات PostgreSQL مدعومة بفهارس B-Tree محسنة.",
        "features": [
          "مزامنة فورية للبيانات عبر WebSockets",
          "لوحة تحكم إدارية متقدمة تدعم الصلاحيات الدقيقة",
          "تقارير محاسبية تفصيلية وتصدير PDF / Excel"
        ],
        "objectives": [
          "تقليص زمن جرد المخزون بنسبة 70%",
          "أتمتة الفواتير الإلكترونية والربط المحاسبي"
        ],
        "metrics": [
          {
            "label": "زمن الاستجابة",
            "value": "< 80ms",
            "desc": "استعلامات محسنة بدون اختناقات"
          },
          {
            "label": "الاستقرار التشغيلي",
            "value": "99.98%",
            "desc": "شحن مستمر دون توقف"
          }
        ],
        "tags": ["Vue 3", "Django", "PostgreSQL", "Tailwind CSS"],
        "image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
        "demo_url": "https://erp.example.com",
        "github_url": "https://github.com/example/erp",
        "accent_color": "#3B82F6",
        "sort_order": 1,
        "is_featured": True,
        "is_published": True,
        "gallery": [
          {
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&q=80",
            "caption": "لوحة التحليلات المركزية",
            "sort_order": 1
          }
        ]
      }
    ],
    "experiences": [
      {
        "year": "2024 - 2025",
        "title": "Lead Full Stack Engineer",
        "organization": "شركة التقنية المتقدمة للحلول البرمجية",
        "description": "قيادة الفريق التقني في بناء وتطوير منصات وتطبيقات ويب سحابية تخدم آلاف المستخدمين النشطين.",
        "icon": "mdi-briefcase-check",
        "color": "#3B82F6",
        "sort_order": 1,
        "is_active": True
      }
    ],
    "testimonials": [
      {
        "client_name": "م. عبد الرحمن الأحمدي",
        "client_role": "المدير التنفيذي • شركة الإبداع التقني",
        "client_company": "الإبداع التقني",
        "client_avatar": "",
        "feedback_text": "عمل احترافي من الطراز الرفيع، التزام تام بالمواعيد ودقة استثنائية في بناء المعمارية البرمجية.",
        "rating": 5,
        "color": "rgba(59,130,246,0.15)",
        "sort_order": 1,
        "is_published": True
      }
    ],
    "statistics": [
      {
        "label": "مشروع منجز",
        "value": 30,
        "suffix": "+",
        "description": "أنظمة وتطبيقات متكاملة تم شحنها للإنتاج الفعلي.",
        "icon": "mdi-rocket-launch",
        "color": "#7B6EF6",
        "sort_order": 1,
        "is_active": True
      },
      {
        "label": "نظام مؤسسي",
        "value": 8,
        "suffix": "",
        "description": "حلول شاملة لإدارة المخازن والمبيعات وسير العمليات.",
        "icon": "mdi-domain",
        "color": "#06B6D4",
        "sort_order": 2,
        "is_active": True
      }
    ],
    "settings": [
      {
        "key": "site_title",
        "value": "عبد الخالق الصايدي | معرض الأعمال والأنظمة",
        "group_name": "general",
        "setting_type": "text",
        "description": "عنوان الموقع في المتصفح ومحركات البحث"
      },
      {
        "key": "typing_roles",
        "value": "Lead Full Stack Engineer, Django & Vue 3 Specialist, ERP System Builder",
        "group_name": "homepage",
        "setting_type": "text",
        "description": "أدوار الكتابة التفاعلية في الهيدر"
      }
    ]
}


EMPTY_STRUCTURE = {
    "profile": {
        "full_name": "",
        "title": "",
        "tagline": "",
        "bio": "",
        "email": "",
        "phone": "",
        "whatsapp": "",
        "github": "",
        "linkedin": "",
        "twitter": "",
        "instagram": "",
        "behance": "",
        "dribbble": "",
        "youtube": "",
        "website": "",
        "location": "",
        "avatar": "",
        "resume": "",
        "available_for_work": True,
        "years_of_experience": 0
    },
    "skill_categories": [
      {
        "name": "",
        "icon": "mdi-folder-outline",
        "sort_order": 0,
        "skills": [
          {
            "name": "",
            "icon": "mdi-star-four-points-outline",
            "color": "#3B82F6",
            "proficiency_percentage": 85,
            "sort_order": 0,
            "is_visible": True
          }
        ]
      }
    ],
    "services": [
      {
        "title": "",
        "description": "",
        "icon": "mdi-monitor-dashboard",
        "color": "#7B6EF6",
        "features": [],
        "sort_order": 0,
        "is_active": True
      }
    ],
    "projects": [
      {
        "slug": "",
        "title": "",
        "category": "",
        "role": "",
        "year": "",
        "short_description": "",
        "full_description": "",
        "problem": "",
        "architecture": "",
        "features": [],
        "objectives": [],
        "metrics": [],
        "tags": [],
        "image": "",
        "demo_url": "",
        "github_url": "",
        "accent_color": "#7B6EF6",
        "sort_order": 0,
        "is_featured": False,
        "is_published": True,
        "gallery": []
      }
    ],
    "experiences": [
      {
        "year": "",
        "title": "",
        "organization": "",
        "description": "",
        "icon": "mdi-briefcase",
        "color": "#7B6EF6",
        "sort_order": 0,
        "is_active": True
      }
    ],
    "testimonials": [
      {
        "client_name": "",
        "client_role": "",
        "client_company": "",
        "client_avatar": "",
        "feedback_text": "",
        "rating": 5,
        "color": "rgba(123,110,246,0.2)",
        "sort_order": 0,
        "is_published": True
      }
    ],
    "statistics": [
      {
        "label": "",
        "value": 0,
        "suffix": "+",
        "description": "",
        "icon": "mdi-rocket-launch",
        "color": "#7B6EF6",
        "sort_order": 0,
        "is_active": True
      }
    ],
    "settings": []
}


def build_live_profile_data():
    profile = Profile.objects.first()
    if not profile:
        return EXAMPLE_DATA["profile"]
    return {
        "full_name": profile.full_name,
        "title": profile.title,
        "tagline": profile.tagline,
        "bio": profile.bio,
        "email": profile.email,
        "phone": profile.phone,
        "whatsapp": profile.whatsapp,
        "github": profile.github,
        "linkedin": profile.linkedin,
        "twitter": profile.twitter,
        "instagram": profile.instagram,
        "behance": profile.behance,
        "dribbble": profile.dribbble,
        "youtube": profile.youtube,
        "website": profile.website,
        "location": profile.location,
        "avatar": profile.avatar,
        "resume": profile.resume,
        "available_for_work": profile.available_for_work,
        "years_of_experience": profile.years_of_experience,
    }


def build_live_skill_categories_data():
    categories = SkillCategory.objects.prefetch_related('skills').all()
    if not categories.exists():
        return []
    result = []
    for cat in categories:
        cat_skills = []
        for sk in cat.skills.all():
            cat_skills.append({
                "name": sk.name,
                "icon": sk.icon,
                "color": sk.color,
                "proficiency_percentage": sk.proficiency_percentage,
                "sort_order": sk.sort_order,
                "is_visible": sk.is_visible,
            })
        result.append({
            "name": cat.name,
            "icon": cat.icon,
            "sort_order": cat.sort_order,
            "skills": cat_skills
        })
    return result


def build_live_services_data():
    services = Service.objects.all()
    if not services.exists():
        return []
    return [
        {
            "title": s.title,
            "description": s.description,
            "icon": s.icon,
            "color": s.color,
            "features": s.features or [],
            "sort_order": s.sort_order,
            "is_active": s.is_active,
        }
        for s in services
    ]


def build_live_projects_data():
    projects = Project.objects.prefetch_related('gallery').all()
    if not projects.exists():
        return []
    result = []
    for p in projects:
        gallery_items = [
            {
                "image_url": img.image_url,
                "caption": img.caption,
                "sort_order": img.sort_order,
            }
            for img in p.gallery.all()
        ]
        result.append({
            "slug": p.slug,
            "title": p.title,
            "category": p.category,
            "role": p.role,
            "year": p.year,
            "short_description": p.short_description,
            "full_description": p.full_description,
            "problem": p.problem,
            "architecture": p.architecture,
            "features": p.features or [],
            "objectives": p.objectives or [],
            "metrics": p.metrics or [],
            "tags": p.tags or [],
            "image": p.image,
            "demo_url": p.demo_url,
            "github_url": p.github_url,
            "accent_color": p.accent_color,
            "sort_order": p.sort_order,
            "is_featured": p.is_featured,
            "is_published": p.is_published,
            "gallery": gallery_items
        })
    return result


def build_live_experiences_data():
    experiences = Experience.objects.all()
    if not experiences.exists():
        return []
    return [
        {
            "year": e.year,
            "title": e.title,
            "organization": e.organization,
            "description": e.description,
            "icon": e.icon,
            "color": e.color,
            "sort_order": e.sort_order,
            "is_active": e.is_active,
        }
        for e in experiences
    ]


def build_live_testimonials_data():
    testimonials = Testimonial.objects.all()
    if not testimonials.exists():
        return []
    return [
        {
            "client_name": t.client_name,
            "client_role": t.client_role,
            "client_company": t.client_company,
            "client_avatar": t.client_avatar,
            "feedback_text": t.feedback_text,
            "rating": t.rating,
            "color": t.color,
            "sort_order": t.sort_order,
            "is_published": t.is_published,
        }
        for t in testimonials
    ]


def build_live_statistics_data():
    statistics = Statistic.objects.all()
    if not statistics.exists():
        return []
    return [
        {
            "label": s.label,
            "value": s.value,
            "suffix": s.suffix,
            "description": s.description,
            "icon": s.icon,
            "color": s.color,
            "sort_order": s.sort_order,
            "is_active": s.is_active,
        }
        for s in statistics
    ]


def build_live_settings_data():
    settings = SiteSetting.objects.all()
    if not settings.exists():
        return []
    return [
        {
            "key": st.key,
            "value": st.value,
            "group_name": st.group_name,
            "setting_type": st.setting_type,
            "description": st.description,
        }
        for st in settings
    ]


def export_portfolio_template(entities=None, with_examples=False, user=None):
    """
    Main export entry point.
    :param entities: list of entity names to export, or None/all for all
    :param with_examples: boolean, whether to use example mock templates if DB is empty or requested
    :param user: current authenticated User
    :return: dict conforming to Portfolio Template Specification v1.0.0
    """
    all_supported_entities = [
        'profile', 'skill_categories', 'services', 'projects',
        'experiences', 'testimonials', 'statistics', 'settings'
    ]

    if not entities or entities == 'all':
        selected_entities = all_supported_entities
    elif isinstance(entities, str):
        selected_entities = [e.strip() for e in entities.split(',') if e.strip() in all_supported_entities]
    else:
        selected_entities = [e for e in entities if e in all_supported_entities]

    data = {}

    for ent in selected_entities:
        if with_examples:
            data[ent] = EXAMPLE_DATA.get(ent, [])
        else:
            if ent == 'profile':
                data[ent] = build_live_profile_data()
            elif ent == 'skill_categories':
                data[ent] = build_live_skill_categories_data()
            elif ent == 'services':
                data[ent] = build_live_services_data()
            elif ent == 'projects':
                data[ent] = build_live_projects_data()
            elif ent == 'experiences':
                data[ent] = build_live_experiences_data()
            elif ent == 'testimonials':
                data[ent] = build_live_testimonials_data()
            elif ent == 'statistics':
                data[ent] = build_live_statistics_data()
            elif ent == 'settings':
                data[ent] = build_live_settings_data()

    template = {
        "$schema": "portfolio-data-template-v1",
        "version": "1.0.0",
        "metadata": {
            "name": "Portfolio Data Template",
            "description": "قالب البيانات الموحد لموقع البورتفوليو",
            "type": "template_with_examples" if with_examples else "live_database_export",
            "exported_at": timezone.now().isoformat(),
            "exported_by": user.username if user and user.is_authenticated else "admin",
            "entities_count": len(selected_entities),
            "included_entities": selected_entities,
        },
        "data": data
    }

    return template
