#!/usr/bin/env python3
"""
Brightness Analysis Tool for Microfilm Quality Assessment

Analyzes brightness and contrast differences between original and reproduced documents
by focusing on background regions rather than text content.
"""

import argparse
import os
import sys
from pathlib import Path
import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from pdf2image import convert_from_path
from typing import List, Tuple, Dict, Any
import json
from datetime import datetime


class BrightnessAnalyzer:
    """Analyzes brightness and contrast in document reproductions."""
    
    def __init__(self, dpi: int = 300, output_dir: str = "brightness_analysis"):
        self.dpi = dpi
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Analysis parameters
        self.edge_margin_percent = 0.05  # 5% margin from edges
        self.min_white_region_size = 100  # minimum pixels for white region
        self.white_threshold = 200  # pixel value threshold for "white" background
        
    def pdf_to_images(self, pdf_path: str) -> List[np.ndarray]:
        """Convert PDF pages to grayscale numpy arrays."""
        print(f"Converting PDF to images: {pdf_path}")
        
        try:
            pil_images = convert_from_path(pdf_path, dpi=self.dpi)
            images = []
            
            for pil_img in pil_images:
                img_array = np.array(pil_img)
                if len(img_array.shape) == 3:
                    gray_img = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray_img = img_array
                images.append(gray_img)
            
            print(f"Converted {len(images)} pages")
            return images
            
        except Exception as e:
            print(f"Error converting PDF {pdf_path}: {e}")
            return []
    
    def extract_edge_regions(self, img: np.ndarray) -> Dict[str, np.ndarray]:
        """Extract edge/margin regions for background analysis."""
        h, w = img.shape
        margin_h = int(h * self.edge_margin_percent)
        margin_w = int(w * self.edge_margin_percent)
        
        regions = {
            'top_edge': img[:margin_h, :],
            'bottom_edge': img[-margin_h:, :],
            'left_edge': img[:, :margin_w],
            'right_edge': img[:, -margin_w:],
            'top_left_corner': img[:margin_h*2, :margin_w*2],
            'top_right_corner': img[:margin_h*2, -margin_w*2:],
            'bottom_left_corner': img[-margin_h*2:, :margin_w*2],
            'bottom_right_corner': img[-margin_h*2:, -margin_w*2:]
        }
        
        return regions
    
    def find_white_regions(self, img: np.ndarray) -> np.ndarray:
        """Find large white/background regions in the image."""
        # Create binary mask of white regions
        white_mask = img > self.white_threshold
        
        # Remove small regions (likely noise)
        kernel = np.ones((3, 3), np.uint8)
        white_mask = cv2.morphologyEx(white_mask.astype(np.uint8), cv2.MORPH_OPEN, kernel)
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find connected components and filter by size
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(white_mask, connectivity=8)
        
        # Create mask of large white regions only
        large_white_mask = np.zeros_like(white_mask)
        for i in range(1, num_labels):  # Skip background label (0)
            if stats[i, cv2.CC_STAT_AREA] > self.min_white_region_size:
                large_white_mask[labels == i] = 1
        
        return large_white_mask.astype(bool)
    
    def analyze_brightness_regions(self, img: np.ndarray) -> Dict[str, Any]:
        """Comprehensive brightness analysis of different image regions."""
        
        # 1. Edge region analysis
        edge_regions = self.extract_edge_regions(img)
        edge_stats = {}
        
        for region_name, region_img in edge_regions.items():
            if region_img.size > 0:
                edge_stats[region_name] = {
                    'mean': float(np.mean(region_img)),
                    'std': float(np.std(region_img)),
                    'median': float(np.median(region_img)),
                    'min': float(np.min(region_img)),
                    'max': float(np.max(region_img))
                }
        
        # 2. White region analysis
        white_mask = self.find_white_regions(img)
        white_pixels = img[white_mask]
        
        white_stats = {}
        if len(white_pixels) > 0:
            white_stats = {
                'mean': float(np.mean(white_pixels)),
                'std': float(np.std(white_pixels)),
                'median': float(np.median(white_pixels)),
                'pixel_count': int(len(white_pixels)),
                'percentage': float(len(white_pixels) / img.size * 100)
            }
        
        # 3. Overall image statistics
        overall_stats = {
            'mean': float(np.mean(img)),
            'std': float(np.std(img)),
            'median': float(np.median(img)),
            'min': float(np.min(img)),
            'max': float(np.max(img))
        }
        
        # 4. Histogram analysis
        hist, bins = np.histogram(img, bins=256, range=(0, 256))
        hist_stats = {
            'peak_brightness': int(np.argmax(hist)),  # Most common brightness value
            'brightness_range': float(np.max(img) - np.min(img)),
            'histogram': hist.tolist()  # For detailed analysis if needed
        }
        
        return {
            'edge_regions': edge_stats,
            'white_regions': white_stats,
            'overall': overall_stats,
            'histogram': hist_stats,
            'white_region_mask': white_mask  # For visualization
        }
    
    def compare_brightness(self, original_stats: Dict, reproduction_stats: Dict) -> Dict[str, Any]:
        """Compare brightness statistics between original and reproduction."""
        
        comparison = {}
        
        # Compare edge regions
        edge_comparison = {}
        for region_name in original_stats['edge_regions'].keys():
            if region_name in reproduction_stats['edge_regions']:
                orig = original_stats['edge_regions'][region_name]
                repro = reproduction_stats['edge_regions'][region_name]
                
                edge_comparison[region_name] = {
                    'brightness_diff': repro['mean'] - orig['mean'],
                    'brightness_ratio': repro['mean'] / orig['mean'] if orig['mean'] > 0 else 0,
                    'contrast_diff': repro['std'] - orig['std'],
                    'contrast_ratio': repro['std'] / orig['std'] if orig['std'] > 0 else 0
                }
        
        comparison['edge_regions'] = edge_comparison
        
        # Compare white regions
        white_comparison = {}
        if original_stats['white_regions'] and reproduction_stats['white_regions']:
            orig_white = original_stats['white_regions']
            repro_white = reproduction_stats['white_regions']
            
            white_comparison = {
                'brightness_diff': repro_white['mean'] - orig_white['mean'],
                'brightness_ratio': repro_white['mean'] / orig_white['mean'] if orig_white['mean'] > 0 else 0,
                'contrast_diff': repro_white['std'] - orig_white['std'],
                'contrast_ratio': repro_white['std'] / orig_white['std'] if orig_white['std'] > 0 else 0,
                'area_diff_percent': repro_white['percentage'] - orig_white['percentage']
            }
        
        comparison['white_regions'] = white_comparison
        
        # Overall comparison
        orig_overall = original_stats['overall']
        repro_overall = reproduction_stats['overall']
        
        overall_comparison = {
            'brightness_diff': repro_overall['mean'] - orig_overall['mean'],
            'brightness_ratio': repro_overall['mean'] / orig_overall['mean'] if orig_overall['mean'] > 0 else 0,
            'contrast_diff': repro_overall['std'] - orig_overall['std'],
            'contrast_ratio': repro_overall['std'] / orig_overall['std'] if orig_overall['std'] > 0 else 0,
            'dynamic_range_diff': (repro_overall['max'] - repro_overall['min']) - (orig_overall['max'] - orig_overall['min'])
        }
        
        comparison['overall'] = overall_comparison
        
        # Quality assessment
        quality_flags = self.assess_quality_flags(comparison)
        comparison['quality_assessment'] = quality_flags
        
        return comparison
    
    def assess_quality_flags(self, comparison: Dict) -> Dict[str, Any]:
        """Assess quality based on brightness comparison results."""
        
        flags = {
            'overexposed': False,
            'underexposed': False,
            'poor_contrast': False,
            'brightness_shift': False,
            'quality_score': 1.0,
            'issues': []
        }
        
        # Check overall brightness ratio
        brightness_ratio = comparison['overall']['brightness_ratio']
        
        if brightness_ratio > 1.15:  # 15% brighter
            flags['overexposed'] = True
            flags['issues'].append(f"Overexposed: {brightness_ratio:.2f}x brighter than original")
            flags['quality_score'] *= 0.7
            
        elif brightness_ratio < 0.85:  # 15% darker
            flags['underexposed'] = True
            flags['issues'].append(f"Underexposed: {brightness_ratio:.2f}x darker than original")
            flags['quality_score'] *= 0.7
        
        # Check contrast ratio
        contrast_ratio = comparison['overall']['contrast_ratio']
        
        if contrast_ratio < 0.8:  # Lost more than 20% contrast
            flags['poor_contrast'] = True
            flags['issues'].append(f"Poor contrast: {contrast_ratio:.2f}x original contrast")
            flags['quality_score'] *= 0.8
        
        # Check for significant brightness shift in background regions
        if comparison['white_regions']:
            white_brightness_ratio = comparison['white_regions']['brightness_ratio']
            if abs(white_brightness_ratio - 1.0) > 0.1:  # 10% shift in background
                flags['brightness_shift'] = True
                flags['issues'].append(f"Background brightness shift: {white_brightness_ratio:.2f}x")
                flags['quality_score'] *= 0.9
        
        # Overall quality determination
        if flags['quality_score'] > 0.8:
            flags['overall_quality'] = 'GOOD'
        elif flags['quality_score'] > 0.6:
            flags['overall_quality'] = 'ACCEPTABLE'
        else:
            flags['overall_quality'] = 'POOR'
        
        return flags
    
    def create_brightness_visualization(self, original_img: np.ndarray, reproduction_img: np.ndarray,
                                      original_stats: Dict, reproduction_stats: Dict,
                                      comparison: Dict, page_num: int) -> str:
        """Create comprehensive brightness analysis visualization."""
        
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle(f'Page {page_num} Brightness Analysis', fontsize=16, fontweight='bold')
        
        # Original and reproduction images
        axes[0, 0].imshow(original_img, cmap='gray', vmin=0, vmax=255)
        axes[0, 0].set_title('Original Document')
        axes[0, 0].axis('off')
        
        axes[0, 1].imshow(reproduction_img, cmap='gray', vmin=0, vmax=255)
        axes[0, 1].set_title('Microfilm Reproduction')
        axes[0, 1].axis('off')
        
        # Add edge region overlays
        h, w = original_img.shape
        margin_h = int(h * self.edge_margin_percent)
        margin_w = int(w * self.edge_margin_percent)
        
        # Draw edge regions on original
        rect_top = patches.Rectangle((0, 0), w, margin_h, linewidth=2, edgecolor='red', facecolor='none', alpha=0.7)
        rect_bottom = patches.Rectangle((0, h-margin_h), w, margin_h, linewidth=2, edgecolor='red', facecolor='none', alpha=0.7)
        rect_left = patches.Rectangle((0, 0), margin_w, h, linewidth=2, edgecolor='blue', facecolor='none', alpha=0.7)
        rect_right = patches.Rectangle((w-margin_w, 0), margin_w, h, linewidth=2, edgecolor='blue', facecolor='none', alpha=0.7)
        
        axes[0, 0].add_patch(rect_top)
        axes[0, 0].add_patch(rect_bottom)
        axes[0, 0].add_patch(rect_left)
        axes[0, 0].add_patch(rect_right)
        
        # White region masks
        if 'white_region_mask' in original_stats:
            white_overlay_orig = np.zeros((*original_img.shape, 3))
            white_overlay_orig[original_stats['white_region_mask']] = [0, 1, 0]  # Green for white regions
            axes[1, 0].imshow(original_img, cmap='gray', alpha=0.7)
            axes[1, 0].imshow(white_overlay_orig, alpha=0.3)
            axes[1, 0].set_title('Original - White Regions (Green)')
            axes[1, 0].axis('off')
        
        if 'white_region_mask' in reproduction_stats:
            white_overlay_repro = np.zeros((*reproduction_img.shape, 3))
            white_overlay_repro[reproduction_stats['white_region_mask']] = [0, 1, 0]  # Green for white regions
            axes[1, 1].imshow(reproduction_img, cmap='gray', alpha=0.7)
            axes[1, 1].imshow(white_overlay_repro, alpha=0.3)
            axes[1, 1].set_title('Reproduction - White Regions (Green)')
            axes[1, 1].axis('off')
        
        # Histograms
        axes[2, 0].hist(original_img.flatten(), bins=50, alpha=0.7, color='blue', label='Original')
        axes[2, 0].hist(reproduction_img.flatten(), bins=50, alpha=0.7, color='red', label='Reproduction')
        axes[2, 0].set_title('Brightness Histograms')
        axes[2, 0].set_xlabel('Pixel Intensity')
        axes[2, 0].set_ylabel('Frequency')
        axes[2, 0].legend()
        axes[2, 0].grid(True, alpha=0.3)
        
        # Statistics summary
        axes[2, 1].axis('off')
        
        quality = comparison['quality_assessment']
        stats_text = f"""
Brightness Analysis Results:

Overall Quality: {quality['overall_quality']}
Quality Score: {quality['quality_score']:.3f}

Brightness Comparison:
  Ratio: {comparison['overall']['brightness_ratio']:.3f}
  Difference: {comparison['overall']['brightness_diff']:.1f}

Contrast Comparison:
  Ratio: {comparison['overall']['contrast_ratio']:.3f}
  Difference: {comparison['overall']['contrast_diff']:.1f}

Background Analysis:
  Original Mean: {original_stats['overall']['mean']:.1f}
  Reproduction Mean: {reproduction_stats['overall']['mean']:.1f}

Issues Detected:
"""
        
        if quality['issues']:
            for issue in quality['issues']:
                stats_text += f"  • {issue}\n"
        else:
            stats_text += "  • No significant issues detected\n"
        
        axes[2, 1].text(0.05, 0.95, stats_text, fontsize=10, verticalalignment='top', 
                       fontfamily='monospace', transform=axes[2, 1].transAxes)
        
        # Add colored border based on quality
        color_map = {'GOOD': 'green', 'ACCEPTABLE': 'orange', 'POOR': 'red'}
        color = color_map.get(quality['overall_quality'], 'gray')
        rect = patches.Rectangle((0, 0), 1, 1, linewidth=4, edgecolor=color, 
                               facecolor='none', transform=axes[2, 1].transAxes)
        axes[2, 1].add_patch(rect)
        
        plt.tight_layout()
        
        # Save the plot
        output_path = self.output_dir / f"page_{page_num:03d}_brightness_analysis.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return str(output_path)
    
    def analyze_document(self, original_path: str, reproduction_path: str) -> Dict[str, Any]:
        """Analyze brightness differences between original and reproduction documents."""
        
        print(f"Analyzing brightness...")
        print(f"Original: {original_path}")
        print(f"Reproduction: {reproduction_path}")
        
        # Convert PDFs to images
        orig_images = self.pdf_to_images(original_path)
        repro_images = self.pdf_to_images(reproduction_path)
        
        if not orig_images or not repro_images:
            raise ValueError("Failed to convert one or both PDFs to images")
        
        min_pages = min(len(orig_images), len(repro_images))
        page_results = []
        
        for i in range(min_pages):
            page_num = i + 1
            print(f"Analyzing page {page_num}...")
            
            # Resize reproduction to match original if needed
            orig_img = orig_images[i]
            repro_img = repro_images[i]
            
            if orig_img.shape != repro_img.shape:
                repro_img = cv2.resize(repro_img, (orig_img.shape[1], orig_img.shape[0]))
            
            # Analyze brightness for both images
            orig_stats = self.analyze_brightness_regions(orig_img)
            repro_stats = self.analyze_brightness_regions(repro_img)
            
            # Compare brightness
            comparison = self.compare_brightness(orig_stats, repro_stats)
            
            # Create visualization
            viz_path = self.create_brightness_visualization(orig_img, repro_img, orig_stats, 
                                                          repro_stats, comparison, page_num)
            
            page_result = {
                'page': page_num,
                'original_stats': orig_stats,
                'reproduction_stats': repro_stats,
                'comparison': comparison,
                'visualization_path': viz_path
            }
            
            # Remove masks from stats for JSON serialization
            if 'white_region_mask' in page_result['original_stats']:
                del page_result['original_stats']['white_region_mask']
            if 'white_region_mask' in page_result['reproduction_stats']:
                del page_result['reproduction_stats']['white_region_mask']
            
            page_results.append(page_result)
        
        # Calculate overall document assessment
        overall_quality_scores = [p['comparison']['quality_assessment']['quality_score'] for p in page_results]
        overall_issues = []
        for p in page_results:
            overall_issues.extend(p['comparison']['quality_assessment']['issues'])
        
        overall_assessment = {
            'average_quality_score': float(np.mean(overall_quality_scores)),
            'pages_analyzed': len(page_results),
            'all_issues': overall_issues,
            'unique_issues': list(set(overall_issues))
        }
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'original_document': original_path,
            'reproduction_document': reproduction_path,
            'analysis_type': 'brightness_analysis',
            'overall_assessment': overall_assessment,
            'page_results': page_results,
            'settings': {
                'dpi': self.dpi,
                'edge_margin_percent': self.edge_margin_percent,
                'white_threshold': self.white_threshold,
                'min_white_region_size': self.min_white_region_size
            }
        }
        
        # Save report
        report_path = self.output_dir / "brightness_analysis_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nBrightness analysis complete! Report saved to: {report_path}")
        return report
    
    def print_summary(self, report: Dict[str, Any]):
        """Print summary of brightness analysis results."""
        
        overall = report['overall_assessment']
        
        print("\n" + "="*70)
        print("BRIGHTNESS ANALYSIS SUMMARY")
        print("="*70)
        print(f"Pages Analyzed: {overall['pages_analyzed']}")
        print(f"Average Quality Score: {overall['average_quality_score']:.3f}")
        
        if overall['unique_issues']:
            print(f"\nIssues Detected:")
            for issue in overall['unique_issues']:
                print(f"  • {issue}")
        else:
            print(f"\nNo significant brightness issues detected.")
        
        print(f"\nResults saved to: {self.output_dir}")
        print("="*70)


def main():
    """Main function for command-line usage."""
    
    parser = argparse.ArgumentParser(description='Analyze brightness differences between original and microfilm documents')
    parser.add_argument('--original', required=True, help='Path to original PDF')
    parser.add_argument('--reproduction', required=True, help='Path to reproduction PDF')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for PDF conversion (default: 300)')
    parser.add_argument('--output', default='brightness_analysis', help='Output directory (default: brightness_analysis)')
    
    args = parser.parse_args()
    
    # Validate input files
    if not os.path.exists(args.original):
        print(f"Error: Original file not found: {args.original}")
        sys.exit(1)
    
    if not os.path.exists(args.reproduction):
        print(f"Error: Reproduction file not found: {args.reproduction}")
        sys.exit(1)
    
    try:
        # Create analyzer and run analysis
        analyzer = BrightnessAnalyzer(dpi=args.dpi, output_dir=args.output)
        report = analyzer.analyze_document(args.original, args.reproduction)
        analyzer.print_summary(report)
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
