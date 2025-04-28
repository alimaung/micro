import os
import random
from pdfgenerator import PDFGenerator

class TestScenarioGenerator:
    def __init__(self, base_output_dir="test_projects"):
        """Initialize the test scenario generator."""
        self.base_output_dir = base_output_dir
        if not os.path.exists(base_output_dir):
            os.makedirs(base_output_dir)
        
    def create_project_dir(self, scenario_name):
        """Create a directory for a specific test scenario."""
        project_dir = os.path.join(self.base_output_dir, scenario_name)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        return project_dir

    def generate_document_specs(self, num_docs, total_pages, include_oversized=False, oversized_doc_ratio=0.08):
        """Generate specifications for documents in a project."""
        docs = []
        remaining_pages = total_pages
        
        # Determine which documents will have A3 pages (20% of documents)
        docs_with_a3 = random.sample(range(num_docs), int(num_docs * 0.2))
        
        # Determine which documents will have oversized pages
        oversized_docs = []
        if include_oversized:
            num_oversized_docs = max(1, int(num_docs * oversized_doc_ratio))
            oversized_docs = random.sample(range(num_docs), num_oversized_docs)
        
        # Calculate average pages per document
        avg_pages = remaining_pages // num_docs
        
        for i in range(num_docs):
            # Ensure last document gets remaining pages
            if i == num_docs - 1:
                pages = remaining_pages
            else:
                # Random variation around average (±20%)
                variation = int(avg_pages * 0.2)
                pages = random.randint(avg_pages - variation, avg_pages + variation)
                pages = max(10, min(pages, remaining_pages - 10))  # Ensure minimum 10 pages
            
            remaining_pages -= pages
            
            doc_spec = {
                'pages': pages,
                'has_a3': i in docs_with_a3,
                'has_oversized': i in oversized_docs,
                'filename': f'document_{i+1:03d}.pdf'
            }
            docs.append(doc_spec)
        
        return docs

    def generate_scenario_a1(self):
        """Full Roll No Temp: ~2700-2800 pages, no temp roll"""
        project_dir = self.create_project_dir("A1_FullRoll_NoTemp")
        pdf_gen = PDFGenerator(output_dir=project_dir)
        
        total_pages = random.randint(2700, 2800)
        num_docs = total_pages // 100  # Average 100 pages per doc
        
        docs = self.generate_document_specs(num_docs, total_pages)
        
        for doc in docs:
            pdf_gen.generate_pdf(
                num_pages=doc['pages'],
                filename=doc['filename'],
                oversized_percentage=0,
                include_a3=doc['has_a3']
            )

    def generate_scenario_a2(self):
        """Full Roll With Temp: ~2400-2500 pages, creates temp roll"""
        project_dir = self.create_project_dir("A2_FullRoll_WithTemp")
        pdf_gen = PDFGenerator(output_dir=project_dir)
        
        total_pages = random.randint(2400, 2500)
        num_docs = total_pages // 100
        
        docs = self.generate_document_specs(num_docs, total_pages)
        
        for doc in docs:
            pdf_gen.generate_pdf(
                num_pages=doc['pages'],
                filename=doc['filename'],
                oversized_percentage=0,
                include_a3=doc['has_a3']
            )

    def generate_scenario_b1(self):
        """Mixed Single Roll: ~2500 pages with oversized"""
        project_dir = self.create_project_dir("B1_MixedSingleRoll")
        pdf_gen = PDFGenerator(output_dir=project_dir)
        
        total_pages = random.randint(2400, 2500)
        num_docs = 20  # As specified in the scenario
        
        docs = self.generate_document_specs(num_docs, total_pages, include_oversized=True)
        
        for doc in docs:
            pdf_gen.generate_pdf(
                num_pages=doc['pages'],
                filename=doc['filename'],
                oversized_percentage=0.08 if doc['has_oversized'] else 0,
                include_a3=doc['has_a3']
            )

    def generate_all_scenarios(self):
        """Generate all test scenarios."""
        self.generate_scenario_a1()
        self.generate_scenario_a2()
        self.generate_scenario_b1()
        # Add more scenarios as needed

if __name__ == "__main__":
    generator = TestScenarioGenerator()
    generator.generate_all_scenarios() 