"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('attendance/', views.attendance, name='attendance'),
    path('mark_attendance/', views.mark_attendance, name='mark_attendance'),
    path('apply_leave/', views.apply_leave, name='apply_leave'),
    path('check_out/', views.check_out, name='check_out'),
    path('apply_leave_form/', views.apply_leave_form, name='apply_leave_form'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('admindashboard/', views.admindashboard, name='admindashboard'),
    path('manage_employee/', views.manage_employee, name='manage_employee'),
    path('delete_employee/<int:id>/', views.delete_employee, name='delete_employee'),
    path('manage_salary/', views.manage_salary, name='manage_salary'),
    path('manage_leave/', views.manage_leave, name='manage_leave'),
    path('admin-leave-action/<int:id>/', views.admin_leave_action, name='admin_leave_action'
    ),
    path('apply_common_increment/', views.apply_common_increment, name='apply_common_increment'),
    path('apply_personal_increment/', views.apply_personal_increment, name='apply_personal_increment'),
    path('common-increment/', views.common_increment_view, name='common_increment'),
    path('personal-increment/', views.personal_increment_view, name='personal_increment'),
    path('add-festival-bonus/', views.add_festival_bonus, name='add_festival_bonus'),
    path('logout_employee/', views.logout_employee, name='logout_employee'),
    path('logout_admin/', views.logout_admin, name='logout_admin'),
    path('manage_attendance/', views.manage_attendance, name='manage_attendance'),
    path('salary/', views.salary, name='salary'),


]
