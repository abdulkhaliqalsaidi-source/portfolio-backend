"""
Portfolio Data Template - Validator & Dry-Run Service
Performs comprehensive validation of JSON payload, entity structures,
types, ranges, foreign references, and generates dry-run preview statistics.
"""

import re
from api.models import (
    Profile, SkillCategory, Skill, Service, Project,
    Experience, Testimonial, Statistic, SiteSetting
)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
SLUG_REGEX = re.compile(r'^[a-zA-Z0-9_-]+$')


class TemplateValidationError(Exception):
    def __init__(self, errors):
        self.errors = errors
        super().__init__(str(errors))


class TemplateValidatorService:
    def __init__(self, payload, import_mode='UPSERT'):
        self.payload = payload
        self.import_mode = import_mode.upper() if import_mode else 'UPSERT'
        self.errors = []
        self.warnings = []
        self.summary = {}
        self.forecast = {'to_create': 0, 'to_update': 0, 'to_skip': 0}
        self.data = {}
        self.version = "1.0.0"

    def validate(self):
        """
        Executes full validation pipeline and returns validation report.
        """
        if not isinstance(self.payload, dict):
            self.errors.append({
                "entity": "root",
                "field": "payload",
                "message": "ملف القالب غير صالح: يجب أن يكون المحتوى عبارة عن كائن JSON صالح (Root Object)."
            })
            return self._build_report(valid=False)

        # 1. Version Check
        self.version = str(self.payload.get('version', '1.0.0'))
        if not self.version.startswith('1.'):
            self.warnings.append({
                "entity": "root",
                "field": "version",
                "message": f"إصدار القالب ({self.version}) قد يتطلب مطابقة مع الإصدار المدعوم (1.x.x)."
            })

        # Extract data dictionary
        if 'data' in self.payload and isinstance(self.payload['data'], dict):
            self.data = self.payload['data']
        else:
            self.data = self.payload

        if not self.data or not isinstance(self.data, dict):
            self.errors.append({
                "entity": "data",
                "field": "data",
                "message": "كائن البيانات فارغ أو غير موجود داخل ملف القالب."
            })
            return self._build_report(valid=False)

        # 2. Entity-by-Entity Deep Validation & Dry Run
        self._validate_profile()
        self._validate_skill_categories()
        self._validate_services()
        self._validate_projects()
        self._validate_experiences()
        self._validate_testimonials()
        self._validate_statistics()
        self._validate_settings()

        is_valid = len(self.errors) == 0
        return self._build_report(valid=is_valid)

    def _build_report(self, valid):
        total_records = sum(self.summary.values())
        return {
            "valid": valid,
            "version": self.version,
            "import_mode": self.import_mode,
            "summary": self.summary,
            "total_records": total_records,
            "forecast": self.forecast,
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
        }

    # ═════════════════════════════════════════════════════════════════════════
    # 1. Profile Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_profile(self):
        profile_data = self.data.get('profile')
        if not profile_data:
            return

        if not isinstance(profile_data, dict):
            self.errors.append({
                "entity": "profile",
                "field": "profile",
                "message": "بيانات الملف الشخصي (profile) يجب أن تكون كائناً (Object)."
            })
            return

        full_name = profile_data.get('full_name') or profile_data.get('name')
        if not full_name or not str(full_name).strip():
            self.errors.append({
                "entity": "profile",
                "field": "full_name",
                "message": "الاسم الكامل (full_name) مطلوب في الملف الشخصي."
            })

        email = profile_data.get('email')
        if email and not EMAIL_REGEX.match(str(email).strip()):
            self.warnings.append({
                "entity": "profile",
                "field": "email",
                "message": f"صيغة البريد الإلكتروني ({email}) قد تكون غير دقيقة."
            })

        yoe = profile_data.get('years_of_experience')
        if yoe is not None:
            try:
                yoe_val = int(yoe)
                if yoe_val < 0 or yoe_val > 70:
                    self.errors.append({
                        "entity": "profile",
                        "field": "years_of_experience",
                        "message": "سنوات الخبرة يجب أن تكون رقماً منطقياً بين 0 و 70."
                    })
            except (ValueError, TypeError):
                self.errors.append({
                    "entity": "profile",
                    "field": "years_of_experience",
                    "message": "سنوات الخبرة يجب أن تكون قيمة رقمية صحيحة."
                })

        self.summary['profile'] = 1
        exists = Profile.objects.exists()
        if exists:
            if self.import_mode in ['UPSERT', 'REPLACE']:
                self.forecast['to_update'] += 1
            elif self.import_mode in ['CREATE_ONLY', 'SKIP_EXISTING']:
                self.forecast['to_skip'] += 1
                self.warnings.append({
                    "entity": "profile",
                    "key": "Profile Singleton",
                    "message": "الملف الشخصي موجود مسبقاً وسيتم تخطي تحديثه بناءً على وضع الاستيراد المختار."
                })
        else:
            self.forecast['to_create'] += 1

    # ═════════════════════════════════════════════════════════════════════════
    # 2. Skill Categories & Skills Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_skill_categories(self):
        cats = self.data.get('skill_categories') or self.data.get('skills')
        if not cats:
            return

        if not isinstance(cats, list):
            self.errors.append({
                "entity": "skill_categories",
                "field": "skill_categories",
                "message": "تصنيفات المهارات (skill_categories) يجب أن تكون مصفوفة (Array)."
            })
            return

        seen_cat_names = set()
        cat_count = 0
        skill_count = 0

        for i, cat in enumerate(cats):
            if not isinstance(cat, dict):
                self.errors.append({
                    "entity": "skill_categories",
                    "index": i,
                    "message": f"عنصر التصنيف رقم #{i+1} يجب أن يكون كائناً (Object)."
                })
                continue

            name = str(cat.get('name', '')).strip()
            if not name:
                self.errors.append({
                    "entity": "skill_categories",
                    "index": i,
                    "field": "name",
                    "message": f"اسم تصنيف المهارات مطلوب في العنصر رقم #{i+1}."
                })
                continue

            if name in seen_cat_names:
                self.warnings.append({
                    "entity": "skill_categories",
                    "index": i,
                    "key": name,
                    "message": f"تصنيف المهارات '{name}' مكرر داخل ملف القالب."
                })
            seen_cat_names.add(name)
            cat_count += 1

            cat_exists = SkillCategory.objects.filter(name=name).exists()
            if cat_exists:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    self.forecast['to_update'] += 1
                else:
                    self.forecast['to_skip'] += 1
            else:
                self.forecast['to_create'] += 1

            # Validate Nested Skills
            skills = cat.get('skills', [])
            if isinstance(skills, list):
                seen_skills_in_cat = set()
                for j, sk in enumerate(skills):
                    if not isinstance(sk, dict):
                        self.errors.append({
                            "entity": "skills",
                            "index": f"{i}.{j}",
                            "message": f"المهارة رقم #{j+1} في تصنيف '{name}' غير صالحة."
                        })
                        continue

                    sk_name = str(sk.get('name', '')).strip()
                    if not sk_name:
                        self.errors.append({
                            "entity": "skills",
                            "index": f"{i}.{j}",
                            "field": "name",
                            "message": f"اسم المهارة مطلوب في العنصر #{j+1} ضمن تصنيف '{name}'."
                        })
                        continue

                    if sk_name in seen_skills_in_cat:
                        self.warnings.append({
                            "entity": "skills",
                            "index": f"{i}.{j}",
                            "key": f"{name} > {sk_name}",
                            "message": f"المهارة '{sk_name}' مكررة داخل نفس التصنيف '{name}'."
                        })
                    seen_skills_in_cat.add(sk_name)
                    skill_count += 1

                    # Check percentage range
                    pct = sk.get('proficiency_percentage', 85)
                    try:
                        pct_val = int(pct)
                        if pct_val < 0 or pct_val > 100:
                            self.errors.append({
                                "entity": "skills",
                                "index": f"{i}.{j}",
                                "field": "proficiency_percentage",
                                "message": f"نسبة إتقان المهارة '{sk_name}' ({pct_val}%) يجب أن تكون بين 0 و 100."
                            })
                    except (ValueError, TypeError):
                        self.errors.append({
                            "entity": "skills",
                            "index": f"{i}.{j}",
                            "field": "proficiency_percentage",
                            "message": f"نسبة إتقان المهارة '{sk_name}' يجب أن تكون رقماً صحيحاً."
                        })

                    # Dry Run Skill Check
                    sk_exists = Skill.objects.filter(category__name=name, name=sk_name).exists()
                    if sk_exists:
                        if self.import_mode in ['UPSERT', 'REPLACE']:
                            self.forecast['to_update'] += 1
                        else:
                            self.forecast['to_skip'] += 1
                    else:
                        self.forecast['to_create'] += 1

        self.summary['skill_categories'] = cat_count
        self.summary['skills'] = skill_count

    # ═════════════════════════════════════════════════════════════════════════
    # 3. Services Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_services(self):
        services = self.data.get('services')
        if not services:
            return

        if not isinstance(services, list):
            self.errors.append({
                "entity": "services",
                "field": "services",
                "message": "قائمة الخدمات (services) يجب أن تكون مصفوفة (Array)."
            })
            return

        seen_titles = set()
        count = 0

        for i, s in enumerate(services):
            if not isinstance(s, dict):
                self.errors.append({
                    "entity": "services",
                    "index": i,
                    "message": f"الخدمة رقم #{i+1} يجب أن تكون كائناً (Object)."
                })
                continue

            # Skip empty skeleton items
            if not any(str(v).strip() for v in s.values() if v is not None):
                continue

            title = str(
                s.get('title') or 
                s.get('name') or 
                s.get('service_name') or 
                s.get('headline') or 
                ''
            ).strip()

            if not title:
                self.errors.append({
                    "entity": "services",
                    "index": i,
                    "field": "title",
                    "message": f"عنوان الخدمة مطلوب في العنصر رقم #{i+1}."
                })
                continue

            if title in seen_titles:
                self.warnings.append({
                    "entity": "services",
                    "index": i,
                    "key": title,
                    "message": f"عنوان الخدمة '{title}' مكرر داخل القالب."
                })
            seen_titles.add(title)
            count += 1

            features = s.get('features', [])
            if features and not isinstance(features, list):
                self.errors.append({
                    "entity": "services",
                    "index": i,
                    "field": "features",
                    "message": f"مميزات الخدمة '{title}' (features) يجب أن تكون قائمة نصوص."
                })

            exists = Service.objects.filter(title=title).exists()
            if exists:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    self.forecast['to_update'] += 1
                else:
                    self.forecast['to_skip'] += 1
            else:
                self.forecast['to_create'] += 1

        self.summary['services'] = count

    # ═════════════════════════════════════════════════════════════════════════
    # 4. Projects & Gallery Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_projects(self):
        projects = self.data.get('projects')
        if not projects:
            return

        if not isinstance(projects, list):
            self.errors.append({
                "entity": "projects",
                "field": "projects",
                "message": "قائمة المشاريع (projects) يجب أن تكون مصفوفة (Array)."
            })
            return

        seen_slugs = set()
        count = 0

        for i, p in enumerate(projects):
            if not isinstance(p, dict):
                self.errors.append({
                    "entity": "projects",
                    "index": i,
                    "message": f"المشروع رقم #{i+1} يجب أن يكون كائناً (Object)."
                })
                continue

            # Skip empty skeleton items
            if not any(str(v).strip() for v in p.values() if v is not None and not isinstance(v, list)):
                continue

            title = str(
                p.get('title') or 
                p.get('name') or 
                p.get('project_name') or 
                ''
            ).strip()

            slug = str(p.get('slug', '')).strip()

            if not slug:
                if title:
                    slug = re.sub(r'[\s_]+', '-', title.lower())
                    slug = re.sub(r'[^a-zA-Z0-9\u0621-\u064A-]', '', slug)[:100]
                    if not slug:
                        slug = f"project-{i+1}"
                else:
                    self.errors.append({
                        "entity": "projects",
                        "index": i,
                        "field": "slug",
                        "message": f"المعرف اللطيف (slug) وعنوان المشروع مطلوبان في العنصر #{i+1}."
                    })
                    continue

            if not title:
                self.errors.append({
                    "entity": "projects",
                    "index": i,
                    "field": "title",
                    "message": f"عنوان المشروع مطلوب في المشروع ذو المعرف '{slug}'."
                })

            if slug in seen_slugs:
                self.errors.append({
                    "entity": "projects",
                    "index": i,
                    "key": slug,
                    "field": "slug",
                    "message": f"المعرف اللطيف للمشروع '{slug}' مكرر داخل القالب؛ يجب أن يكون فريداً لكل مشروع."
                })
            seen_slugs.add(slug)
            count += 1

            metrics = p.get('metrics', [])
            if metrics and isinstance(metrics, list):
                for m_idx, m in enumerate(metrics):
                    if not isinstance(m, (dict, str)):
                        self.warnings.append({
                            "entity": "projects",
                            "index": f"{i}.metrics.{m_idx}",
                            "key": slug,
                            "message": f"مؤشر الأداء رقم #{m_idx+1} في المشروع '{slug}' يجب أن يكون كائناً أو نصاً."
                        })

            exists = Project.objects.filter(slug=slug).exists()
            if exists:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    self.forecast['to_update'] += 1
                else:
                    self.forecast['to_skip'] += 1
            else:
                self.forecast['to_create'] += 1

        self.summary['projects'] = count

    # ═════════════════════════════════════════════════════════════════════════
    # 5. Experience / Timeline Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_experiences(self):
        experiences = self.data.get('experiences') or self.data.get('timeline')
        if not experiences:
            return

        if not isinstance(experiences, list):
            self.errors.append({
                "entity": "experiences",
                "field": "experiences",
                "message": "قائمة المسار المهني والخبرات يجب أن تكون مصفوفة (Array)."
            })
            return

        seen_keys = set()
        count = 0

        for i, e in enumerate(experiences):
            if not isinstance(e, dict):
                continue

            # Skip empty skeleton items
            if not any(str(v).strip() for v in e.values() if v is not None):
                continue

            title = str(
                e.get('title') or 
                e.get('role') or 
                e.get('position') or 
                e.get('job_title') or 
                e.get('name') or 
                e.get('headline') or 
                e.get('experience') or 
                ''
            ).strip()

            year = str(
                e.get('year') or 
                e.get('period') or 
                e.get('date') or 
                e.get('duration') or 
                e.get('time') or 
                ''
            ).strip()

            if not title:
                self.errors.append({
                    "entity": "experiences",
                    "index": i,
                    "field": "title",
                    "message": f"المسمى أو عنوان الخبرة مطلوب في العنصر #{i+1}."
                })
                continue

            nat_key = f"{year}:{title}"
            seen_keys.add(nat_key)
            count += 1

            exists = Experience.objects.filter(title=title, year=year).exists()
            if exists:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    self.forecast['to_update'] += 1
                else:
                    self.forecast['to_skip'] += 1
            else:
                self.forecast['to_create'] += 1

        self.summary['experiences'] = count

    # ═════════════════════════════════════════════════════════════════════════
    # 6. Testimonials Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_testimonials(self):
        testimonials = self.data.get('testimonials')
        if not testimonials:
            return

        if not isinstance(testimonials, list):
            self.errors.append({
                "entity": "testimonials",
                "field": "testimonials",
                "message": "قائمة آراء العملاء يجب أن تكون مصفوفة (Array)."
            })
            return

        count = 0
        for i, t in enumerate(testimonials):
            if not isinstance(t, dict):
                continue

            # Skip empty skeleton items
            if not any(str(v).strip() for v in t.values() if v is not None):
                continue

            c_name = str(
                t.get('client_name') or 
                t.get('name') or 
                t.get('author') or 
                t.get('client') or 
                t.get('reviewer') or 
                t.get('customer') or 
                t.get('person') or 
                ''
            ).strip()

            feedback = str(
                t.get('feedback_text') or 
                t.get('text') or 
                t.get('feedback') or 
                t.get('quote') or 
                t.get('comment') or 
                t.get('testimonial') or 
                t.get('content') or 
                t.get('message') or 
                t.get('review') or 
                t.get('body') or 
                ''
            ).strip()

            if not c_name:
                self.errors.append({
                    "entity": "testimonials",
                    "index": i,
                    "field": "client_name",
                    "message": f"اسم العميل مطلوب في التقييم #{i+1}."
                })
                continue

            if not feedback:
                # If feedback is empty, provide a gentle warning or fallback rather than failing
                self.warnings.append({
                    "entity": "testimonials",
                    "index": i,
                    "field": "feedback_text",
                    "message": f"نص التقييم غير محدد للعميل '{c_name}'."
                })

            rating = t.get('rating', 5)
            try:
                r_val = int(rating) if rating is not None else 5
                if r_val < 1 or r_val > 5:
                    self.errors.append({
                        "entity": "testimonials",
                        "index": i,
                        "field": "rating",
                        "message": f"التقييم للعميل '{c_name}' ({r_val}) يجب أن يكون بين 1 و 5 نجوم."
                    })
            except (ValueError, TypeError):
                self.errors.append({
                    "entity": "testimonials",
                    "index": i,
                    "field": "rating",
                    "message": f"قيمة التقييم للعميل '{c_name}' يجب أن تكون رقماً صحيحاً."
                })

            count += 1
            exists = Testimonial.objects.filter(client_name=c_name).exists()
            if exists:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    self.forecast['to_update'] += 1
                else:
                    self.forecast['to_skip'] += 1
            else:
                self.forecast['to_create'] += 1

        self.summary['testimonials'] = count

    # ═════════════════════════════════════════════════════════════════════════
    # 7. Statistics Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_statistics(self):
        statistics = self.data.get('statistics') or self.data.get('stats')
        if not statistics:
            return

        if not isinstance(statistics, list):
            self.errors.append({
                "entity": "statistics",
                "field": "statistics",
                "message": "قائمة الإحصائيات يجب أن تكون مصفوفة (Array)."
            })
            return

        count = 0
        for i, s in enumerate(statistics):
            if not isinstance(s, dict):
                continue

            # Skip empty skeleton items
            if not any(str(v).strip() for v in s.values() if v is not None):
                continue

            label = str(
                s.get('label') or 
                s.get('title') or 
                s.get('name') or 
                s.get('stat_name') or 
                ''
            ).strip()

            if not label:
                self.errors.append({
                    "entity": "statistics",
                    "index": i,
                    "field": "label",
                    "message": f"عنوان الإحصائية مطلوب في العنصر #{i+1}."
                })
                continue

            val = (
                s.get('value') if s.get('value') is not None else 
                s.get('val') if s.get('val') is not None else 
                s.get('count') if s.get('count') is not None else 
                s.get('number', 0)
            )
            try:
                int(val)
            except (ValueError, TypeError):
                self.errors.append({
                    "entity": "statistics",
                    "index": i,
                    "field": "value",
                    "message": f"قيمة الإحصائية '{label}' يجب أن تكون رقماً."
                })

            count += 1
            exists = Statistic.objects.filter(label=label).exists()
            if exists:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    self.forecast['to_update'] += 1
                else:
                    self.forecast['to_skip'] += 1
            else:
                self.forecast['to_create'] += 1

        self.summary['statistics'] = count

    # ═════════════════════════════════════════════════════════════════════════
    # 8. Settings Validation
    # ═════════════════════════════════════════════════════════════════════════
    def _validate_settings(self):
        settings_data = self.data.get('settings')
        if not settings_data:
            return

        count = 0
        if isinstance(settings_data, list):
            for i, st in enumerate(settings_data):
                if isinstance(st, dict):
                    key = str(st.get('key', '')).strip()
                    if not key:
                        self.warnings.append({
                            "entity": "settings",
                            "index": i,
                            "message": f"تم تخطي إعداد بدون مفتاح (key) في السطر #{i+1}."
                        })
                        continue
                    count += 1
                    exists = SiteSetting.objects.filter(key=key).exists()
                    if exists:
                        if self.import_mode in ['UPSERT', 'REPLACE']:
                            self.forecast['to_update'] += 1
                        else:
                            self.forecast['to_skip'] += 1
                    else:
                        self.forecast['to_create'] += 1
        elif isinstance(settings_data, dict):
            for k, v in settings_data.items():
                k_clean = str(k).strip()
                if not k_clean:
                    continue
                count += 1
                exists = SiteSetting.objects.filter(key=k_clean).exists()
                if exists:
                    if self.import_mode in ['UPSERT', 'REPLACE']:
                        self.forecast['to_update'] += 1
                    else:
                        self.forecast['to_skip'] += 1
                else:
                    self.forecast['to_create'] += 1

        self.summary['settings'] = count
