"""
Portfolio Data Template - Import Service
Executes atomic database transactions, supports multiple import modes
(CREATE_ONLY, UPSERT, SKIP_EXISTING, REPLACE), and logs import history and audit entries.
"""

import time
from django.db import transaction
from django.utils import timezone
from api.models import (
    Profile, SkillCategory, Skill, Service, Project,
    ProjectImage, Experience, Testimonial, Statistic, SiteSetting,
    DataImportHistory, AuditLog
)
from api.services.template_validator_service import TemplateValidatorService


class TemplateImportService:
    def __init__(self, payload, import_mode='UPSERT', filename='template.json', user=None, request=None, replace_confirmed=False):
        self.payload = payload
        self.import_mode = import_mode.upper() if import_mode else 'UPSERT'
        self.filename = filename or 'template.json'
        self.user = user
        self.request = request
        self.replace_confirmed = replace_confirmed
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.entity_stats = {}
        self.errors_log = []
        self.warnings_log = []

    def execute(self):
        """
        Validates payload and executes database import inside a transaction.
        Returns full execution summary dict.
        """
        start_time = time.time()

        # Step 1: Pre-validation
        validator = TemplateValidatorService(self.payload, import_mode=self.import_mode)
        validation_report = validator.validate()

        if not validation_report['valid']:
            duration_ms = int((time.time() - start_time) * 1000)
            history = self._save_history(
                status='FAILED',
                summary=validation_report['summary'],
                created=0, updated=0, skipped=0,
                errors=validation_report['errors'],
                warnings=validation_report['warnings'],
                duration_ms=duration_ms
            )
            return {
                "success": False,
                "status": "FAILED",
                "message": "فشل التحقق من صحة القالب. يرجى مراجعة الأخطاء الموضحة.",
                "history_id": history.id if history else None,
                "report": validation_report
            }

        # Step 2: Safety Check for REPLACE Mode
        if self.import_mode == 'REPLACE' and not self.replace_confirmed:
            duration_ms = int((time.time() - start_time) * 1000)
            return {
                "success": False,
                "status": "FAILED",
                "message": "وضع الاستبدال الشامل (REPLACE) يتطلب تأكيداً صريحاً قبل المتابعة.",
                "report": validation_report
            }

        data = validator.data
        self.warnings_log.extend(validation_report.get('warnings', []))

        # Step 3: Atomic Database Transaction
        try:
            with transaction.atomic():
                # If REPLACE mode, clean existing records for present entities
                if self.import_mode == 'REPLACE':
                    self._perform_replace_cleanup(data)

                # Process Entities in proper topological order
                if 'profile' in data and data['profile']:
                    self._import_profile(data['profile'])

                if 'skill_categories' in data or 'skills' in data:
                    cats = data.get('skill_categories') or data.get('skills', [])
                    self._import_skill_categories(cats)

                if 'services' in data and data['services']:
                    self._import_services(data['services'])

                if 'projects' in data and data['projects']:
                    self._import_projects(data['projects'])

                if 'experiences' in data or 'timeline' in data:
                    exps = data.get('experiences') or data.get('timeline', [])
                    self._import_experiences(exps)

                if 'testimonials' in data and data['testimonials']:
                    self._import_testimonials(data['testimonials'])

                if 'statistics' in data or 'stats' in data:
                    stats_list = data.get('statistics') or data.get('stats', [])
                    self._import_statistics(stats_list)

                if 'settings' in data and data['settings']:
                    self._import_settings(data['settings'])

            duration_ms = int((time.time() - start_time) * 1000)

            # Log to History & Audit
            history = self._save_history(
                status='SUCCESS',
                summary=self.entity_stats,
                created=self.created_count,
                updated=self.updated_count,
                skipped=self.skipped_count,
                errors=[],
                warnings=self.warnings_log,
                duration_ms=duration_ms
            )

            self._log_audit_success(duration_ms)

            return {
                "success": True,
                "status": "SUCCESS",
                "message": "تم استيراد بيانات القالب وتحديث الموقع بنجاح!",
                "history_id": history.id if history else None,
                "version": validator.version,
                "import_mode": self.import_mode,
                "summary": self.entity_stats,
                "created_count": self.created_count,
                "updated_count": self.updated_count,
                "skipped_count": self.skipped_count,
                "warnings": self.warnings_log,
                "duration_ms": duration_ms
            }

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            err_msg = str(e)
            self.errors_log.append({
                "entity": "transaction",
                "message": f"حدث خطأ أثناء حفظ البيانات في قاعدة البيانات: {err_msg}"
            })

            history = self._save_history(
                status='FAILED',
                summary=self.entity_stats,
                created=0, updated=0, skipped=0,
                errors=self.errors_log,
                warnings=self.warnings_log,
                duration_ms=duration_ms
            )

            return {
                "success": False,
                "status": "FAILED",
                "message": f"فشلت عملية الاستيراد وتم التراجع عن كافة التغييرات: {err_msg}",
                "history_id": history.id if history else None,
                "errors": self.errors_log,
                "duration_ms": duration_ms
            }

    # ═════════════════════════════════════════════════════════════════════════
    # REPLACE Cleanup
    # ═════════════════════════════════════════════════════════════════════════
    def _perform_replace_cleanup(self, data):
        if 'skill_categories' in data or 'skills' in data:
            Skill.objects.all().delete()
            SkillCategory.objects.all().delete()
        if 'services' in data:
            Service.objects.all().delete()
        if 'projects' in data:
            ProjectImage.objects.all().delete()
            Project.objects.all().delete()
        if 'experiences' in data or 'timeline' in data:
            Experience.objects.all().delete()
        if 'testimonials' in data:
            Testimonial.objects.all().delete()
        if 'statistics' in data or 'stats' in data:
            Statistic.objects.all().delete()

    # ═════════════════════════════════════════════════════════════════════════
    # Entity Importers
    # ═════════════════════════════════════════════════════════════════════════
    def _import_profile(self, p):
        exists = Profile.objects.exists()
        if exists and self.import_mode in ['CREATE_ONLY', 'SKIP_EXISTING']:
            self.skipped_count += 1
            self.entity_stats['profile'] = {'created': 0, 'updated': 0, 'skipped': 1}
            return

        defaults = {
            'full_name': p.get('full_name') or p.get('name', 'المطور'),
            'title': p.get('title', ''),
            'tagline': p.get('tagline', ''),
            'bio': p.get('bio', ''),
            'email': p.get('email', ''),
            'phone': p.get('phone', ''),
            'whatsapp': p.get('whatsapp', ''),
            'github': p.get('github', ''),
            'linkedin': p.get('linkedin', ''),
            'twitter': p.get('twitter', ''),
            'instagram': p.get('instagram', ''),
            'behance': p.get('behance', ''),
            'dribbble': p.get('dribbble', ''),
            'youtube': p.get('youtube', ''),
            'website': p.get('website', ''),
            'location': p.get('location', ''),
            'avatar': p.get('avatar', ''),
            'resume': p.get('resume', ''),
            'available_for_work': bool(p.get('available_for_work', True)),
            'years_of_experience': int(p.get('years_of_experience', 3) or 3),
        }

        obj, created = Profile.objects.update_or_create(id=1, defaults=defaults)
        if created:
            self.created_count += 1
            self.entity_stats['profile'] = {'created': 1, 'updated': 0, 'skipped': 0}
        else:
            self.updated_count += 1
            self.entity_stats['profile'] = {'created': 0, 'updated': 1, 'skipped': 0}

    def _import_skill_categories(self, cats):
        created_cats = 0
        updated_cats = 0
        skipped_cats = 0
        created_skills = 0
        updated_skills = 0
        skipped_skills = 0

        for cat_data in cats:
            name = str(cat_data.get('name', '')).strip()
            if not name:
                continue

            icon = cat_data.get('icon', 'mdi-folder-outline')
            sort_order = int(cat_data.get('sort_order', 0) or 0)

            cat_obj = SkillCategory.objects.filter(name=name).first()
            if not cat_obj:
                cat_obj = SkillCategory.objects.create(name=name, icon=icon, sort_order=sort_order)
                created_cats += 1
                self.created_count += 1
            else:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    cat_obj.icon = icon
                    cat_obj.sort_order = sort_order
                    cat_obj.save()
                    updated_cats += 1
                    self.updated_count += 1
                else:
                    skipped_cats += 1
                    self.skipped_count += 1

            # Process nested skills
            for sk in cat_data.get('skills', []):
                sk_name = str(sk.get('name', '')).strip()
                if not sk_name:
                    continue

                sk_icon = sk.get('icon', 'mdi-star-four-points-outline')
                color = sk.get('color', '#3B82F6')
                pct = int(sk.get('proficiency_percentage', 85) or 85)
                s_order = int(sk.get('sort_order', 0) or 0)
                is_vis = bool(sk.get('is_visible', True))

                skill_obj = Skill.objects.filter(category=cat_obj, name=sk_name).first()
                if not skill_obj:
                    Skill.objects.create(
                        category=cat_obj,
                        name=sk_name,
                        icon=sk_icon,
                        color=color,
                        proficiency_percentage=pct,
                        sort_order=s_order,
                        is_visible=is_vis
                    )
                    created_skills += 1
                    self.created_count += 1
                else:
                    if self.import_mode in ['UPSERT', 'REPLACE']:
                        skill_obj.icon = sk_icon
                        skill_obj.color = color
                        skill_obj.proficiency_percentage = pct
                        skill_obj.sort_order = s_order
                        skill_obj.is_visible = is_vis
                        skill_obj.save()
                        updated_skills += 1
                        self.updated_count += 1
                    else:
                        skipped_skills += 1
                        self.skipped_count += 1

        self.entity_stats['skill_categories'] = {'created': created_cats, 'updated': updated_cats, 'skipped': skipped_cats}
        self.entity_stats['skills'] = {'created': created_skills, 'updated': updated_skills, 'skipped': skipped_skills}

    def _import_services(self, services):
        c_count = 0
        u_count = 0
        s_count = 0

        for s in services:
            title = str(s.get('title', '')).strip()
            if not title:
                continue

            desc = s.get('description', '')
            icon = s.get('icon', 'mdi-monitor-dashboard')
            color = s.get('color', '#7B6EF6')
            features = s.get('features', [])
            sort_order = int(s.get('sort_order', 0) or 0)
            is_active = bool(s.get('is_active', True))

            obj = Service.objects.filter(title=title).first()
            if not obj:
                Service.objects.create(
                    title=title,
                    description=desc,
                    icon=icon,
                    color=color,
                    features=features if isinstance(features, list) else [],
                    sort_order=sort_order,
                    is_active=is_active
                )
                c_count += 1
                self.created_count += 1
            else:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    obj.description = desc
                    obj.icon = icon
                    obj.color = color
                    obj.features = features if isinstance(features, list) else []
                    obj.sort_order = sort_order
                    obj.is_active = is_active
                    obj.save()
                    u_count += 1
                    self.updated_count += 1
                else:
                    s_count += 1
                    self.skipped_count += 1

        self.entity_stats['services'] = {'created': c_count, 'updated': u_count, 'skipped': s_count}

    def _import_projects(self, projects):
        c_count = 0
        u_count = 0
        s_count = 0

        for p in projects:
            slug = str(p.get('slug', '')).strip()
            title = str(p.get('title', '')).strip()
            if not slug or not title:
                continue

            defaults = {
                'title': title,
                'category': p.get('category', ''),
                'role': p.get('role', ''),
                'year': str(p.get('year', '') or '2025'),
                'short_description': p.get('short_description', ''),
                'full_description': p.get('full_description', ''),
                'problem': p.get('problem', ''),
                'architecture': p.get('architecture', ''),
                'features': p.get('features', []) if isinstance(p.get('features'), list) else [],
                'objectives': p.get('objectives', []) if isinstance(p.get('objectives'), list) else [],
                'metrics': p.get('metrics', []) if isinstance(p.get('metrics'), list) else [],
                'tags': p.get('tags', []) if isinstance(p.get('tags'), list) else [],
                'image': p.get('image', ''),
                'demo_url': p.get('demo_url', ''),
                'github_url': p.get('github_url', ''),
                'accent_color': p.get('accent_color', '#7B6EF6'),
                'sort_order': int(p.get('sort_order', 0) or 0),
                'is_featured': bool(p.get('is_featured', False)),
                'is_published': bool(p.get('is_published', True)),
            }

            obj = Project.objects.filter(slug=slug).first()
            if not obj:
                proj_obj = Project.objects.create(slug=slug, **defaults)
                c_count += 1
                self.created_count += 1
            else:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    for k, v in defaults.items():
                        setattr(obj, k, v)
                    obj.save()
                    proj_obj = obj
                    u_count += 1
                    self.updated_count += 1
                else:
                    proj_obj = obj
                    s_count += 1
                    self.skipped_count += 1

            # Handle gallery if present
            gallery = p.get('gallery')
            if isinstance(gallery, list) and self.import_mode in ['UPSERT', 'REPLACE']:
                ProjectImage.objects.filter(project=proj_obj).delete()
                for g_idx, g in enumerate(gallery):
                    if isinstance(g, dict) and g.get('image_url'):
                        ProjectImage.objects.create(
                            project=proj_obj,
                            image_url=g.get('image_url'),
                            caption=g.get('caption', ''),
                            sort_order=int(g.get('sort_order', g_idx) or g_idx)
                        )

        self.entity_stats['projects'] = {'created': c_count, 'updated': u_count, 'skipped': s_count}

    def _import_experiences(self, experiences):
        c_count = 0
        u_count = 0
        s_count = 0

        for e in experiences:
            if not isinstance(e, dict):
                continue

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
                continue

            org = str(e.get('organization') or e.get('company') or e.get('org') or e.get('workplace') or '')
            desc = str(e.get('description') or e.get('desc') or e.get('details') or e.get('summary') or '')
            icon = e.get('icon', 'mdi-briefcase')
            color = e.get('color', '#7B6EF6')
            s_order = int(e.get('sort_order', 0) or 0)
            is_act = bool(e.get('is_active', True))

            obj = Experience.objects.filter(title=title, year=year).first()
            if not obj:
                Experience.objects.create(
                    year=year,
                    title=title,
                    organization=org,
                    description=desc,
                    icon=icon,
                    color=color,
                    sort_order=s_order,
                    is_active=is_act
                )
                c_count += 1
                self.created_count += 1
            else:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    obj.organization = org
                    obj.description = desc
                    obj.icon = icon
                    obj.color = color
                    obj.sort_order = s_order
                    obj.is_active = is_act
                    obj.save()
                    u_count += 1
                    self.updated_count += 1
                else:
                    s_count += 1
                    self.skipped_count += 1

        self.entity_stats['experiences'] = {'created': c_count, 'updated': u_count, 'skipped': s_count}

    def _import_testimonials(self, testimonials):
        c_count = 0
        u_count = 0
        s_count = 0

        for t in testimonials:
            if not isinstance(t, dict):
                continue

            if not any(str(v).strip() for v in t.values() if v is not None):
                continue

            client_name = str(
                t.get('client_name') or 
                t.get('name') or 
                t.get('author') or 
                t.get('client') or 
                t.get('reviewer') or 
                t.get('customer') or 
                t.get('person') or 
                ''
            ).strip()

            if not client_name:
                continue

            client_role = str(t.get('client_role') or t.get('role') or t.get('position') or t.get('title') or '')
            company = str(t.get('client_company') or t.get('company') or t.get('org') or t.get('organization') or '')
            avatar = str(t.get('client_avatar') or t.get('avatar') or '')
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
                ''
            )
            rating = int(t.get('rating', 5) or 5)
            color = t.get('color', 'rgba(123,110,246,0.2)')
            s_order = int(t.get('sort_order', 0) or 0)
            is_pub = bool(t.get('is_published', True))

            obj = Testimonial.objects.filter(client_name=client_name).first()
            if not obj:
                Testimonial.objects.create(
                    client_name=client_name,
                    client_role=client_role,
                    client_company=company,
                    client_avatar=avatar,
                    feedback_text=feedback,
                    rating=rating,
                    color=color,
                    sort_order=s_order,
                    is_published=is_pub
                )
                c_count += 1
                self.created_count += 1
            else:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    obj.client_role = client_role
                    obj.client_company = company
                    obj.client_avatar = avatar
                    obj.feedback_text = feedback
                    obj.rating = rating
                    obj.color = color
                    obj.sort_order = s_order
                    obj.is_published = is_pub
                    obj.save()
                    u_count += 1
                    self.updated_count += 1
                else:
                    s_count += 1
                    self.skipped_count += 1

        self.entity_stats['testimonials'] = {'created': c_count, 'updated': u_count, 'skipped': s_count}

    def _import_statistics(self, statistics):
        c_count = 0
        u_count = 0
        s_count = 0

        for s in statistics:
            label = str(s.get('label', '')).strip()
            if not label:
                continue

            value = int(s.get('value', 0) or 0)
            suffix = s.get('suffix', '+')
            desc = s.get('description', '')
            icon = s.get('icon', 'mdi-rocket-launch')
            color = s.get('color', '#7B6EF6')
            s_order = int(s.get('sort_order', 0) or 0)
            is_act = bool(s.get('is_active', True))

            obj = Statistic.objects.filter(label=label).first()
            if not obj:
                Statistic.objects.create(
                    label=label,
                    value=value,
                    suffix=suffix,
                    description=desc,
                    icon=icon,
                    color=color,
                    sort_order=s_order,
                    is_active=is_act
                )
                c_count += 1
                self.created_count += 1
            else:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    obj.value = value
                    obj.suffix = suffix
                    obj.description = desc
                    obj.icon = icon
                    obj.color = color
                    obj.sort_order = s_order
                    obj.is_active = is_act
                    obj.save()
                    u_count += 1
                    self.updated_count += 1
                else:
                    s_count += 1
                    self.skipped_count += 1

        self.entity_stats['statistics'] = {'created': c_count, 'updated': u_count, 'skipped': s_count}

    def _import_settings(self, settings_data):
        c_count = 0
        u_count = 0
        s_count = 0

        items = []
        if isinstance(settings_data, list):
            items = settings_data
        elif isinstance(settings_data, dict):
            items = [{"key": k, "value": v} for k, v in settings_data.items()]

        for st in items:
            key = str(st.get('key', '')).strip()
            if not key:
                continue

            val = str(st.get('value', ''))
            group = st.get('group_name', 'general')
            s_type = st.get('setting_type', 'text')
            desc = st.get('description', '')

            obj = SiteSetting.objects.filter(key=key).first()
            if not obj:
                SiteSetting.objects.create(
                    key=key,
                    value=val,
                    group_name=group,
                    setting_type=s_type,
                    description=desc
                )
                c_count += 1
                self.created_count += 1
            else:
                if self.import_mode in ['UPSERT', 'REPLACE']:
                    obj.value = val
                    if group: obj.group_name = group
                    if s_type: obj.setting_type = s_type
                    if desc: obj.description = desc
                    obj.save()
                    u_count += 1
                    self.updated_count += 1
                else:
                    s_count += 1
                    self.skipped_count += 1

        self.entity_stats['settings'] = {'created': c_count, 'updated': u_count, 'skipped': s_count}

    # ═════════════════════════════════════════════════════════════════════════
    # Logging & History Helpers
    # ═════════════════════════════════════════════════════════════════════════
    def _save_history(self, status, summary, created, updated, skipped, errors, warnings, duration_ms):
        try:
            return DataImportHistory.objects.create(
                filename=self.filename,
                version=str(self.payload.get('version', '1.0.0')) if isinstance(self.payload, dict) else '1.0.0',
                import_mode=self.import_mode,
                status=status,
                summary=summary or {},
                created_count=created,
                updated_count=updated,
                skipped_count=skipped,
                error_count=len(errors),
                warning_count=len(warnings),
                errors_log=errors,
                warnings_log=warnings,
                imported_by=self.user if self.user and self.user.is_authenticated else None,
                duration_ms=duration_ms
            )
        except Exception as e:
            print(f"Failed to create DataImportHistory: {e}")
            return None

    def _log_audit_success(self, duration_ms):
        try:
            ip = ""
            if self.request:
                x_forwarded = self.request.META.get('HTTP_X_FORWARDED_FOR')
                ip = x_forwarded.split(',')[0] if x_forwarded else self.request.META.get('REMOTE_ADDR', '')

            AuditLog.objects.create(
                user=self.user if self.user and self.user.is_authenticated else None,
                action=f"استيراد قالب بيانات ({self.import_mode})",
                entity_type="DataTemplate",
                entity_id=self.filename,
                details={
                    "filename": self.filename,
                    "mode": self.import_mode,
                    "created": self.created_count,
                    "updated": self.updated_count,
                    "skipped": self.skipped_count,
                    "duration_ms": duration_ms
                },
                ip_address=ip
            )
        except Exception as e:
            print(f"Audit log write failed: {e}")
