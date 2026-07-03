from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('skills/', views.skills_view, name='skills'),
    path('skills/<int:pk>/edit/', views.skill_edit_view, name='skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete_view, name='skill_delete'),
    path('skill-gap/', views.skill_gap_view, name='skill_gap'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('quiz/result/', views.quiz_result_view, name='quiz_result'),
    path('resume-upload/', views.resume_upload_view, name='resume_upload'),
]