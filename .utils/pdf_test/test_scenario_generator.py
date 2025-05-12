import os
import random
from pdfgenerator import PDFGenerator
import pandas as pd
import openpyxl

class TestScenarioGenerator:
    def __init__(self, base_output_dir="test_projects"):
        """Initialize the test scenario generator."""
        self.base_output_dir = base_output_dir
        if not os.path.exists(base_output_dir):
            os.makedirs(base_output_dir)
        # Start barcode counter to avoid duplicates across projects
        self.next_barcode = 1
        # Generate a random starting comid (8 digits) only once
        self.next_comid = random.randint(10000000, 99999999)
        
    def create_project_dir(self, scenario_name):
        """Create a directory for a specific test scenario."""
        project_dir = os.path.join(self.base_output_dir, scenario_name)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        
        # Create PDF subfolder with project-specific name
        pdf_folder_name = f"PDFs zu {scenario_name}"
        pdf_dir = os.path.join(project_dir, pdf_folder_name)
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
        
        return project_dir, pdf_dir

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
            
            # Use 10-digit padded number for filename, increment class counter to avoid duplicates
            padded_number = f"{self.next_barcode:010d}"
            self.next_barcode += 1
            
            doc_spec = {
                'pages': pages,
                'has_a3': i in docs_with_a3,
                'has_oversized': i in oversized_docs,
                'filename': f'{padded_number}.pdf',
                'barcode': padded_number
            }
            docs.append(doc_spec)
        
        return docs

    def create_comlist(self, project_name, docs, project_dir):
        """Create a comlist Excel file for the project."""
        # Create data for Excel file
        comids = []
        for _ in range(len(docs)):
            # Convert comid to string to ensure Excel treats it as text
            comids.append(str(self.next_comid))
            self.next_comid += 1
        
        data = {
            # Ensure barcode is treated as string (it already is, but being explicit)
            'barcode': [str(doc['barcode']) for doc in docs],
            'comid': comids
        }
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel file
        excel_filename = f"{project_name}_comlist.xlsx"
        excel_path = os.path.join(project_dir, excel_filename)
        
        # Use ExcelWriter with string format for both columns
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
            # Get the worksheet
            worksheet = writer.sheets['Sheet1']
            
            # Format the barcode and comid columns as text
            for row in range(2, len(df) + 2):  # Start from row 2 (skipping header)
                worksheet.cell(row=row, column=1).number_format = '@'  # barcode
                worksheet.cell(row=row, column=2).number_format = '@'  # comid
        
        return excel_path

    def generate_scenario_rrd001(self):
        """RRD001-2025_OU_Full-NoTemp-Normal: ~2700-2800 pages, no temp roll"""
        project_name = "RRD001-2025_OU_Full-NoTemp-Normal"
        project_dir, pdf_dir = self.create_project_dir(project_name)
        pdf_gen = PDFGenerator(output_dir=pdf_dir)
        
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
        
        # Create comlist Excel file
        self.create_comlist(project_name, docs, project_dir)

    def generate_scenario_rrd002(self):
        """RRD002-2025_OU_Partial-NoTemp-Normal: ~2400-2500 pages"""
        project_name = "RRD002-2025_OU_Partial-NoTemp-Normal"
        project_dir, pdf_dir = self.create_project_dir(project_name)
        pdf_gen = PDFGenerator(output_dir=pdf_dir)
        
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
        
        # Create comlist Excel file
        self.create_comlist(project_name, docs, project_dir)

    def generate_scenario_rrd003(self):
        """RRD003-2025_OU_Partial-NoTemp-Oversized: ~2500 pages with oversized"""
        project_name = "RRD003-2025_OU_Partial-NoTemp-Oversized"
        project_dir, pdf_dir = self.create_project_dir(project_name)
        pdf_gen = PDFGenerator(output_dir=pdf_dir)
        
        total_pages = random.randint(2400, 2500)
        num_docs = 20  # As specified in the scenario
        
        docs = self.generate_document_specs(num_docs, total_pages, include_oversized=True)
        
        for doc in docs:
            pdf_gen.generate_pdf(
                num_pages=doc['pages'],
                filename=doc['filename'],
                oversized_percentage=0.08 if doc['has_oversized'] else 0,
                include_a3=doc['has_a3'],
                consecutive_oversized_percentage=0.3 if doc['has_oversized'] else 0
            )
        
        # Create comlist Excel file
        self.create_comlist(project_name, docs, project_dir)

    def generate_scenario_rrd004(self):
        """RRD004-2025_OU_Full-Temp-Normal: ~3100 pages, designed to use temp roll"""
        project_name = "RRD004-2025_OU_Full-Temp-Normal"
        project_dir, pdf_dir = self.create_project_dir(project_name)
        pdf_gen = PDFGenerator(output_dir=pdf_dir)
        
        # Create one roll of around 2900 pages + 200 extra pages
        total_pages = random.randint(3050, 3150)
        num_docs = total_pages // 100  # Average 100 pages per doc
        
        docs = self.generate_document_specs(num_docs, total_pages)
        
        for doc in docs:
            pdf_gen.generate_pdf(
                num_pages=doc['pages'],
                filename=doc['filename'],
                oversized_percentage=0,
                include_a3=doc['has_a3']
            )
        
        # Create comlist Excel file (in the main project directory, not in PDF folder)
        self.create_comlist(project_name, docs, project_dir)

    def generate_all_scenarios(self):
        """Generate all test scenarios."""
        self.generate_scenario_rrd001()
        self.generate_scenario_rrd002()
        self.generate_scenario_rrd003()
        self.generate_scenario_rrd004()  # Add the new scenario
        # Add more scenarios as needed

if __name__ == "__main__":
    generator = TestScenarioGenerator()
    generator.generate_all_scenarios() 