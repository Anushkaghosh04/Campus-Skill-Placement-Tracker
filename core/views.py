from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count

from .forms import RegisterForm, ProfileForm, SkillForm, ResumeUploadForm, TargetRoleForm, StyledAuthenticationForm
from .models import Profile, Skill, QuizQuestion, QuizResult, Resume, ActivityLog
from .utils import (
    calculate_readiness_score, get_readiness_badge, analyze_skill_gap,
    recommend_career, extract_resume_keywords, suggest_missing_resume_skills,
    ROLE_REQUIRED_SKILLS,
)


def log_activity(user, message):
    ActivityLog.objects.create(user=user, message=message)


# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------

def home_view(request):
    return render(request, 'core/home.html', {'landing_page': True})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['name']
            user.save()
            Profile.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
            )
            log_activity(user, "Account created")
            login(request, user)
            messages.success(request, f"Welcome aboard, {user.first_name or user.username}! Your account is ready.")
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = StyledAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = StyledAuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------

@login_required
def dashboard_view(request):
    user = request.user
    Profile.objects.get_or_create(user=user)

    score_data = calculate_readiness_score(user)
    badge_label, badge_color = get_readiness_badge(score_data['total'])
    recommendation = recommend_career(user)

    gap_data = None
    profile = user.profile
    if profile.target_role:
        gap_data = analyze_skill_gap(user, profile.target_role)

    skills_by_category = (
        user.skills.values('category').annotate(count=Count('id')).order_by('category')
    )

    recent_activities = user.activities.all()[:8]
    latest_quiz = user.quiz_results.first()

    context = {
        'profile': profile,
        'score_data': score_data,
        'badge_label': badge_label,
        'badge_color': badge_color,
        'recommendation': recommendation,
        'gap_data': gap_data,
        'skills_by_category': skills_by_category,
        'total_skills': user.skills.count(),
        'recent_activities': recent_activities,
        'latest_quiz': latest_quiz,
        'has_resume': hasattr(user, 'resume'),
    }
    return render(request, 'core/dashboard.html', context)


# ---------------------------------------------------------------------------
# PROFILE
# ---------------------------------------------------------------------------

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            log_activity(request.user, "Updated profile information")
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'core/profile.html', {'form': form, 'profile': profile})


# ---------------------------------------------------------------------------
# SKILLS CRUD
# ---------------------------------------------------------------------------

@login_required
def skills_view(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            try:
                skill.save()
                log_activity(request.user, f"Added skill: {skill.name}")
                messages.success(request, f"Skill '{skill.name}' added.")
            except Exception:
                messages.error(request, f"You already have a skill named '{skill.name}'.")
            return redirect('skills')
    else:
        form = SkillForm()

    skills = request.user.skills.all()
    return render(request, 'core/skills.html', {'form': form, 'skills': skills})


@login_required
def skill_edit_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            log_activity(request.user, f"Updated skill: {skill.name}")
            messages.success(request, "Skill updated.")
            return redirect('skills')
    else:
        form = SkillForm(instance=skill)

    return render(request, 'core/skill_edit.html', {'form': form, 'skill': skill})


@login_required
def skill_delete_view(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    if request.method == 'POST':
        name = skill.name
        skill.delete()
        log_activity(request.user, f"Removed skill: {name}")
        messages.success(request, f"Skill '{name}' removed.")
        return redirect('skills')
    return render(request, 'core/skill_confirm_delete.html', {'skill': skill})


# ---------------------------------------------------------------------------
# SKILL GAP ANALYZER
# ---------------------------------------------------------------------------

@login_required
def skill_gap_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = TargetRoleForm(request.POST)
        if form.is_valid():
            profile.target_role = form.cleaned_data['target_role']
            profile.save()
            log_activity(request.user, f"Set target role: {profile.get_target_role_display()}")
            return redirect('skill_gap')
    else:
        initial = {'target_role': profile.target_role} if profile.target_role else {}
        form = TargetRoleForm(initial=initial)

    gap_data = None
    if profile.target_role:
        gap_data = analyze_skill_gap(request.user, profile.target_role)

    return render(request, 'core/skill_gap.html', {
        'form': form, 'gap_data': gap_data, 'profile': profile,
        'all_roles': ROLE_REQUIRED_SKILLS,
    })


# ---------------------------------------------------------------------------
# QUIZ MODULE
# ---------------------------------------------------------------------------

@login_required
def quiz_view(request):
    questions = list(QuizQuestion.objects.all())

    if request.method == 'POST':
        if not questions:
            messages.warning(request, "No quiz questions available yet.")
            return redirect('dashboard')

        score = 0
        for q in questions:
            selected = request.POST.get(f'question_{q.id}')
            if selected and q.is_correct(selected):
                score += 1

        total = len(questions)
        percentage = round((score / total) * 100, 2) if total else 0

        QuizResult.objects.create(
            user=request.user, score=score, total_questions=total, percentage=percentage
        )
        log_activity(request.user, f"Completed quiz: {score}/{total} ({percentage}%)")
        messages.success(request, f"Quiz submitted! You scored {score}/{total} ({percentage}%).")
        return redirect('quiz_result')

    return render(request, 'core/quiz.html', {'questions': questions})


@login_required
def quiz_result_view(request):
    results = request.user.quiz_results.all()
    latest = results.first()
    return render(request, 'core/quiz_result.html', {'results': results, 'latest': latest})


# ---------------------------------------------------------------------------
# RESUME UPLOAD & ANALYZER
# ---------------------------------------------------------------------------

@login_required
def resume_upload_view(request):
    existing_resume = getattr(request.user, 'resume', None)

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            if existing_resume:
                existing_resume.delete()

            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()

            extracted_text = _extract_pdf_text(resume.file.path)
            resume.extracted_text = extracted_text
            matched = extract_resume_keywords(extracted_text)
            resume.matched_keywords = ', '.join(matched)
            resume.save()

            log_activity(request.user, "Uploaded resume")
            messages.success(request, "Resume uploaded and analyzed successfully.")
            return redirect('resume_upload')
    else:
        form = ResumeUploadForm()

    resume = getattr(request.user, 'resume', None)
    missing_skills = []
    if resume:
        missing_skills = suggest_missing_resume_skills(request.user, resume.matched_keywords_list())

    return render(request, 'core/resume_upload.html', {
        'form': form, 'resume': resume, 'missing_skills': missing_skills,
    })


def _extract_pdf_text(filepath):
    """Best-effort text extraction from an uploaded PDF resume."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(filepath)
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text.strip()
    except Exception:
        return ""