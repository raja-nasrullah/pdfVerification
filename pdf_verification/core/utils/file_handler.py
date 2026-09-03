import os
import zipfile
from datetime import datetime
import shutil

class FileHandler:
    
    @staticmethod
    def get_file_size(file):
        """Get file size in KB"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return size / 1024  # Size in KB
    
    @staticmethod
    def get_file_extension(filename):
        """Get file extension"""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def is_pdf(filename):
        """Check if file is PDF"""
        return FileHandler.get_file_extension(filename) == '.pdf'
    
    @staticmethod
    def is_zip(filename):
        """Check if file is ZIP"""
        return FileHandler.get_file_extension(filename) == '.zip'
    
    @staticmethod
    def create_upload_dir():
        """Create upload directory if not exists"""
        upload_dir = 'media/uploads'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        return upload_dir
    
    @staticmethod
    def get_timestamp():
        """Get timestamp for unique filename"""
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    @staticmethod
    def extract_pdfs_from_zip(zip_file_path, extract_to_dir):
        """
        Extract all PDF files from a ZIP archive.
        
        Args:
            zip_file_path (str): Path to the ZIP file
            extract_to_dir (str): Directory to extract PDFs to
            
        Returns:
            list: List of extracted PDF file paths
        """
        extracted_pdfs = []
        
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Get list of all files in ZIP
                all_files = zip_ref.namelist()
                
                # Filter for PDF files
                pdf_files = [f for f in all_files if f.lower().endswith('.pdf')]
                
                if not pdf_files:
                    return []  # No PDF found in ZIP
                
                # Extract each PDF
                for pdf_file in pdf_files:
                    # Get the base filename (without path)
                    base_filename = os.path.basename(pdf_file)
                    
                    # Create unique filename with timestamp
                    timestamp = FileHandler.get_timestamp()
                    unique_filename = f"{timestamp}_{base_filename}"
                    extract_path = os.path.join(extract_to_dir, unique_filename)
                    
                    # Extract the file
                    with zip_ref.open(pdf_file) as source, open(extract_path, 'wb') as target:
                        shutil.copyfileobj(source, target)
                    
                    extracted_pdfs.append(extract_path)
                    
        except zipfile.BadZipFile:
            raise ValueError("Invalid ZIP file")
        except Exception as e:
            raise Exception(f"Error extracting ZIP: {str(e)}")
        
        return extracted_pdfs
    
    @staticmethod
    def handle_uploaded_file(file, filename):
        """
        Handle uploaded file (PDF or ZIP).
        
        Args:
            file: Uploaded file object
            filename (str): Original filename
            
        Returns:
            dict: {
                'success': bool,
                'message': str,
                'pdfs': list,  # List of saved PDF paths
                'file_type': str  # 'pdf' or 'zip'
            }
        """
        upload_dir = FileHandler.create_upload_dir()
        timestamp = FileHandler.get_timestamp()
        
        # Generate unique filename
        base_name = os.path.splitext(filename)[0]
        extension = FileHandler.get_file_extension(filename)
        unique_filename = f"{timestamp}_{base_name}{extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save the uploaded file
        with open(file_path, 'wb') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Check if it's a PDF
        if FileHandler.is_pdf(filename):
            return {
                'success': True,
                'message': 'PDF file uploaded successfully',
                'pdfs': [file_path],
                'file_type': 'pdf',
                'original_name': filename
            }
        
        # Check if it's a ZIP
        elif FileHandler.is_zip(filename):
            # Extract PDFs from ZIP
            try:
                extracted_pdfs = FileHandler.extract_pdfs_from_zip(file_path, upload_dir)
                
                if not extracted_pdfs:
                    # No PDF found in ZIP, clean up the ZIP file
                    os.remove(file_path)
                    return {
                        'success': False,
                        'message': 'No PDF files found in the ZIP archive',
                        'pdfs': [],
                        'file_type': 'zip'
                    }
                
                # Optionally delete the ZIP file after extraction (cleanup)
                os.remove(file_path)
                
                return {
                    'success': True,
                    'message': f'Successfully extracted {len(extracted_pdfs)} PDF(s) from ZIP',
                    'pdfs': extracted_pdfs,
                    'file_type': 'zip',
                    'original_name': filename
                }
                
            except Exception as e:
                # Clean up the ZIP file if extraction failed
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {
                    'success': False,
                    'message': f'Error extracting ZIP: {str(e)}',
                    'pdfs': [],
                    'file_type': 'zip'
                }
        
        # Unsupported file type
        else:
            # Clean up unsupported file
            if os.path.exists(file_path):
                os.remove(file_path)
            return {
                'success': False,
                'message': f'Unsupported file type: {extension}. Please upload PDF or ZIP files.',
                'pdfs': [],
                'file_type': 'unknown'
            }
    
    @staticmethod
    def get_pdfs_from_zip(zip_file_path):
        """
        Get list of PDF filenames from ZIP without extracting.
        
        Args:
            zip_file_path (str): Path to the ZIP file
            
        Returns:
            list: List of PDF filenames in the ZIP
        """
        pdfs = []
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                all_files = zip_ref.namelist()
                pdfs = [f for f in all_files if f.lower().endswith('.pdf')]
        except:
            pass
        return pdfs
    
    @staticmethod
    def cleanup_temp_files(file_paths):
        """
        Clean up temporary files.
        
        Args:
            file_paths (list): List of file paths to delete
        """
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass