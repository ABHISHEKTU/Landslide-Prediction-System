"""
URL configuration for landslide_detection project.

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

from .import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),

# =================== admin ===========================================
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin_manage_authority/', views.admin_manage_authority, name='admin_manage_authority'),
    path('admin_view_authority/', views.admin_view_authority, name='admin_view_authority'),
    path('admin_delete_authority/<int:authority_id>/', views.admin_delete_authority, name='admin_delete_authority'),
    path('manage_helpline/', views.manage_helpline, name='manage_helpline'),
    path('view_reporting_admin/', views.view_reporting_admin, name='view_reporting_admin'),
    path('admin_edit_authority/<int:authority_id>/', views.admin_edit_authority, name='admin_edit_authority'),
    path('view_reporting_admin2/', views.view_reporting_admin2, name='view_reporting_admin2'),
    path('reply_complaint/<int:complaint_id>/', views.reply_complaint, name='reply_complaint'),
    path('send_emergency_notification/', views.send_emergency_notification, name='send_emergency_notification'),
    path('view_complaints/', views.view_complaints, name='view_complaints'),


# =======================authority===========================================
    path('authority_home/', views.authority_home, name='authority_home'),
    path('report_landslide_authority/', views.report_landslide_authority, name='report_landslide_authority'),
    path('view_emergencyNoti_authority/', views.view_emergencyNoti_authority, name='view_emergencyNoti_authority'),
    path('view_reporting_authority/', views.view_reporting_authority, name='view_reporting_authority'),
    path('send_complaint_authority/', views.send_complaint_authority, name='send_complaint_authority'),
    path('profile/', views.profile, name='profile'),


# ===========================user===========================================
    path('user_registration/', views.user_registration, name='user_registration'),
    path('report_landslide_users/', views.report_landslide_users, name='report_landslide_users'),
    path('send_complaint_user/', views.send_complaint_user, name='send_complaint_user'),
    path('view_reporting_users/', views.view_reporting_users, name='view_reporting_users'),
    path('view_emergencyNoti_users/', views.view_emergencyNoti_users, name='view_emergencyNoti_users'),
    path('user_registration/', views.user_registration, name='user_registration'),
    path('view_helpline_users/', views.view_helpline_users, name='view_helpline_users'),
    path('logout/', views.logout, name='logout'),
     path('user_home/', views.user_home, name='user_home'),

    path('emergency_notification/', views.emergency_notification, name='emergency_notification'),
    
    
    path('update_profile/', views.update_profile, name='update_profile'),
   
    
    path('about/', views.about, name='about'),
    path('user_registration/', views.user_registration, name='user_registration'),
     

    path("landslide_page", views.authority_landslide_page, name="landslide_page"),
    path("api/landslide-predict/", views.landslide_predict_view_authority, name="landslide_prediction"),
    path("api/save-authority-report/", views.save_authority_report, name="save_authority_report"),
    path("user_landslide_page", views.user_landslide_page, name="user_landslide_page"),
    path("api/user_landslide-predict/", views.landslide_predict_view, name="landslide_prediction"),
    path("api/save-user-report/", views.save_user_report, name="save_user_report"),
   
    path("admin_delete_helpline/<int:id>/", views.admin_delete_helpline, name="admin_delete_helpline"),

]
