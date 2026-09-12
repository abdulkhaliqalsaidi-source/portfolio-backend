from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomTokenObtainPairView, CurrentUserView, ChangePasswordView,
    PublicContentView, PublicProjectDetailView, PublicContactView,
    DashboardSummaryView, ProfileViewSet, ProjectViewSet,
    SkillCategoryViewSet, SkillViewSet, ServiceViewSet,
    ExperienceViewSet, TestimonialViewSet, StatisticViewSet,
    ContactMessageViewSet, SiteSettingViewSet, UserViewSet,
    AuditLogViewSet, MediaUploadView,
    DataTemplateExportView, DataTemplateValidateView,
    DataTemplateImportView, DataImportHistoryViewSet,
    BlogPostViewSet
)

router = DefaultRouter()
router.register(r'admin/profile', ProfileViewSet, basename='admin-profile')
router.register(r'admin/projects', ProjectViewSet, basename='admin-projects')
router.register(r'admin/posts', BlogPostViewSet, basename='admin-posts')
router.register(r'public/posts', BlogPostViewSet, basename='public-posts')
router.register(r'admin/skill-categories', SkillCategoryViewSet, basename='admin-skill-categories')
router.register(r'admin/skills', SkillViewSet, basename='admin-skills')
router.register(r'admin/services', ServiceViewSet, basename='admin-services')
router.register(r'admin/timeline', ExperienceViewSet, basename='admin-timeline')
router.register(r'admin/testimonials', TestimonialViewSet, basename='admin-testimonials')
router.register(r'admin/statistics', StatisticViewSet, basename='admin-statistics')
router.register(r'admin/messages', ContactMessageViewSet, basename='admin-messages')
router.register(r'admin/settings', SiteSettingViewSet, basename='admin-settings')
router.register(r'admin/users', UserViewSet, basename='admin-users')
router.register(r'admin/audit-logs', AuditLogViewSet, basename='admin-audit-logs')
router.register(r'admin/data-template/history', DataImportHistoryViewSet, basename='admin-data-template-history')

urlpatterns = [
    # Auth & Tokens
    path('auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', CurrentUserView.as_view(), name='auth_me'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='auth_change_password'),

    # Public Endpoints
    path('public/content/', PublicContentView.as_view(), name='public_content'),
    path('public/project/<str:identifier>/', PublicProjectDetailView.as_view(), name='public_project_detail'),
    path('public/contact/', PublicContactView.as_view(), name='public_contact'),

    # Admin Analytics & Media
    path('admin/dashboard-summary/', DashboardSummaryView.as_view(), name='admin_dashboard_summary'),
    path('admin/media/', MediaUploadView.as_view(), name='admin_media'),

    # Portfolio Data Template Endpoints
    path('admin/data-template/export/', DataTemplateExportView.as_view(), name='admin_data_template_export'),
    path('admin/data-template/validate/', DataTemplateValidateView.as_view(), name='admin_data_template_validate'),
    path('admin/data-template/import/', DataTemplateImportView.as_view(), name='admin_data_template_import'),

    # Router URLs
    path('', include(router.urls)),
]

