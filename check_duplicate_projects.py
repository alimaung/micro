#!/usr/bin/env python3
"""
Script to check for duplicate projects based on archive_id, location, and doc_type.
This script can be run standalone or as a Django management command.
"""

import os
import sys
import django
from collections import defaultdict

# Add the project directory to Python path
project_dir = os.path.join(os.path.dirname(__file__), 'micro')
sys.path.insert(0, project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'micro.settings')
django.setup()

from microapp.models import Project

def check_duplicate_projects():
    """
    Check for duplicate projects based on archive_id, location, and doc_type.
    Returns a dictionary of duplicates grouped by the combination of these fields.
    """
    print("Checking for duplicate projects...")
    print("=" * 60)
    
    # Get all projects
    projects = Project.objects.all().values(
        'id', 'archive_id', 'location', 'doc_type', 'name', 
        'created_at', 'owner__username', 'processing_complete',
        'film_allocation_complete', 'distribution_complete', 'handoff_complete'
    )
    
    # Group projects by the combination of archive_id, location, doc_type
    grouped_projects = defaultdict(list)
    
    for project in projects:
        # Create a key from archive_id, location, doc_type
        # Handle None values by converting to string
        key = (
            project['archive_id'] or 'None',
            project['location'] or 'None', 
            project['doc_type'] or 'None'
        )
        grouped_projects[key].append(project)
    
    # Find duplicates (groups with more than one project)
    duplicates = {key: projects for key, projects in grouped_projects.items() if len(projects) > 1}
    
    if not duplicates:
        print("✅ No duplicate projects found!")
        return
    
    print(f"🔍 Found {len(duplicates)} sets of duplicate projects:")
    print()
    
    total_duplicate_projects = 0
    
    for i, (key, duplicate_projects) in enumerate(duplicates.items(), 1):
        archive_id, location, doc_type = key
        total_duplicate_projects += len(duplicate_projects)
        
        print(f"Duplicate Set #{i}")
        print(f"Archive ID: {archive_id}")
        print(f"Location: {location}")
        print(f"Doc Type: {doc_type}")
        print(f"Number of duplicates: {len(duplicate_projects)}")
        print("-" * 40)
        
        # Sort by creation date (oldest first)
        sorted_projects = sorted(duplicate_projects, key=lambda x: x['created_at'])
        
        for j, project in enumerate(sorted_projects, 1):
            status_indicators = []
            if project['processing_complete']:
                status_indicators.append("✅ Processed")
            if project['film_allocation_complete']:
                status_indicators.append("🎬 Film Allocated")
            if project['distribution_complete']:
                status_indicators.append("📦 Distributed")
            if project['handoff_complete']:
                status_indicators.append("📧 Handed Off")
            
            status_str = " | ".join(status_indicators) if status_indicators else "❌ Not Processed"
            
            print(f"  {j}. Project ID: {project['id']}")
            print(f"     Name: {project['name'] or 'No name'}")
            print(f"     Owner: {project['owner__username'] or 'Unknown'}")
            print(f"     Created: {project['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"     Status: {status_str}")
            print()
        
        print("=" * 60)
        print()
    
    print(f"📊 Summary:")
    print(f"   Total duplicate sets: {len(duplicates)}")
    print(f"   Total duplicate projects: {total_duplicate_projects}")
    print(f"   Total projects in database: {Project.objects.count()}")
    
    # Provide recommendations
    print()
    print("💡 Recommendations:")
    print("   1. Review each duplicate set to determine which projects should be kept")
    print("   2. Consider merging data from duplicate projects if needed")
    print("   3. Delete unnecessary duplicate projects to clean up the database")
    print("   4. Implement unique constraints to prevent future duplicates")

def get_project_details(project_id):
    """Get detailed information about a specific project."""
    try:
        project = Project.objects.get(id=project_id)
        print(f"Project Details for ID {project_id}:")
        print(f"  Archive ID: {project.archive_id}")
        print(f"  Name: {project.name}")
        print(f"  Location: {project.location}")
        print(f"  Doc Type: {project.doc_type}")
        print(f"  Project Path: {project.project_path}")
        print(f"  Owner: {project.owner.username if project.owner else 'None'}")
        print(f"  Created: {project.created_at}")
        print(f"  Processing Complete: {project.processing_complete}")
        print(f"  Film Allocation Complete: {project.film_allocation_complete}")
        print(f"  Distribution Complete: {project.distribution_complete}")
        print(f"  Handoff Complete: {project.handoff_complete}")
        print(f"  Total Pages: {project.total_pages}")
        print(f"  Documents Count: {project.documents.count()}")
        print(f"  Rolls Count: {project.rolls.count()}")
        return project
    except Project.DoesNotExist:
        print(f"❌ Project with ID {project_id} not found")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "details":
        if len(sys.argv) > 2:
            project_id = sys.argv[2]
            try:
                get_project_details(int(project_id))
            except ValueError:
                print("❌ Invalid project ID. Please provide a numeric ID.")
        else:
            print("❌ Please provide a project ID after 'details'")
            print("Usage: python check_duplicate_projects.py details <project_id>")
    else:
        check_duplicate_projects()
