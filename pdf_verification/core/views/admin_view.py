from django.shortcuts import render
from core.models import Summary

# Dashboard
def index(request):
    """Admin Dashboard - Shows statistics and recent uploads"""
    
    # Get statistics from database
    total_files = Summary.objects.count()
    verified_files = Summary.objects.filter(is_fully_verified=True).count()
    mismatched_files = Summary.objects.filter(is_fully_verified=False).count()
    recent_uploads = Summary.objects.order_by('-created_at')[:10]
    
    context = {
        'total_files': total_files,
        'verified_files': verified_files,
        'mismatched_files': mismatched_files,
        'recent_uploads': recent_uploads,
    }
    
    return render(request, 'core/admin/index.html', context)


# ===== ADD THIS FUNCTION =====
def uploaded_data(request):
    """Display all uploaded PDF data from database"""
    
    # 👇 CHANGE THIS LINE to ensure NO records are skipped
    all_records = Summary.objects.all().order_by('id')
    
    # Get statistics
    total_records = all_records.count()
    verified_count = all_records.filter(is_fully_verified=True).count()
    mismatched_count = all_records.filter(is_fully_verified=False).count()
    
    context = {
        'records': all_records,
        'total_records': total_records,
        'verified_count': verified_count,
        'mismatched_count': mismatched_count,
    }
    
    return render(request, 'core/admin/uploaded-data.html', context)

# ===== ADD THIS FUNCTION =====
def record_detail(request, record_id):
    """View detailed information for a single record"""
    
    try:
        record = Summary.objects.get(id=record_id)
    except Summary.DoesNotExist:
        return render(request, 'core/admin/404.html', status=404)
    
    # Calculate differences in Python (Django templates can't subtract)
    record.gepco_diff = record.gepco_summary - record.gepco_calculated
    record.lesco_diff = record.lesco_summary - record.lesco_calculated
    record.mepco_diff = record.mepco_summary - record.mepco_calculated
    record.sepco_diff = record.sepco_summary - record.sepco_calculated
    record.sngpl_diff = record.sngpl_summary - record.sngpl_calculated
    record.ssgc_diff = record.ssgc_summary - record.ssgc_calculated
    record.grand_total_diff = record.grand_total_summary - record.grand_total_calculated
    
    context = {
        'record': record,
    }
    
    return render(request, 'core/admin/record-detail.html', context)

# User Management
def users(request):
    return render(request, 'core/admin/users.html')


def add_user(request):
    return render(request, 'core/admin/add-user.html')


def user_details(request):
    return render(request, 'core/admin/user-details.html')


# Agent Management
def create_agent(request):
    return render(request, 'core/admin/create-agent.html')


# Main Features
def profile(request):
    return render(request, 'core/admin/profile.html')


def charts(request):
    return render(request, 'core/admin/charts.html')


def tables(request):
    return render(request, 'core/admin/tables.html')


def forms(request):
    return render(request, 'core/admin/forms.html')


def components(request):
    return render(request, 'core/admin/components.html')


def alerts(request):
    return render(request, 'core/admin/alerts.html')


def modals(request):
    return render(request, 'core/admin/modals.html')


def settings(request):
    return render(request, 'core/admin/settings.html')


def blank(request):
    return render(request, 'core/admin/blank.html')


# Authentication Pages
def login(request):
    return render(request, 'core/admin/login.html')


def register(request):
    return render(request, 'core/admin/register.html')


def forgot_password(request):
    return render(request, 'core/admin/forgot-password.html')


# Error Pages
def error_404(request):
    return render(request, 'core/admin/404.html', status=404)


def error_500(request):
    return render(request, 'core/admin/500.html', status=500)