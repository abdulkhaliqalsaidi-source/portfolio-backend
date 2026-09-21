from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import (
    Profile, SkillCategory, Skill, Service, Project,
    ProjectImage, Experience, Testimonial, Statistic,
    ContactMessage, SiteSetting, AuditLog, MediaFile,
    DataImportHistory, BlogPost
)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        token['is_superuser'] = user.is_superuser
        token['is_staff'] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_superuser': self.user.is_superuser,
            'is_staff': self.user.is_staff,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'date_joined', 'password']
        read_only_fields = ['date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

    def to_internal_value(self, data):
        if isinstance(data, dict):
            mutable_data = data.copy()
            # Convert None/null string and URL fields into empty string so DB CharFields never fail validation
            string_fields = [
                'full_name', 'title', 'tagline', 'bio', 'email', 'phone', 'whatsapp',
                'github', 'linkedin', 'twitter', 'instagram', 'behance', 'dribbble',
                'youtube', 'website', 'location', 'avatar', 'resume'
            ]
            for field in string_fields:
                if field in mutable_data and mutable_data[field] is None:
                    mutable_data[field] = ''
            return super().to_internal_value(mutable_data)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        avatar_val = str(instance.avatar or '').strip()
        if avatar_val:
            if avatar_val.startswith('http://') or avatar_val.startswith('https://'):
                data['avatar'] = avatar_val
            elif avatar_val.startswith('/media/') or avatar_val.startswith('media/'):
                clean_path = '/' + avatar_val.lstrip('/')
                data['avatar'] = request.build_absolute_uri(clean_path) if request else f"http://127.0.0.1:8000{clean_path}"
            else:
                data['avatar'] = avatar_val
        else:
            data['avatar'] = ''
            
        resume_val = str(instance.resume or '').strip()
        if resume_val:
            if resume_val.startswith('http://') or resume_val.startswith('https://'):
                data['resume'] = resume_val
            elif resume_val.startswith('/media/') or resume_val.startswith('media/'):
                clean_path = '/' + resume_val.lstrip('/')
                data['resume'] = request.build_absolute_uri(clean_path) if request else f"http://127.0.0.1:8000{clean_path}"
            else:
                data['resume'] = resume_val
        else:
            data['resume'] = ''
            
        return data


class SkillSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'category', 'category_name', 'name', 'icon', 'color', 'proficiency_percentage', 'sort_order', 'is_visible']


class SkillCategorySerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = SkillCategory
        fields = ['id', 'name', 'icon', 'sort_order', 'skills']


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    gallery = ProjectImageSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        img_val = str(instance.image or '')
        if img_val.startswith('/media/'):
            request = self.context.get('request')
            data['image'] = request.build_absolute_uri(img_val) if request else f"http://127.0.0.1:8000{img_val}"
        return data


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'


class StatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statistic
        fields = '__all__'


class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['created_at', 'ip_address']


class ContactCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['sender_name', 'sender_email', 'sender_phone', 'subject', 'message']

    def validate_sender_email(self, value):
        val = (value or '').strip()
        if not val or '@' not in val or '.' not in val.split('@')[-1]:
            raise serializers.ValidationError("يرجى إدخال بريد إلكتروني صحيح.")
        return val.lower()

    def validate_sender_name(self, value):
        import html
        val = html.escape((value or '').strip())
        if len(val) < 2:
            raise serializers.ValidationError("يرجى إدخال اسم صحيح لا يقل عن حرفين.")
        if len(val) > 120:
            raise serializers.ValidationError("الاسم طويل جداً.")
        return val

    def validate_subject(self, value):
        import html
        val = html.escape((value or '').strip())
        if not val or len(val) < 2:
            raise serializers.ValidationError("يرجى إدخال موضوع الرسالة.")
        return val

    def validate_message(self, value):
        import html
        val = html.escape((value or '').strip())
        if not val or len(val) < 5:
            raise serializers.ValidationError("نص الرسالة قصير جداً، يرجى كتابة تفاصيل أكثر.")
        if len(val) > 4000:
            raise serializers.ValidationError("نص الرسالة تجاوز الحد الأقصى المسموح (4000 حرف).")
        return val


class SiteSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSetting
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'username', 'action', 'entity_type', 'entity_id', 'details', 'ip_address', 'created_at']


class MediaFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = MediaFile
        fields = ['id', 'title', 'file', 'file_url', 'file_type', 'file_size', 'uploaded_at']

    def get_file_url(self, obj):
        if obj.file and hasattr(obj.file, 'url'):
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.file.url)
            return f"http://127.0.0.1:8000{obj.file.url}"
        return ""

    def get_file(self, obj):
        return self.get_file_url(obj)


class DataImportHistorySerializer(serializers.ModelSerializer):
    imported_by_username = serializers.CharField(source='imported_by.username', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    import_mode_display = serializers.CharField(source='get_import_mode_display', read_only=True)

    class Meta:
        model = DataImportHistory
        fields = [
            'id', 'filename', 'version', 'import_mode', 'import_mode_display',
            'status', 'status_display', 'summary', 'created_count', 'updated_count',
            'skipped_count', 'error_count', 'warning_count', 'errors_log',
            'warnings_log', 'imported_by', 'imported_by_username', 'duration_ms', 'created_at'
        ]


class BlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'
