from django.contrib import admin
from django.db.models import Avg
from .models import Profile, Skill, QuizQuestion, QuizResult, Resume, ActivityLog


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'branch', 'semester', 'cgpa', 'projects_count', 'target_role')
    list_filter = ('branch', 'semester', 'target_role')
    search_fields = ('name', 'user__username', 'email')


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category', 'proficiency', 'created_at')
    list_filter = ('category', 'proficiency')
    search_fields = ('name', 'user__username')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text_short', 'category', 'correct_option')
    list_filter = ('category',)
    search_fields = ('question_text',)

    def question_text_short(self, obj):
        return obj.question_text[:70]
    question_text_short.short_description = 'Question'


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'total_questions', 'percentage', 'taken_at')
    list_filter = ('taken_at',)
    search_fields = ('user__username',)

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        avg = QuizResult.objects.aggregate(avg=Avg('percentage'))['avg']
        extra_context['average_percentage'] = round(avg, 2) if avg else 0
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at')
    search_fields = ('user__username',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'message')
