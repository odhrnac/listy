from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='generator/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload/', views.upload_view, name='upload'),
    path('history/', views.history_view, name='history'),
    path('history/<int:job_id>/', views.job_detail_view, name='job_detail'),
    path('download/zip/<int:job_id>/', views.download_zip, name='download_zip'),
    path('download/<int:pdf_id>/', views.download_pdf, name='download_pdf'),
]