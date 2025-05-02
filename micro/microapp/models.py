from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    # Core project identification
    archive_id = models.CharField(max_length=20, help_text="Format: RRDxxx-xxxx")
    location = models.CharField(max_length=10, help_text="Location code (e.g., OU, DW)")
    doc_type = models.CharField(max_length=50, blank=True, null=True)
    
    # Path information
    project_path = models.CharField(max_length=500)
    project_folder_name = models.CharField(max_length=255)
    pdf_folder_path = models.CharField(max_length=500, blank=True, null=True)
    comlist_path = models.CharField(max_length=500, blank=True, null=True)
    output_dir = models.CharField(max_length=500, blank=True, null=True)
    
    # Project flags
    has_pdf_folder = models.BooleanField(default=False)
    
    # Processing status
    processing_complete = models.BooleanField(default=False)
    
    # Processing settings from project setup
    retain_sources = models.BooleanField(default=True)
    add_to_database = models.BooleanField(default=True)
    
    # Process results (to be populated in later steps)
    has_oversized = models.BooleanField(default=False, null=True, blank=True)
    total_pages = models.IntegerField(null=True, blank=True)
    total_pages_with_refs = models.IntegerField(null=True, blank=True)
    
    # Timestamps and ownership
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.archive_id} ({self.location})"
    
    @property
    def location_code(self):
        """
        Get the numeric location code used for film number allocation.
        Returns: "1" for OU, "2" for DW, "3" for other locations
        """
        location_map = {
            "OU": "1",
            "DW": "2"
        }
        return location_map.get(self.location, "3")
