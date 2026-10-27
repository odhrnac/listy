from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('templates/', views.template_list, name='template_list'),
    path('templates/create/', views.template_edit, name='template_create'),
    path('templates/<int:template_id>/edit/', views.template_edit, name='template_edit'),
    path('templates/<int:template_id>/delete/', views.template_delete, name='template_delete'),

    path('images/', views.image_asset_list, name='image_asset_list'),
    path('images/<int:image_id>/delete/', views.image_asset_delete, name='image_asset_delete'),

    path('templates/<int:template_id>/images/', views.template_image_list, name='template_image_list'),
    path('templates/<int:template_id>/images/<int:image_id>/edit/', views.template_image_edit, name='template_image_edit'),
    path('templates/<int:template_id>/images/<int:image_id>/delete/', views.template_image_delete, name='template_image_delete'),

    path('templates/<int:template_id>/fields/', views.template_field_list, name='template_field_list'),
    path('templates/<int:template_id>/fields/<int:field_id>/edit/', views.template_field_edit, name='template_field_edit'),
    path('templates/<int:template_id>/fields/<int:field_id>/delete/', views.template_field_delete, name='template_field_delete'),
]