from django.core.management.base import BaseCommand
from core.models import QuizQuestion


QUESTIONS = [
    {
        "question_text": "Which HTTP method is typically used to update an existing resource?",
        "category": "WEB",
        "option_a": "GET", "option_b": "PUT", "option_c": "DELETE", "option_d": "CONNECT",
        "correct_option": "B",
    },
    {
        "question_text": "In Python, which keyword is used to define a function?",
        "category": "PROGRAMMING",
        "option_a": "func", "option_b": "def", "option_c": "function", "option_d": "lambda",
        "correct_option": "B",
    },
    {
        "question_text": "Which SQL clause is used to filter rows after grouping?",
        "category": "DATABASE",
        "option_a": "WHERE", "option_b": "HAVING", "option_c": "GROUP BY", "option_d": "ORDER BY",
        "correct_option": "B",
    },
    {
        "question_text": "Which CSS property is used to change text color?",
        "category": "WEB",
        "option_a": "font-color", "option_b": "text-style", "option_c": "color", "option_d": "background-color",
        "correct_option": "C",
    },
    {
        "question_text": "Which Django command applies database migrations?",
        "category": "TOOLS",
        "option_a": "python manage.py migrate",
        "option_b": "python manage.py runserver",
        "option_c": "python manage.py collectstatic",
        "option_d": "python manage.py startapp",
        "correct_option": "A",
    },
    {
        "question_text": "Which Git command is used to stage changes for commit?",
        "category": "TOOLS",
        "option_a": "git commit", "option_b": "git push", "option_c": "git add", "option_d": "git clone",
        "correct_option": "C",
    },
    {
        "question_text": "What does CGPA stand for in an academic context?",
        "category": "GENERAL",
        "option_a": "Cumulative Grade Point Average",
        "option_b": "Career Grade Point Analysis",
        "option_c": "Combined Grade Percentage Average",
        "option_d": "Class Grade Point Assessment",
        "correct_option": "A",
    },
    {
        "question_text": "Which data structure uses FIFO (First In First Out) order?",
        "category": "PROGRAMMING",
        "option_a": "Stack", "option_b": "Queue", "option_c": "Tree", "option_d": "Graph",
        "correct_option": "B",
    },
    {
        "question_text": "Which of these is a NoSQL database?",
        "category": "DATABASE",
        "option_a": "MySQL", "option_b": "PostgreSQL", "option_c": "MongoDB", "option_d": "SQLite",
        "correct_option": "C",
    },
    {
        "question_text": "In REST APIs, which status code indicates 'Not Found'?",
        "category": "WEB",
        "option_a": "200", "option_b": "301", "option_c": "404", "option_d": "500",
        "correct_option": "C",
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample quiz questions."

    def handle(self, *args, **options):
        created_count = 0
        for q in QUESTIONS:
            obj, created = QuizQuestion.objects.get_or_create(
                question_text=q["question_text"],
                defaults=q,
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(
            f"Seeding complete. {created_count} new questions added "
            f"({QuizQuestion.objects.count()} total in database)."
        ))
