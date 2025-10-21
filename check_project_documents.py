#!/usr/bin/env python3
"""
Script to check and compare documents across multiple projects.
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

from microapp.models import Project, Document

def check_projects(project_ids):
    """Check and compare documents across specified projects."""
    
    print("🔍 Checking projects for duplicate documents...")
    print("=" * 80)
    
    projects_data = {}
    all_documents = defaultdict(list)  # doc_id -> list of projects that have it
    
    # Collect data for each project
    for project_id in project_ids:
        try:
            project = Project.objects.get(id=project_id)
            documents = project.documents.all()
            
            project_info = {
                'project': project,
                'documents': list(documents),
                'doc_ids': set(doc.doc_id for doc in documents),
                'document_count': documents.count(),
                'total_pages': sum(doc.pages for doc in documents if doc.pages),
            }
            
            projects_data[project_id] = project_info
            
            # Track which projects have which documents
            for doc in documents:
                all_documents[doc.doc_id].append(project_id)
            
            print(f"\n📁 Project {project_id}: {project.archive_id} ({project.location})")
            print(f"   Name: {project.name or 'No name'}")
            print(f"   Doc Type: {project.doc_type or 'No doc type'}")
            print(f"   Project Path: {project.project_path}")
            print(f"   Documents: {project_info['document_count']}")
            print(f"   Total Pages: {project_info['total_pages']}")
            print(f"   Created: {project.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Owner: {project.owner.username if project.owner else 'No owner'}")
            
        except Project.DoesNotExist:
            print(f"❌ Project {project_id} not found")
            continue
    
    # Find duplicate documents
    print("\n" + "=" * 80)
    print("🔍 DOCUMENT OVERLAP ANALYSIS")
    print("=" * 80)
    
    duplicate_docs = {doc_id: project_list for doc_id, project_list in all_documents.items() 
                     if len(project_list) > 1}
    
    if duplicate_docs:
        print(f"\n📄 Found {len(duplicate_docs)} documents that appear in multiple projects:")
        
        for doc_id, project_list in sorted(duplicate_docs.items()):
            print(f"\n   Document ID: {doc_id}")
            print(f"   Appears in projects: {project_list}")
            
            # Show details for each occurrence
            for proj_id in project_list:
                if proj_id in projects_data:
                    doc = next((d for d in projects_data[proj_id]['documents'] if d.doc_id == doc_id), None)
                    if doc:
                        print(f"      Project {proj_id}: {doc.pages} pages, path: {doc.path}")
    else:
        print("\n✅ No duplicate documents found across these projects")
    
    # Compare project similarities
    print("\n" + "=" * 80)
    print("🔍 PROJECT SIMILARITY ANALYSIS")
    print("=" * 80)
    
    project_pairs = []
    project_ids_list = list(projects_data.keys())
    
    for i, proj_id1 in enumerate(project_ids_list):
        for proj_id2 in project_ids_list[i+1:]:
            if proj_id1 in projects_data and proj_id2 in projects_data:
                proj1 = projects_data[proj_id1]
                proj2 = projects_data[proj_id2]
                
                # Calculate overlap
                common_docs = proj1['doc_ids'] & proj2['doc_ids']
                total_unique_docs = len(proj1['doc_ids'] | proj2['doc_ids'])
                overlap_percentage = (len(common_docs) / total_unique_docs * 100) if total_unique_docs > 0 else 0
                
                project_pairs.append({
                    'proj1_id': proj_id1,
                    'proj2_id': proj_id2,
                    'proj1': proj1['project'],
                    'proj2': proj2['project'],
                    'common_docs': len(common_docs),
                    'overlap_percentage': overlap_percentage,
                    'proj1_only': len(proj1['doc_ids'] - proj2['doc_ids']),
                    'proj2_only': len(proj2['doc_ids'] - proj1['doc_ids']),
                })
    
    # Sort by overlap percentage (highest first)
    project_pairs.sort(key=lambda x: x['overlap_percentage'], reverse=True)
    
    for pair in project_pairs:
        print(f"\n📊 Projects {pair['proj1_id']} vs {pair['proj2_id']}:")
        print(f"   {pair['proj1'].archive_id} vs {pair['proj2'].archive_id}")
        print(f"   Common documents: {pair['common_docs']}")
        print(f"   Overlap: {pair['overlap_percentage']:.1f}%")
        print(f"   Project {pair['proj1_id']} only: {pair['proj1_only']} documents")
        print(f"   Project {pair['proj2_id']} only: {pair['proj2_only']} documents")
        
        # Check if they have the same basic info
        same_archive_id = pair['proj1'].archive_id == pair['proj2'].archive_id
        same_location = pair['proj1'].location == pair['proj2'].location
        same_doc_type = pair['proj1'].doc_type == pair['proj2'].doc_type
        
        if same_archive_id and same_location and same_doc_type:
            print(f"   🚨 POTENTIAL DUPLICATES: Same archive_id, location, and doc_type!")
        elif same_archive_id:
            print(f"   ⚠️  Same archive_id but different location/doc_type")
        
        if pair['overlap_percentage'] > 80:
            print(f"   🚨 HIGH OVERLAP: {pair['overlap_percentage']:.1f}% document overlap!")
        elif pair['overlap_percentage'] > 50:
            print(f"   ⚠️  MODERATE OVERLAP: {pair['overlap_percentage']:.1f}% document overlap")
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    total_projects = len(projects_data)
    total_documents = sum(len(proj['doc_ids']) for proj in projects_data.values())
    unique_documents = len(all_documents)
    
    print(f"Projects analyzed: {total_projects}")
    print(f"Total documents (with duplicates): {total_documents}")
    print(f"Unique documents: {unique_documents}")
    print(f"Duplicate documents: {len(duplicate_docs)}")
    
    if len(duplicate_docs) > 0:
        duplicate_instances = sum(len(project_list) for project_list in duplicate_docs.values())
        print(f"Total duplicate instances: {duplicate_instances - len(duplicate_docs)}")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    high_overlap_pairs = [p for p in project_pairs if p['overlap_percentage'] > 80]
    if high_overlap_pairs:
        print("   🚨 HIGH PRIORITY - Review these project pairs for potential merging:")
        for pair in high_overlap_pairs:
            print(f"      - Projects {pair['proj1_id']} and {pair['proj2_id']} ({pair['overlap_percentage']:.1f}% overlap)")
    
    duplicate_project_pairs = [p for p in project_pairs if 
                              p['proj1'].archive_id == p['proj2'].archive_id and
                              p['proj1'].location == p['proj2'].location and
                              p['proj1'].doc_type == p['proj2'].doc_type]
    if duplicate_project_pairs:
        print("   🚨 DUPLICATE PROJECTS - Same archive_id, location, and doc_type:")
        for pair in duplicate_project_pairs:
            print(f"      - Projects {pair['proj1_id']} and {pair['proj2_id']} ({pair['proj1'].archive_id})")

def main():
    """Main function."""
    if len(sys.argv) > 1:
        # Use command line arguments
        try:
            project_ids = [int(arg) for arg in sys.argv[1:]]
        except ValueError:
            print("❌ Please provide valid project IDs as arguments")
            print("Usage: python check_project_documents.py 106 111 112 113 114")
            return
    else:
        # Default project IDs
        project_ids = [106, 111, 112, 113, 114]
    
    check_projects(project_ids)

if __name__ == "__main__":
    main()
