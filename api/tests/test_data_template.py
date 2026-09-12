from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from api.models import (
    Profile, SkillCategory, Skill, Service, Project,
    Experience, Testimonial, Statistic, SiteSetting,
    DataImportHistory
)
from api.services.template_export_service import export_portfolio_template
from api.services.template_validator_service import TemplateValidatorService
from api.services.template_import_service import TemplateImportService


class DataTemplateSystemTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='TestPassword123!'
        )
        self.client.force_authenticate(user=self.user)

        # Pre-seed some base data
        self.profile = Profile.objects.create(
            full_name="المطور الأصلي",
            title="مهندس برمجيات",
            email="dev@example.com"
        )
        self.cat = SkillCategory.objects.create(name="Frontend", icon="mdi-monitor")
        self.skill = Skill.objects.create(
            category=self.cat,
            name="Vue.js",
            proficiency_percentage=90
        )
        self.project = Project.objects.create(
            slug="initial-project",
            title="مشروع ابتدائي",
            short_description="وصف قصير"
        )

    def test_export_template_service(self):
        # 1. Export live database data
        live_export = export_portfolio_template(entities='all', with_examples=False, user=self.user)
        self.assertEqual(live_export['version'], "1.0.0")
        self.assertIn('profile', live_export['data'])
        self.assertEqual(live_export['data']['profile']['full_name'], "المطور الأصلي")
        self.assertEqual(len(live_export['data']['skill_categories']), 1)
        self.assertEqual(live_export['data']['skill_categories'][0]['name'], "Frontend")

        # 2. Export with examples
        example_export = export_portfolio_template(entities='all', with_examples=True, user=self.user)
        self.assertEqual(example_export['version'], "1.0.0")
        self.assertIn('profile', example_export['data'])
        self.assertTrue(len(example_export['data']['projects']) > 0)

    def test_export_api_endpoint(self):
        response = self.client.get('/api/admin/data-template/export/?entities=profile,projects&examples=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('profile', data['data'])
        self.assertIn('projects', data['data'])

    def test_validate_service_valid(self):
        payload = {
            "version": "1.0.0",
            "data": {
                "skill_categories": [
                    {
                        "name": "Backend",
                        "icon": "mdi-server",
                        "skills": [
                            {"name": "Django", "proficiency_percentage": 95}
                        ]
                    }
                ],
                "projects": [
                    {
                        "slug": "new-project",
                        "title": "مشروع جديد تماماً",
                        "short_description": "الوصف"
                    }
                ]
            }
        }
        validator = TemplateValidatorService(payload, import_mode='UPSERT')
        report = validator.validate()
        self.assertTrue(report['valid'])
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['forecast']['to_create'], 3) # Cat + Skill + Project

    def test_validate_service_invalid_ranges(self):
        payload = {
            "version": "1.0.0",
            "data": {
                "skill_categories": [
                    {
                        "name": "DevOps",
                        "skills": [
                            {"name": "Docker", "proficiency_percentage": 150} # Invalid > 100
                        ]
                    }
                ],
                "testimonials": [
                    {
                        "client_name": "العميل",
                        "feedback_text": "رأي",
                        "rating": 10 # Invalid > 5
                    }
                ]
            }
        }
        validator = TemplateValidatorService(payload, import_mode='UPSERT')
        report = validator.validate()
        self.assertFalse(report['valid'])
        self.assertTrue(len(report['errors']) >= 2)

    def test_import_upsert_mode(self):
        payload = {
            "version": "1.0.0",
            "data": {
                "profile": {
                    "full_name": "المطور المحدث",
                    "title": "Senior Architect"
                },
                "skill_categories": [
                    {
                        "name": "Frontend", # Existing category
                        "skills": [
                            {"name": "Vue.js", "proficiency_percentage": 99}, # Update existing skill
                            {"name": "TypeScript", "proficiency_percentage": 85} # New skill
                        ]
                    }
                ]
            }
        }
        importer = TemplateImportService(
            payload=payload,
            import_mode='UPSERT',
            filename='test_upsert.json',
            user=self.user
        )
        res = importer.execute()
        self.assertTrue(res['success'])
        self.assertEqual(res['status'], 'SUCCESS')

        # Check DB updates
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, "المطور المحدث")

        vue_skill = Skill.objects.get(category__name="Frontend", name="Vue.js")
        self.assertEqual(vue_skill.proficiency_percentage, 99)

        ts_skill = Skill.objects.get(category__name="Frontend", name="TypeScript")
        self.assertEqual(ts_skill.proficiency_percentage, 85)

        # Check History log
        history_entry = DataImportHistory.objects.filter(filename='test_upsert.json').first()
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.status, 'SUCCESS')

    def test_import_create_only_mode(self):
        payload = {
            "version": "1.0.0",
            "data": {
                "projects": [
                    {
                        "slug": "initial-project", # Existing
                        "title": "محاولة تعديل غير مسموحة",
                        "short_description": "لن يتغير"
                    },
                    {
                        "slug": "brand-new-project", # New
                        "title": "مشروع إضافي",
                        "short_description": "سيتم إنشاؤه"
                    }
                ]
            }
        }
        importer = TemplateImportService(
            payload=payload,
            import_mode='CREATE_ONLY',
            filename='test_create_only.json',
            user=self.user
        )
        res = importer.execute()
        self.assertTrue(res['success'])
        self.assertEqual(res['created_count'], 1)
        self.assertEqual(res['skipped_count'], 1)

        # Verify initial project was NOT changed
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "مشروع ابتدائي")

        # Verify brand new project was created
        self.assertTrue(Project.objects.filter(slug="brand-new-project").exists())

    def test_unauthenticated_access_denied(self):
        unauth_client = APIClient()
        res = unauth_client.get('/api/admin/data-template/export/')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
