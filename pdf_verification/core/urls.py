from django.urls import path
from core.views.summary_view import *
from core.views import admin_view

app_name = 'core'

urlpatterns = [
    # ===== ADMIN DASHBOARD (DEFAULT PAGE) =====
    path('', admin_view.index, name='admin_index'),
    
    # ===== ADMIN UPLOAD VIEW =====
    path('admin-panel/upload/', UploadPDFView.as_view(), name='upload'),
    
    # ===== VIEW UPLOADED DATA (NEW) =====
    path('admin-panel/uploaded-data/', admin_view.uploaded_data, name='admin_uploaded_data'),
    path('admin-panel/record/<int:record_id>/', admin_view.record_detail, name='admin_record_detail'),
    
    # ===== API ENDPOINTS =====
    path('api/upload/', UploadPDFView.as_view(), name='api_upload'),
    path('api/get-results/', GetResultsView.as_view(), name='get_results'),
    path('api/clear-data/', ClearDataView.as_view(), name='clear_data'),

    # ===== ADMIN DASHBOARD VIEWS =====
    path('admin-panel/', admin_view.index, name='admin_index'),
    path('admin-panel/users/', admin_view.users, name='admin_users'),
    path('admin-panel/add-user/', admin_view.add_user, name='admin_add_user'),
    path('admin-panel/user-details/', admin_view.user_details, name='admin_user_details'),
    path('admin-panel/create-agent/', admin_view.create_agent, name='admin_create_agent'),
    path('admin-panel/profile/', admin_view.profile, name='admin_profile'),
    path('admin-panel/charts/', admin_view.charts, name='admin_charts'),
    path('admin-panel/tables/', admin_view.tables, name='admin_tables'),
    path('admin-panel/forms/', admin_view.forms, name='admin_forms'),
    path('admin-panel/components/', admin_view.components, name='admin_components'),
    path('admin-panel/alerts/', admin_view.alerts, name='admin_alerts'),
    path('admin-panel/modals/', admin_view.modals, name='admin_modals'),
    path('admin-panel/settings/', admin_view.settings, name='admin_settings'),
    path('admin-panel/blank/', admin_view.blank, name='admin_blank'),
    path('admin-panel/login/', admin_view.login, name='admin_login'),
    path('admin-panel/register/', admin_view.register, name='admin_register'),
    path('admin-panel/forgot-password/', admin_view.forgot_password, name='admin_forgot_password'),
    path('admin-panel/404/', admin_view.error_404, name='admin_404'),
    path('admin-panel/500/', admin_view.error_500, name='admin_500'),
]