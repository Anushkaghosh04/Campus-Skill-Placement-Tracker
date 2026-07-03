from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


BRANCH_CHOICES = [
    ('CSE', 'Computer Science Engineering'),
    ('IT', 'Information Technology'),
    ('ECE', 'Electronics & Communication'),
    ('EEE', 'Electrical & Electronics'),
    ('MECH', 'Mechanical Engineering'),
    ('CIVIL', 'Civil Engineering'),
    ('OTHER', 'Other'),
]

SKILL_CATEGORY_CHOICES = [
    ('PROGRAMMING', 'Programming'),
    ('WEB', 'Web Development'),
    ('DATABASE', 'Database'),
    ('TOOLS', 'Tools'),
]

PROFICIENCY_CHOICES = [
    ('BEGINNER', 'Beginner'),
    ('INTERMEDIATE', 'Intermediate'),
    ('ADVANCED', 'Advanced'),
]

TARGET_ROLE_CHOICES = [
    ('FRONTEND', 'Frontend Developer'),
    ('BACKEND', 'Backend Developer'),
    ('FULLSTACK', 'Full Stack Developer'),
    ('DATA_ANALYST', 'Data Analyst'),
]


class Profile(models.Model):
    """Extended student profile, linked one-to-one with Django's auth User."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES, default='CSE')
    semester = models.PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    cgpa = models.DecimalField(
        max_digits=4, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    projects_count = models.PositiveIntegerField(default=0, help_text="Number of projects completed")
    target_role = models.CharField(max_length=20, choices=TARGET_ROLE_CHOICES, blank=True, null=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.user.username

    @property
    def display_name(self):
        return self.name or self.user.get_full_name() or self.user.username


class Skill(models.Model):
    """A single skill entry belonging to a student."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=SKILL_CATEGORY_CHOICES, default='PROGRAMMING')
    proficiency = models.CharField(max_length=15, choices=PROFICIENCY_CHOICES, default='BEGINNER')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']
        unique_together = ('user', 'name')

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class QuizQuestion(models.Model):
    """MCQ question stored in DB; admin manageable."""
    CATEGORY_CHOICES = SKILL_CATEGORY_CHOICES + [('GENERAL', 'General Aptitude')]

    question_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='GENERAL')
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'Option A'), ('B', 'Option B'), ('C', 'Option C'), ('D', 'Option D')]
    )

    def __str__(self):
        return self.question_text[:60]

    def is_correct(self, selected_option):
        return selected_option == self.correct_option


class QuizResult(models.Model):
    """Stores a student's quiz attempt result."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_results')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    taken_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-taken_at']

    def __str__(self):
        return f"{self.user.username} - {self.percentage}% ({self.taken_at:%Y-%m-%d})"


class Resume(models.Model):
    """Uploaded resume file plus basic extracted-text analysis."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume')
    file = models.FileField(upload_to='resumes/')
    extracted_text = models.TextField(blank=True)
    matched_keywords = models.TextField(blank=True, help_text="Comma-separated matched skill keywords")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume of {self.user.username}"

    def matched_keywords_list(self):
        return [k.strip() for k in self.matched_keywords.split(',') if k.strip()]


class ActivityLog(models.Model):
    """Simple recent-activity feed for the dashboard."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message}"
