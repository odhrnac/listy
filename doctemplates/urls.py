from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_edit, name='template_create'),
    path('templates/<int:template_id>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:template_id>/delete/', views.template_delete, name='template_delete'),
]