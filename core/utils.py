"""
Core "intelligence" of the Placement Readiness Tracker:
- Readiness score engine
- Skill gap analyzer
- Career role recommender
- Resume keyword extractor
"""

from django.db.models import Avg


# ---------------------------------------------------------------------------
# Role -> required skill map (used for gap analysis + recommendations)
# Keys match Profile.TARGET_ROLE_CHOICES values.
# ---------------------------------------------------------------------------
ROLE_REQUIRED_SKILLS = {
    'FRONTEND': ['HTML', 'CSS', 'JavaScript', 'React', 'Bootstrap', 'Git'],
    'BACKEND': ['Python', 'Django', 'SQL', 'REST API', 'Git', 'Linux'],
    'FULLSTACK': ['HTML', 'CSS', 'JavaScript', 'Python', 'Django', 'SQL', 'Git', 'React'],
    'DATA_ANALYST': ['Python', 'SQL', 'Excel', 'Pandas', 'Power BI', 'Statistics'],
}

ROLE_LABELS = {
    'FRONTEND': 'Frontend Developer',
    'BACKEND': 'Backend Developer',
    'FULLSTACK': 'Full Stack Developer',
    'DATA_ANALYST': 'Data Analyst',
}

# Keywords resumes are scanned for (basic, case-insensitive)
RESUME_KEYWORDS = [
    'Python', 'Django', 'Flask', 'HTML', 'CSS', 'JavaScript', 'React', 'Angular',
    'Vue', 'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Git', 'GitHub', 'REST API',
    'Bootstrap', 'jQuery', 'Java', 'C++', 'C', 'Linux', 'Docker', 'AWS',
    'Excel', 'Pandas', 'NumPy', 'Power BI', 'Tableau', 'Statistics',
    'Machine Learning', 'Data Analysis', 'TypeScript', 'Node.js',
]


def calculate_readiness_score(user):
    """
    Placement readiness score out of 100:
      - Skills count      -> 40%
      - Projects count    -> 30%
      - Resume uploaded   -> 20%
      - Quiz score (avg)  -> 10%
    Returns dict with breakdown + total.
    """
    skills_count = user.skills.count()
    # Cap contribution: 8+ skills = full 40%
    skills_score = min(skills_count / 8, 1) * 40

    profile = getattr(user, 'profile', None)
    projects_count = profile.projects_count if profile else 0
    # Cap contribution: 5+ projects = full 30%
    projects_score = min(projects_count / 5, 1) * 30

    has_resume = hasattr(user, 'resume') and bool(user.resume.file)
    resume_score = 20 if has_resume else 0

    avg_quiz = user.quiz_results.aggregate(avg=Avg('percentage'))['avg'] or 0
    quiz_score = (float(avg_quiz) / 100) * 10

    total = round(skills_score + projects_score + resume_score + quiz_score, 1)
    total = min(total, 100)

    return {
        'skills_score': round(skills_score, 1),
        'projects_score': round(projects_score, 1),
        'resume_score': resume_score,
        'quiz_score': round(quiz_score, 1),
        'total': total,
        'skills_count': skills_count,
        'projects_count': projects_count,
        'has_resume': has_resume,
        'avg_quiz_percentage': round(float(avg_quiz), 1),
    }


def get_readiness_badge(score):
    """Return badge label + Bootstrap color class based on score."""
    if score >= 75:
        return 'Job Ready', 'success'
    elif score >= 40:
        return 'Intermediate', 'warning'
    else:
        return 'Beginner', 'danger'


def analyze_skill_gap(user, target_role):
    """
    Compare the student's current skills against the required skill set
    for `target_role`. Matching is case-insensitive substring-aware.
    Returns dict: required, possessed, missing, match_percentage.
    """
    required = ROLE_REQUIRED_SKILLS.get(target_role, [])
    user_skills = [s.name.strip().lower() for s in user.skills.all()]

    possessed = []
    missing = []
    for req_skill in required:
        req_lower = req_skill.lower()
        found = any(req_lower == us for us in user_skills)
        if found:
            possessed.append(req_skill)
        else:
            missing.append(req_skill)

    match_percentage = round((len(possessed) / len(required)) * 100, 1) if required else 0

    return {
        'role_label': ROLE_LABELS.get(target_role, target_role),
        'required': required,
        'possessed': possessed,
        'missing': missing,
        'match_percentage': match_percentage,
    }


def recommend_career(user):
    """
    Rule-based recommender:
      - HTML/CSS/JS present        -> Frontend Developer
      - Python/Django/SQL present  -> Backend Developer
      - Both groups present        -> Full Stack Developer
      - Otherwise                  -> best partial match among all roles
    """
    user_skills = set(s.name.strip().lower() for s in user.skills.all())

    frontend_core = {'html', 'css', 'javascript'}
    backend_core = {'python', 'django', 'sql'}

    has_frontend = len(user_skills & frontend_core) >= 2
    has_backend = len(user_skills & backend_core) >= 2

    if has_frontend and has_backend:
        role_key = 'FULLSTACK'
        reason = "You have both frontend (HTML/CSS/JS) and backend (Python/Django/SQL) skills."
    elif has_backend:
        role_key = 'BACKEND'
        reason = "You have strong Python/Django/SQL skills suited for backend roles."
    elif has_frontend:
        role_key = 'FRONTEND'
        reason = "You have strong HTML/CSS/JavaScript skills suited for frontend roles."
    else:
        # fall back to best matching role by overlap
        best_role, best_score = None, -1
        for role_key_candidate, skills in ROLE_REQUIRED_SKILLS.items():
            overlap = len(user_skills & set(s.lower() for s in skills))
            if overlap > best_score:
                best_score = overlap
                best_role = role_key_candidate
        role_key = best_role or 'FULLSTACK'
        reason = "Based on your current skill set, this role has the closest match. Add more skills for a stronger recommendation."

    return {
        'role_key': role_key,
        'role_label': ROLE_LABELS.get(role_key, role_key),
        'reason': reason,
    }


def extract_resume_keywords(text):
    """Scan extracted resume text for known keywords (case-insensitive, whole-word/phrase match)."""
    import re
    text_lower = text.lower()
    matched = []
    for kw in RESUME_KEYWORDS:
        pattern = r'(?<![a-z0-9])' + re.escape(kw.lower()) + r'(?![a-z0-9])'
        if re.search(pattern, text_lower):
            matched.append(kw)
    return matched


def suggest_missing_resume_skills(user, matched_keywords):
    """Suggest skills in the user's target role that are absent from resume text."""
    profile = getattr(user, 'profile', None)
    target_role = profile.target_role if profile else None
    if not target_role:
        return []
    required = ROLE_REQUIRED_SKILLS.get(target_role, [])
    matched_lower = [m.lower() for m in matched_keywords]
    return [r for r in required if r.lower() not in matched_lower]
