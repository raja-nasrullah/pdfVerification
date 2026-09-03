from django.views import View
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
import os
import json
from datetime import datetime
import logging

# Import your services
from core.services.pdf_processor import process_pdf
from core.models import Summary
from core.utils.file_handler import FileHandler

logger = logging.getLogger(__name__)


class UploadPDFView(View):
    """Main view for PDF/ZIP upload and verification"""
    
    template_name = 'core/admin/upload.html'
    
    def get(self, request):
        """Handle GET request - Clear session and show form"""
        request.session.pop('verification_results', None)
        request.session.pop('last_upload', None)
        request.session.pop('uploaded_filename', None)
        
        results = request.session.get('verification_results')
        
        context = {
            'results': results,
            'last_upload': request.session.get('last_upload')
        }
        
        return render(request, self.template_name, context)
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """Handle POST request - Process uploaded file (PDF or ZIP) and SAVE TO DATABASE"""
        
        # Clear old session data
        request.session.pop('verification_results', None)
        request.session.pop('last_upload', None)
        request.session.pop('uploaded_filename', None)
        
        # Check if file is uploaded
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file uploaded'
            }, status=400)
        
        file = request.FILES['file']
        if not file.name:
            return JsonResponse({
                'success': False,
                'error': 'No file selected'
            }, status=400)
        
        # ---- Use FileHandler to process the uploaded file ----
        result = FileHandler.handle_uploaded_file(file, file.name)
        
        # Check if upload was successful
        if not result['success']:
            return JsonResponse({
                'success': False,
                'error': result['message']
            }, status=400)
        
        # ---- Process each PDF found ----
        all_results = []
        saved_records = []
        
        try:
            for pdf_path in result['pdfs']:
                logger.info(f"📄 Processing PDF: {pdf_path}")
                
                # Process the PDF
                companies_data = process_pdf(pdf_path)
                
                # ===== SAVE TO DATABASE - SINGLE ROW =====
                with transaction.atomic():
                    # Get data for each company
                    gepco_data = companies_data.get('GEPCO', {'summary': 0, 'calculated': 0})
                    lesco_data = companies_data.get('LESCO', {'summary': 0, 'calculated': 0})
                    mepco_data = companies_data.get('MEPCO', {'summary': 0, 'calculated': 0})
                    sepco_data = companies_data.get('SEPCO', {'summary': 0, 'calculated': 0})
                    sngpl_data = companies_data.get('SNGPL', {'summary': 0, 'calculated': 0})
                    ssgc_data = companies_data.get('SSGC', {'summary': 0, 'calculated': 0})
                    
                    # Calculate grand totals
                    grand_total_summary = sum(data['summary'] for data in companies_data.values())
                    grand_total_calculated = sum(data['calculated'] for data in companies_data.values())
                    
                    # Get original filename from the saved PDF path
                    original_filename = os.path.basename(pdf_path)
                    
                    # Create single row
                    summary = Summary.objects.create(
                        file_name=original_filename,
                        zip_file_name=result.get('original_name', file.name),
                        
                        # GEPCO
                        gepco_summary=gepco_data['summary'],
                        gepco_calculated=gepco_data['calculated'],
                        gepco_verified=(gepco_data['summary'] == gepco_data['calculated']),
                        
                        # LESCO
                        lesco_summary=lesco_data['summary'],
                        lesco_calculated=lesco_data['calculated'],
                        lesco_verified=(lesco_data['summary'] == lesco_data['calculated']),
                        
                        # MEPCO
                        mepco_summary=mepco_data['summary'],
                        mepco_calculated=mepco_data['calculated'],
                        mepco_verified=(mepco_data['summary'] == mepco_data['calculated']),
                        
                        # SEPCO
                        sepco_summary=sepco_data['summary'],
                        sepco_calculated=sepco_data['calculated'],
                        sepco_verified=(sepco_data['summary'] == sepco_data['calculated']),
                        
                        # SNGPL
                        sngpl_summary=sngpl_data['summary'],
                        sngpl_calculated=sngpl_data['calculated'],
                        sngpl_verified=(sngpl_data['summary'] == sngpl_data['calculated']),
                        
                        # SSGC
                        ssgc_summary=ssgc_data['summary'],
                        ssgc_calculated=ssgc_data['calculated'],
                        ssgc_verified=(ssgc_data['summary'] == ssgc_data['calculated']),
                        
                        # Grand Total
                        grand_total_summary=grand_total_summary,
                        grand_total_calculated=grand_total_calculated,
                        grand_total_verified=(grand_total_summary == grand_total_calculated),
                        
                        # Status
                        is_fully_verified=(grand_total_summary == grand_total_calculated),
                    )
                    
                    saved_records.append({
                        'id': summary.id,
                        'filename': original_filename,
                        'file_path': pdf_path
                    })
                    
                    logger.info(f"✅ Saved summary record ID: {summary.id} for file: {original_filename}")
                    
                    # Store results for response
                    all_results.append({
                        'filename': original_filename,
                        'companies': companies_data,
                        'grand_total': {
                            'summary': grand_total_summary,
                            'calculated': grand_total_calculated,
                            'verified': (grand_total_summary == grand_total_calculated),
                            'difference': abs(grand_total_summary - grand_total_calculated)
                        },
                        'record_id': summary.id,
                        'file_upload_time': datetime.now().strftime('%Y%m%d_%H%M%S'),
                        'timestamp': datetime.now().isoformat()
                    })
            
            # ---- Prepare response ----
            if len(all_results) == 1:
                # Single PDF - use session for display
                results = all_results[0]
                request.session['verification_results'] = results
                request.session['last_upload'] = datetime.now().isoformat()
                request.session['uploaded_filename'] = file.name
                
                return JsonResponse({
                    'success': True,
                    'message': f'File {file.name} processed successfully',
                    'results': results,
                    'record_id': saved_records[0]['id'],
                    'file_path': saved_records[0]['file_path'],
                    'file_type': result['file_type'],
                    'pdf_count': len(all_results)
                })
            else:
                # Multiple PDFs from ZIP - return all
                request.session['verification_results'] = {
                    'multiple': True,
                    'files': all_results,
                    'total': len(all_results)
                }
                request.session['last_upload'] = datetime.now().isoformat()
                request.session['uploaded_filename'] = file.name
                
                return JsonResponse({
                    'success': True,
                    'message': f'Successfully processed {len(all_results)} PDF(s) from {file.name}',
                    'results': all_results,
                    'file_type': result['file_type'],
                    'pdf_count': len(all_results),
                    'records': saved_records
                })
            
        except Exception as e:
            logger.error(f"❌ Error processing file: {e}")
            
            # Clean up any saved PDFs on error
            for pdf_path in result['pdfs']:
                try:
                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)
                except:
                    pass
            
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class GetResultsView(View):
    """View to get latest results from database"""
    
    @staticmethod
    def build_companies_from_summary(summary):
        """Build companies data from Summary model instance"""
        companies = {}
        
        # Define company field mappings
        mapping = {
            'GEPCO': ('gepco_summary', 'gepco_calculated', 'gepco_verified'),
            'LESCO': ('lesco_summary', 'lesco_calculated', 'lesco_verified'),
            'MEPCO': ('mepco_summary', 'mepco_calculated', 'mepco_verified'),
            'SEPCO': ('sepco_summary', 'sepco_calculated', 'sepco_verified'),
            'SNGPL': ('sngpl_summary', 'sngpl_calculated', 'sngpl_verified'),
            'SSGC': ('ssgc_summary', 'ssgc_calculated', 'ssgc_verified'),
        }
        
        for company, (summary_field, calculated_field, verified_field) in mapping.items():
            companies[company] = {
                'summary': float(getattr(summary, summary_field, 0)),
                'calculated': float(getattr(summary, calculated_field, 0)),
                'verified': getattr(summary, verified_field, False),
                'transactions': []  # Transactions are stored separately
            }
        
        return companies
    
    def get(self, request):
        # Try to get from session first
        results = request.session.get('verification_results')
        
        if not results:
            # Get the latest record from database
            try:
                latest = Summary.objects.order_by('-created_at').first()
                
                if latest:
                    companies_data = self.build_companies_from_summary(latest)
                    
                    # Calculate grand totals
                    grand_total_summary = sum(data['summary'] for data in companies_data.values())
                    grand_total_calculated = sum(data['calculated'] for data in companies_data.values())
                    
                    results = {
                        'companies': companies_data,
                        'grand_total': {
                            'summary': float(latest.grand_total_summary),
                            'calculated': float(latest.grand_total_calculated),
                            'verified': latest.grand_total_verified,
                            'difference': abs(float(latest.grand_total_summary) - float(latest.grand_total_calculated))
                        },
                        'filename': latest.file_name,
                        'timestamp': latest.created_at.isoformat(),
                        'db_saved': True,
                        'record_id': latest.id,
                        'file_upload_time': latest.created_at.strftime('%Y%m%d_%H%M%S')
                    }
                    
                    # Store in session
                    request.session['verification_results'] = results
                    request.session['last_upload'] = datetime.now().isoformat()
                    
            except Exception as e:
                logger.error(f"Error fetching from database: {e}")
        
        if not results:
            return JsonResponse({
                'success': False,
                'message': 'No data available. Please upload a PDF.',
                'data': None
            })
        
        return JsonResponse({
            'success': True,
            'data': results,
            'last_upload': request.session.get('last_upload')
        })


class ClearDataView(View):
    """View to clear all cached data"""
    
    def get(self, request):
        request.session.flush()
        return JsonResponse({
            'success': True,
            'message': 'All data cleared successfully'
        })