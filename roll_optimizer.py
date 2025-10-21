#!/usr/bin/env python3
"""
Roll Capacity Optimizer

Finds the best combination of documents to fit into a roll with limited capacity,
considering padding requirements for each document.
"""

from itertools import combinations
from typing import List, Tuple, Dict


class RollOptimizer:
    def __init__(self, roll_capacity: int, padding_per_document: int = 100):
        self.roll_capacity = roll_capacity
        self.padding_per_document = padding_per_document
    
    def calculate_effective_size(self, document_pages: int) -> int:
        """Calculate the effective size of a document including padding."""
        return document_pages + self.padding_per_document
    
    def find_best_combination(self, documents: List[int], optimize_for: str = 'pages') -> Dict:
        """
        Find the best combination of documents that maximizes either page usage
        or number of documents while staying within roll capacity.
        
        Args:
            documents: List of document page counts
            optimize_for: 'pages' to maximize total pages, 'count' to maximize document count
            
        Returns:
            Dictionary with best combination details
        """
        best_combination = []
        best_total_pages = 0
        best_document_count = 0
        best_effective_size = 0
        best_remaining_capacity = self.roll_capacity
        
        # Try all possible combinations
        for r in range(1, len(documents) + 1):
            for combo in combinations(enumerate(documents), r):
                indices, pages = zip(*combo)
                
                # Calculate effective size with padding
                effective_sizes = [self.calculate_effective_size(p) for p in pages]
                total_effective_size = sum(effective_sizes)
                
                # Check if combination fits in roll
                if total_effective_size <= self.roll_capacity:
                    total_pages = sum(pages)
                    document_count = len(pages)
                    
                    # Update best based on optimization criteria
                    is_better = False
                    if optimize_for == 'pages':
                        # Prioritize total pages, then document count as tiebreaker
                        if (total_pages > best_total_pages or 
                            (total_pages == best_total_pages and document_count > best_document_count)):
                            is_better = True
                    elif optimize_for == 'count':
                        # Prioritize document count, then total pages as tiebreaker
                        if (document_count > best_document_count or 
                            (document_count == best_document_count and total_pages > best_total_pages)):
                            is_better = True
                    
                    if is_better:
                        best_combination = list(zip(indices, pages, effective_sizes))
                        best_total_pages = total_pages
                        best_document_count = document_count
                        best_effective_size = total_effective_size
                        best_remaining_capacity = self.roll_capacity - total_effective_size
        
        return {
            'combination': best_combination,
            'total_pages': best_total_pages,
            'document_count': best_document_count,
            'total_effective_size': best_effective_size,
            'remaining_capacity': best_remaining_capacity,
            'utilization_percent': (best_effective_size / self.roll_capacity) * 100,
            'optimization_mode': optimize_for
        }
    
    def print_results(self, documents: List[int], result: Dict):
        """Print formatted results of the optimization."""
        print("=" * 60)
        print("ROLL CAPACITY OPTIMIZATION RESULTS")
        print("=" * 60)
        print(f"Roll Capacity: {self.roll_capacity} pages")
        print(f"Padding per document: {self.padding_per_document} pages")
        print(f"Optimization mode: {'Maximum pages' if result['optimization_mode'] == 'pages' else 'Maximum documents'}")
        print()
        
        print("Available Documents:")
        for i, pages in enumerate(documents):
            effective = self.calculate_effective_size(pages)
            print(f"  Document {i}: {pages} pages (effective: {effective} pages)")
        print()
        
        if result['combination']:
            print("BEST COMBINATION:")
            print("-" * 30)
            for idx, pages, effective in result['combination']:
                print(f"  Document {idx}: {pages} pages (effective: {effective} pages)")
            
            print()
            print("SUMMARY:")
            print(f"  Number of documents: {result['document_count']}")
            print(f"  Total document pages: {result['total_pages']}")
            print(f"  Total effective size: {result['total_effective_size']}")
            print(f"  Remaining capacity: {result['remaining_capacity']}")
            print(f"  Roll utilization: {result['utilization_percent']:.1f}%")
            
            # Show the roll layout
            print()
            print("ROLL LAYOUT:")
            layout = []
            for idx, pages, effective in result['combination']:
                layout.extend([50, pages, 50])  # padding, document, padding
            
            layout_str = " + ".join(str(x) for x in layout)
            print(f"  {layout_str} = {sum(layout)} pages")
        else:
            print("No valid combination found that fits in the roll capacity!")


def main():
    # Problem parameters
    roll_capacity = 2900
    documents = [91, 779, 520, 198, 494, 630]
    padding_per_document = 100
    
    # Create optimizer
    optimizer = RollOptimizer(roll_capacity, padding_per_document)
    
    # Find best combination for maximum pages
    print("OPTIMIZING FOR MAXIMUM PAGES:")
    result_pages = optimizer.find_best_combination(documents, optimize_for='pages')
    optimizer.print_results(documents, result_pages)
    
    print("\n" + "="*60 + "\n")
    
    # Find best combination for maximum document count
    print("OPTIMIZING FOR MAXIMUM DOCUMENTS:")
    result_count = optimizer.find_best_combination(documents, optimize_for='count')
    optimizer.print_results(documents, result_count)
    
    # Additional analysis
    print()
    print("=" * 60)
    print("ADDITIONAL ANALYSIS")
    print("=" * 60)
    
    # Show all valid combinations
    all_combinations = []
    
    for r in range(1, len(documents) + 1):
        for combo in combinations(enumerate(documents), r):
            indices, pages = zip(*combo)
            effective_sizes = [optimizer.calculate_effective_size(p) for p in pages]
            total_effective_size = sum(effective_sizes)
            
            if total_effective_size <= roll_capacity:
                total_pages = sum(pages)
                document_count = len(pages)
                all_combinations.append({
                    'indices': indices,
                    'pages': pages,
                    'document_count': document_count,
                    'total_pages': total_pages,
                    'total_effective_size': total_effective_size,
                    'utilization': (total_effective_size / roll_capacity) * 100
                })
    
    # Sort by total pages (descending)
    all_combinations_by_pages = sorted(all_combinations, key=lambda x: x['total_pages'], reverse=True)
    
    print("Top 10 combinations by TOTAL PAGES:")
    for i, combo in enumerate(all_combinations_by_pages[:10]):
        doc_list = ", ".join(f"Doc{idx}" for idx in combo['indices'])
        print(f"  {i+1:2d}. {doc_list}: {combo['document_count']} docs, {combo['total_pages']} pages "
              f"({combo['total_effective_size']}/{roll_capacity}, "
              f"{combo['utilization']:.1f}% utilization)")
    
    # Sort by document count (descending), then by total pages
    all_combinations_by_count = sorted(all_combinations, 
                                     key=lambda x: (x['document_count'], x['total_pages']), 
                                     reverse=True)
    
    print(f"\nTop 10 combinations by DOCUMENT COUNT:")
    for i, combo in enumerate(all_combinations_by_count[:10]):
        doc_list = ", ".join(f"Doc{idx}" for idx in combo['indices'])
        print(f"  {i+1:2d}. {doc_list}: {combo['document_count']} docs, {combo['total_pages']} pages "
              f"({combo['total_effective_size']}/{roll_capacity}, "
              f"{combo['utilization']:.1f}% utilization)")


if __name__ == "__main__":
    main()
