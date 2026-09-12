from django.contrib import admin
from .models import (
    Profile, SkillCategory, Skill, Service, Project,
    ProjectImage, Experience, Testimonial, Statistic,
    ContactMessage, SiteSetting, AuditLog, MediaFile
)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'email', 'phone', 'available_for_work', 'updated_at')

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'sort_order')
    inlines = [SkillInline]

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'proficiency_percentage', 'is_visible', 'sort_order')
    list_filter = ('category', 'is_visible')
    search_fields = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'color', 'is_active', 'sort_order')
    list_filter = ('is_active',)

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_featured', 'is_published', 'sort_order', 'created_at')
    list_filter = ('is_featured', 'is_published')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectImageInline]

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('year', 'title', 'organization', 'is_active', 'sort_order')
    list_filter = ('is_active',)

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('client_name', 'client_role', 'rating', 'is_published', 'created_at')
    list_filter = ('is_published', 'rating')

@admin.register(Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ('label', 'value', 'suffix', 'is_active', 'sort_order')
    list_filter = ('is_active',)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('sender_name', 'sender_email', 'subject', 'status', 'is_read', 'created_at')
    list_filter = ('status', 'is_read', 'created_at')
    search_fields = ('sender_name', 'sender_email', 'subject', 'message')

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'group_name', 'setting_type', 'updated_at')
    list_filter = ('group_name', 'setting_type')
    search_fields = ('key', 'value', 'description')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'action', 'entity_type', 'entity_id', 'ip_address')
    list_filter = ('action', 'entity_type', 'created_at')
    search_fields = ('action', 'entity_type', 'entity_id', 'ip_address')

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'file_size', 'uploaded_at')
    list_filter = ('file_type', 'uploaded_at')
