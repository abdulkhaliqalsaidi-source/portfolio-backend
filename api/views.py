from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q

from .models import (
    Profile, SkillCategory, Skill, Service, Project,
    ProjectImage, Experience, Testimonial, Statistic,
    ContactMessage, SiteSetting, AuditLog, MediaFile,
    DataImportHistory, BlogPost
)
from .serializers import (
    CustomTokenObtainPairSerializer, UserSerializer, ProfileSerializer,
    SkillCategorySerializer, SkillSerializer, ServiceSerializer,
    ProjectSerializer, ProjectImageSerializer, ExperienceSerializer,
    TestimonialSerializer, StatisticSerializer, ContactMessageSerializer,
    ContactCreateSerializer, SiteSettingSerializer, AuditLogSerializer,
    MediaFileSerializer, DataImportHistorySerializer, BlogPostSerializer
)
from .permissions import IsAdminOrReadOnly, IsSuperUserOnly
from .services.template_export_service import export_portfolio_template
from .services.template_validator_service import TemplateValidatorService
from .services.template_import_service import TemplateImportService
from django.utils import timezone
import json


def log_action(user, action_name, entity_type, entity_id="", details=None, request=None):
    try:
        ip = ""
        if request:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR', '')
        
        AuditLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action_name,
            entity_type=entity_type,
            entity_id=str(entity_id),
            details=details or {},
            ip_address=ip
        )
    except Exception as e:
        print(f"Error writing audit log: {e}")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get('username')
            user = User.objects.filter(username=username).first()
            if user:
                log_action(user, "تسجيل دخول ناجح", "Authentication", user.id, {"username": username}, request)
        return response


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({"error": "كلمة المرور الحالية غير صحيحة."}, status=status.HTTP_400_BAD_REQUEST)

        if not new_password or len(new_password) < 6:
            return Response({"error": "كلمة المرور الجديدة يجب أن لا تقل عن 6 أحرف."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        log_action(user, "تغيير كلمة المرور", "User", user.id, {}, request)
        return Response({"message": "تم تغيير كلمة المرور بنجاح."})


# ════════════════════════════════════════
# PUBLIC APIS
# ════════════════════════════════════════

class PublicContentView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        profile, _ = Profile.objects.get_or_create(id=1)
        profile_data = ProfileSerializer(profile, context={'request': request}).data

        stats = Statistic.objects.filter(is_active=True).order_by('sort_order', 'id')
        stats_data = StatisticSerializer(stats, many=True, context={'request': request}).data

        services = Service.objects.filter(is_active=True).order_by('sort_order', 'id')
        services_data = ServiceSerializer(services, many=True, context={'request': request}).data

        # Structured tech stack
        categories = SkillCategory.objects.prefetch_related('skills').order_by('sort_order', 'id')
        tech_stack_dict = {}
        for cat in categories:
            visible_skills = cat.skills.filter(is_visible=True).order_by('sort_order', 'id')
            tech_stack_dict[cat.name] = SkillSerializer(visible_skills, many=True, context={'request': request}).data

        projects = Project.objects.filter(is_published=True).order_by('sort_order', '-created_at')
        projects_data = ProjectSerializer(projects, many=True, context={'request': request}).data

        testimonials = Testimonial.objects.filter(is_published=True).order_by('sort_order', '-created_at')
        testimonials_data = TestimonialSerializer(testimonials, many=True, context={'request': request}).data

        timeline = Experience.objects.filter(is_active=True).order_by('sort_order', '-id')
        timeline_data = ExperienceSerializer(timeline, many=True, context={'request': request}).data

        posts = BlogPost.objects.filter(is_published=True).order_by('-is_featured', 'sort_order', '-published_at')
        posts_data = BlogPostSerializer(posts, many=True, context={'request': request}).data

        # Settings
        settings_objs = SiteSetting.objects.all()
        settings_dict = {s.key: s.value for s in settings_objs}

        return Response({
            'profile': profile_data,
            'developer': profile_data,  # Alias for smooth frontend compat
            'stats': stats_data,
            'services': services_data,
            'techStack': tech_stack_dict,
            'skillCategories': SkillCategorySerializer(categories, many=True, context={'request': request}).data,
            'projects': projects_data,
            'testimonials': testimonials_data,
            'timeline': timeline_data,
            'posts': posts_data,
            'settings': settings_dict,
        })


class PublicProjectDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, identifier):
        # Support slug or ID
        if identifier.isdigit():
            project = get_object_or_404(Project, id=int(identifier), is_published=True)
        else:
            project = get_object_or_404(Project, slug=identifier, is_published=True)

        other_projects = Project.objects.filter(is_published=True).exclude(id=project.id).order_by('sort_order')[:3]

        return Response({
            'project': ProjectSerializer(project, context={'request': request}).data,
            'other_projects': ProjectSerializer(other_projects, many=True, context={'request': request}).data
        })


class PublicContactView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactCreateSerializer(data=request.data)
        if serializer.is_valid():
            ip = ""
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR', '')

            msg = serializer.save(ip_address=ip)
            log_action(None, "استلام رسالة تواصل جديدة", "ContactMessage", msg.id, {
                "name": msg.sender_name,
                "email": msg.sender_email,
                "subject": msg.subject
            }, request)
            return Response({"success": True, "message": "تم استلام رسالتك بنجاح! سأتواصل معك قريباً."}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ════════════════════════════════════════
# ADMIN APIS & VIEWSETS
# ════════════════════════════════════════

class DashboardSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total_projects = Project.objects.count()
        total_services = Service.objects.count()
        total_skills = Skill.objects.count()
        total_messages = ContactMessage.objects.count()
        unread_messages = ContactMessage.objects.filter(is_read=False).count()
        total_testimonials = Testimonial.objects.count()
        total_posts = BlogPost.objects.count()

        latest_messages = ContactMessageSerializer(ContactMessage.objects.order_by('-created_at')[:5], many=True).data
        latest_projects = ProjectSerializer(Project.objects.order_by('-created_at')[:5], many=True).data
        latest_posts = BlogPostSerializer(BlogPost.objects.order_by('-published_at')[:5], many=True).data
        recent_audit_logs = AuditLogSerializer(AuditLog.objects.order_by('-created_at')[:10], many=True).data

        return Response({
            'metrics': {
                'total_projects': total_projects,
                'total_services': total_services,
                'total_skills': total_skills,
                'total_messages': total_messages,
                'unread_messages': unread_messages,
                'total_testimonials': total_testimonials,
                'total_posts': total_posts,
            },
            'latest_messages': latest_messages,
            'latest_projects': latest_projects,
            'latest_posts': latest_posts,
            'recent_audit_logs': recent_audit_logs,
        })


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(id=1)
        serializer = self.get_serializer(profile, context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(id=1)
        serializer = self.get_serializer(profile, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        log_action(request.user, "تحديث الملف الشخصي", "Profile", profile.id, request.data, request)
        return Response(serializer.data)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('sort_order', '-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "إضافة مشروع جديد", "Project", instance.id, {"title": instance.title}, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "تحديث بيانات مشروع", "Project", instance.id, {"title": instance.title}, self.request)

    def perform_destroy(self, instance):
        log_action(self.request.user, "حذف مشروع", "Project", instance.id, {"title": instance.title}, self.request)
        instance.delete()


class SkillCategoryViewSet(viewsets.ModelViewSet):
    queryset = SkillCategory.objects.all().order_by('sort_order', 'id')
    serializer_class = SkillCategorySerializer
    permission_classes = [permissions.IsAuthenticated]


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all().order_by('sort_order', 'id')
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all().order_by('sort_order', 'id')
    serializer_class = ServiceSerializer
    permission_classes = [permissions.IsAuthenticated]


class ExperienceViewSet(viewsets.ModelViewSet):
    queryset = Experience.objects.all().order_by('sort_order', '-id')
    serializer_class = ExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all().order_by('sort_order', '-created_at')
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.IsAuthenticated]


class StatisticViewSet(viewsets.ModelViewSet):
    queryset = Statistic.objects.all().order_by('sort_order', 'id')
    serializer_class = StatisticSerializer
    permission_classes = [permissions.IsAuthenticated]


class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all().order_by('-created_at')
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='toggle-read')
    def toggle_read(self, request, pk=None):
        msg = self.get_object()
        msg.is_read = not msg.is_read
        if msg.is_read and msg.status == 'new':
            msg.status = 'read'
        msg.save()
        return Response({"is_read": msg.is_read, "status": msg.status})

    @action(detail=True, methods=['post'], url_path='archive')
    def archive_message(self, request, pk=None):
        msg = self.get_object()
        msg.status = 'archived'
        msg.save()
        return Response({"status": msg.status})


class SiteSettingViewSet(viewsets.ModelViewSet):
    queryset = SiteSetting.objects.all().order_by('group_name', 'key')
    serializer_class = SiteSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='bulk-update')
    def bulk_update(self, request):
        data = request.data
        items_to_save = []
        if isinstance(data, dict):
            if 'settings' in data and isinstance(data['settings'], list):
                items_to_save = data['settings']
            else:
                for k, v in data.items():
                    items_to_save.append({'key': k, 'value': v})
        elif isinstance(data, list):
            items_to_save = data
        else:
            return Response({"error": "البيانات المرسلة غير صحيحة."}, status=status.HTTP_400_BAD_REQUEST)

        for item in items_to_save:
            if not isinstance(item, dict) or 'key' not in item:
                continue
            k = str(item['key'])
            val = item.get('value', '')
            grp = item.get('group_name', 'general')
            if isinstance(val, bool):
                val_str = 'true' if val else 'false'
                v_type = 'boolean'
            elif isinstance(val, int):
                val_str = str(val)
                v_type = 'integer'
            else:
                val_str = str(val) if val is not None else ''
                v_type = 'string'
            SiteSetting.objects.update_or_create(
                key=k,
                defaults={'value': val_str, 'setting_type': v_type, 'group_name': grp}
            )
        log_action(request.user, "تحديث إعدادات الموقع العامة", "SiteSetting", "", data, request)
        return Response({"message": "تم حفظ الإعدادات بنجاح."})


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsSuperUserOnly]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.all().order_by('-created_at')
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]


class MediaUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.svg', '.gif', '.pdf'}
    FORBIDDEN_EXTENSIONS = {'.exe', '.py', '.sh', '.bat', '.cmd', '.php', '.html', '.htm', '.js', '.phtml', '.vbs', '.jsp', '.asp', '.aspx', '.cgi', '.pl', '.jar'}
    ALLOWED_IMAGE_MIMES = {'image/jpeg', 'image/png', 'image/webp', 'image/svg+xml', 'image/gif'}
    ALLOWED_DOC_MIMES = {'application/pdf'}

    def get(self, request):
        files = MediaFile.objects.all().order_by('-uploaded_at')
        serializer = MediaFileSerializer(files, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        import os
        import html
        from django.conf import settings
        from django.utils.text import get_valid_filename
        from PIL import Image

        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({"error": "لم يتم إرسال أي ملف."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. File size validation (Max 10 MB or configured limit)
        max_size_mb = getattr(settings, 'MAX_UPLOAD_SIZE_MB', 10)
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_obj.size > max_size_bytes:
            return Response(
                {"error": f"حجم الملف يتجاوز الحد الأقصى المسموح به ({max_size_mb} ميجابايت)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. File extension validation
        original_name = get_valid_filename(file_obj.name)
        _, ext = os.path.splitext(original_name.lower())

        if ext in self.FORBIDDEN_EXTENSIONS or ext not in self.ALLOWED_EXTENSIONS:
            return Response(
                {"error": f"نوع الملف ({ext}) غير مسموح به. الصيغ المسموحة: {', '.join(sorted(self.ALLOWED_EXTENSIONS))}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. MIME-Type validation
        content_type = getattr(file_obj, 'content_type', '').lower()
        if ext in {'.jpg', '.jpeg', '.png', '.webp', '.gif'} and content_type not in self.ALLOWED_IMAGE_MIMES:
            return Response({"error": "نوع محتوى الملف غير متطابق مع صيغة الصورة."}, status=status.HTTP_400_BAD_REQUEST)

        if ext == '.pdf' and content_type not in self.ALLOWED_DOC_MIMES and content_type != 'application/octet-stream':
            return Response({"error": "نوع محتوى الملف غير متطابق مع ملف PDF صالح."}, status=status.HTTP_400_BAD_REQUEST)

        # 4. Image integrity check using Pillow (for non-SVG images)
        if ext in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
            try:
                img = Image.open(file_obj)
                img.verify()
                file_obj.seek(0)
            except Exception:
                return Response({"error": "الملف المرفوع تالف أو ليس صورة صالحة."}, status=status.HTTP_400_BAD_REQUEST)

        # 5. Sanitize Title and metadata
        title = request.data.get('title') or original_name
        title = html.escape(title.strip())[:200]
        file_type = 'image' if ext != '.pdf' else 'document'
        
        media_file = MediaFile.objects.create(
            title=title,
            file=file_obj,
            file_type=file_type,
            file_size=file_obj.size
        )
        serializer = MediaFileSerializer(media_file, context={'request': request})
        log_action(request.user, "رفع ملف وسائط جديد", "MediaFile", media_file.id, {"title": title}, request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        file_id = request.data.get('id') if isinstance(request.data, dict) else None
        if not file_id:
            file_id = request.query_params.get('id')
        if not file_id:
            return Response({"error": "معرف الملف مطلوب."}, status=status.HTTP_400_BAD_REQUEST)
        media_file = get_object_or_404(MediaFile, id=file_id)
        if media_file.file:
            media_file.file.delete(save=False)
        media_file.delete()
        log_action(request.user, "حذف ملف وسائط", "MediaFile", file_id, {}, request)
        return Response({"message": "تم حذف الملف بنجاح."})


# ════════════════════════════════════════
# PORTFOLIO DATA TEMPLATE APIS
# ════════════════════════════════════════

class DataTemplateExportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        entities = request.query_params.get('entities', 'all')
        with_examples = request.query_params.get('examples', 'false').lower() in ['true', '1', 'yes']
        
        template_data = export_portfolio_template(
            entities=entities,
            with_examples=with_examples,
            user=request.user
        )
        
        log_action(
            request.user,
            f"تصدير قالب بيانات الموقع ({'مع أمثلة' if with_examples else 'بيانات حية'})",
            "DataTemplate",
            "",
            {"entities": entities, "with_examples": with_examples},
            request
        )

        response = Response(template_data, status=status.HTTP_200_OK)
        # Suggest filename for browser download if downloaded directly
        today_str = timezone.now().strftime('%Y-%m-%d')
        filename = f"portfolio-template-{'examples-' if with_examples else ''}{today_str}.json"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class DataTemplateValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        payload = None
        import_mode = request.data.get('import_mode', 'UPSERT')

        # Check if file was uploaded
        file_obj = request.FILES.get('file')
        if file_obj:
            if file_obj.size > 5 * 1024 * 1024:
                return Response({
                    "valid": False,
                    "errors": [{"entity": "file", "message": "حجم الملف تجاوز الحد الأقصى المسموح به (5 ميغابايت)."}]
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                content = file_obj.read().decode('utf-8')
                payload = json.loads(content)
            except Exception as e:
                return Response({
                    "valid": False,
                    "errors": [{"entity": "json", "message": f"الملف المرفوع لا يحتوي على JSON صالح: {str(e)}"}]
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            payload = request.data.get('payload') or request.data

        if not payload:
            return Response({
                "valid": False,
                "errors": [{"entity": "payload", "message": "لم يتم إرسال أي ملف أو كائن بيانات للفحص."}]
            }, status=status.HTTP_400_BAD_REQUEST)

        validator = TemplateValidatorService(payload, import_mode=import_mode)
        report = validator.validate()
        return Response(report, status=status.HTTP_200_OK if report['valid'] else status.HTTP_200_OK)


class DataTemplateImportView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        payload = None
        filename = "template.json"
        import_mode = request.data.get('import_mode', 'UPSERT')
        replace_confirmed = str(request.data.get('replace_confirmed', 'false')).lower() in ['true', '1', 'yes']

        # Check if file was uploaded
        file_obj = request.FILES.get('file')
        if file_obj:
            filename = getattr(file_obj, 'name', 'template.json')
            if file_obj.size > 5 * 1024 * 1024:
                return Response({
                    "success": False,
                    "status": "FAILED",
                    "message": "حجم الملف تجاوز الحد الأقصى المسموح به (5 ميغابايت)."
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                content = file_obj.read().decode('utf-8')
                payload = json.loads(content)
            except Exception as e:
                return Response({
                    "success": False,
                    "status": "FAILED",
                    "message": f"الملف المرفوع لا يحتوي على JSON صالح: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            payload = request.data.get('payload') or request.data
            filename = request.data.get('filename', 'template.json')

        if not payload:
            return Response({
                "success": False,
                "status": "FAILED",
                "message": "لم يتم إرسال أي ملف أو بيانات للاستيراد."
            }, status=status.HTTP_400_BAD_REQUEST)

        importer = TemplateImportService(
            payload=payload,
            import_mode=import_mode,
            filename=filename,
            user=request.user,
            request=request,
            replace_confirmed=replace_confirmed
        )

        result = importer.execute()
        http_status = status.HTTP_200_OK if result['success'] else status.HTTP_400_BAD_REQUEST
        return Response(result, status=http_status)


class DataImportHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DataImportHistorySerializer
    queryset = DataImportHistory.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        log_action(request.user, "حذف سجل استيراد", "DataImportHistory", instance.id, {"filename": instance.filename}, request)
        instance.delete()
        return Response({"message": "تم حذف سجل العملية بنجاح."}, status=status.HTTP_200_OK)


class BlogPostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    serializer_class = BlogPostSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        qs = BlogPost.objects.all()
        # If not authenticated, only show published posts
        if not self.request.user or not self.request.user.is_authenticated:
            qs = qs.filter(is_published=True)

        category = self.request.query_params.get('category')
        if category and category != 'الكل':
            qs = qs.filter(category=category)

        tag = self.request.query_params.get('tag')
        if tag:
            qs = qs.filter(tags__contains=[tag])

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search) |
                Q(category__icontains=search)
            )

        return qs

    def perform_create(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "إنشاء مقال جديد", "BlogPost", instance.id, {"title": instance.title, "category": instance.category}, self.request)

    def perform_update(self, serializer):
        instance = serializer.save()
        log_action(self.request.user, "تعديل مقال", "BlogPost", instance.id, {"title": instance.title}, self.request)

    def perform_destroy(self, instance):
        log_action(self.request.user, "حذف مقال", "BlogPost", instance.id, {"title": instance.title}, self.request)
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def increment_view(self, request, pk=None):
        from django.db.models import F
        post = self.get_object()
        BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
        post.refresh_from_db()
        return Response({"views_count": post.views_count}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def toggle_like(self, request, pk=None):
        from django.db.models import F
        post = self.get_object()
        BlogPost.objects.filter(pk=post.pk).update(likes_count=F('likes_count') + 1)
        post.refresh_from_db()
        return Response({"likes_count": post.likes_count}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny], url_path='by-slug/(?P<slug>[^/.]+)')
    def by_slug(self, request, slug=None):
        import urllib.parse
        decoded_slug = urllib.parse.unquote(slug)
        try:
            post = BlogPost.objects.get(slug=decoded_slug)
            if not post.is_published and (not request.user or not request.user.is_authenticated):
                return Response({"detail": "المقال غير متاح."}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(post)
            return Response(serializer.data)
        except BlogPost.DoesNotExist:
            # Fallback by id if numeric
            if decoded_slug.isdigit():
                try:
                    post = BlogPost.objects.get(pk=int(decoded_slug))
                    serializer = self.get_serializer(post)
                    return Response(serializer.data)
                except BlogPost.DoesNotExist:
                    pass
            return Response({"detail": "المقال غير موجود."}, status=status.HTTP_404_NOT_FOUND)

