from django.db import models

class Summary(models.Model):
    # File information
    file_name = models.CharField(max_length=255)
    zip_file_name = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    
    # GEPCO
    gepco_summary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gepco_calculated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    gepco_verified = models.BooleanField(default=False)
    
    # LESCO
    lesco_summary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    lesco_calculated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    lesco_verified = models.BooleanField(default=False)
    
    # MEPCO
    mepco_summary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mepco_calculated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mepco_verified = models.BooleanField(default=False)
    
    # SEPCO
    sepco_summary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sepco_calculated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sepco_verified = models.BooleanField(default=False)
    
    # SNGPL
    sngpl_summary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sngpl_calculated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sngpl_verified = models.BooleanField(default=False)
    
    # SSGC
    ssgc_summary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    ssgc_calculated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    ssgc_verified = models.BooleanField(default=False)
    
    # Grand Total
    grand_total_summary = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grand_total_calculated = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grand_total_verified = models.BooleanField(default=False)
    
    # Overall status
    is_fully_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'summaries'
        ordering = ['-created_at']
        verbose_name = 'Summary'
        verbose_name_plural = 'Summaries'
    
    def __str__(self):
        return f"{self.file_name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"