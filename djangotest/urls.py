"""
URL configuration for djangotest project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.contrib.auth import views as auth_views

from main import views

urlpatterns = [
    path('', auth_views.LoginView.as_view(template_name='login.html'), name='login'),  # Default home page
    path('admin/', admin.site.urls),
    path('main/',views.main_page, name='main'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),  # Logout page
    path('level-4/', views.level_4_page, name='HL_LL'),  # Level 4 page
    path('delete-text/<int:text_id>/', views.delete_text, name='delete_text'),  # Delete text
    path('edit-text/<int:text_id>/', views.edit_text, name='edit_text'),  # Edit text
    path('generate-ppt/', views.generate_ppt, name='generate_ppt'),
    path('add_text/', views.add_text, name='add_text'),
    path('level-3/', views.level_3_page, name='level_3_page'),
    path('level-2/', views.level_2_page, name='level_2_page'),
    path('add_text', views.add_text, name='add_text'),  # Add text page
    path('level-1/', views.level_1_page, name='level_1_page'),
    path('delete-texts/', views.admin_delete_texts, name='admin_delete_texts'),
    path('redirect-after-login/', views.redirect_after_login, name='redirect_after_login'),
]
