#!/usr/bin/env python3
"""
Automated Optical Inspection (AOI) Orientation Visualization Module

This module provides comprehensive visualization tools for orientation detection results.
It creates visual reports showing detected orientations, confidence scores, and 
comparison overlays to help validate and understand the orientation detection process.
"""

import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
import seaborn as sns
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrientationVisualizer:
    """
    Visualization tools for orientation detection results.
    
    This class creates comprehensive visual reports showing:
    - Original and rotated images side by side
    - Rotation confidence scores and quality metrics
    - Overlay comparisons with difference maps
    - Score progression charts
    - Summary statistics
    """
    
    def __init__(self, output_dir: str = "orientation_results", dpi: int = 150):
        """
        Initialize the orientation visualizer.
        
        Args:
            output_dir: Directory to save visualization outputs
            dpi: DPI for saved images
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.dpi = dpi
        
        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")
        
        logger.info(f"OrientationVisualizer initialized, output dir: {self.output_dir}")
    
    def create_orientation_comparison(self, original_img: np.ndarray, 
                                    reproduction_img: np.ndarray,
                                    orientation_result: Dict[str, Any],
                                    page_num: int = 1) -> str:
        """
        Create a comprehensive orientation comparison visualization.
        
        Args:
            original_img: Original document image
            reproduction_img: Reproduction image
            orientation_result: Results from OrientationDetector.detect_orientation()
            page_num: Page number for labeling
            
        Returns:
            Path to saved visualization
        """
        logger.info(f"Creating orientation comparison for page {page_num}")
        
        # Apply detected rotation to reproduction
        from orientation_detector import OrientationDetector
        detector = OrientationDetector()
        rotated_reproduction = detector.apply_detected_orientation(reproduction_img, orientation_result)
        
        # Create figure with custom layout
        fig = plt.figure(figsize=(20, 12))
        gs = GridSpec(3, 4, figure=fig, height_ratios=[2, 2, 1], width_ratios=[1, 1, 1, 1])
        
        # Main title
        final_rotation = orientation_result['final_rotation']
        confidence = orientation_result['final_confidence']
        quality = orientation_result['quality']
        
        fig.suptitle(f'Page {page_num} - Orientation Detection Results\n'
                    f'Detected Rotation: {final_rotation:.1f}° | '
                    f'Confidence: {confidence:.3f} | Quality: {quality.upper()}',
                    fontsize=16, fontweight='bold')
        
        # Row 1: Original images comparison
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.imshow(original_img, cmap='gray')
        ax1.set_title('Original Document', fontsize=12, fontweight='bold')
        ax1.axis('off')
        
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.imshow(reproduction_img, cmap='gray')
        ax2.set_title('Reproduction (Original Orientation)', fontsize=12, fontweight='bold')
        ax2.axis('off')
        
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.imshow(rotated_reproduction, cmap='gray')
        ax3.set_title(f'Reproduction (Rotated {final_rotation:.1f}°)', fontsize=12, fontweight='bold')
        ax3.axis('off')
        
        # Row 1, Col 4: Overlay comparison
        ax4 = fig.add_subplot(gs[0, 3])
        overlay = self._create_overlay_image(original_img, rotated_reproduction)
        ax4.imshow(overlay)
        ax4.set_title('Overlay Comparison\n(Red: Original, Green: Rotated)', fontsize=12, fontweight='bold')
        ax4.axis('off')
        
        # Row 2: Edge detection comparison
        ax5 = fig.add_subplot(gs[1, 0])
        orig_edges = cv2.Canny(original_img, 50, 150)
        ax5.imshow(orig_edges, cmap='gray')
        ax5.set_title('Original Edges', fontsize=12)
        ax5.axis('off')
        
        ax6 = fig.add_subplot(gs[1, 1])
        repro_edges = cv2.Canny(reproduction_img, 50, 150)
        ax6.imshow(repro_edges, cmap='gray')
        ax6.set_title('Reproduction Edges (Original)', fontsize=12)
        ax6.axis('off')
        
        ax7 = fig.add_subplot(gs[1, 2])
        rotated_edges = cv2.Canny(rotated_reproduction, 50, 150)
        ax7.imshow(rotated_edges, cmap='gray')
        ax7.set_title('Reproduction Edges (Rotated)', fontsize=12)
        ax7.axis('off')
        
        ax8 = fig.add_subplot(gs[1, 3])
        # Ensure edges have same dimensions before computing difference
        if orig_edges.shape != rotated_edges.shape:
            rotated_edges = cv2.resize(rotated_edges, (orig_edges.shape[1], orig_edges.shape[0]))
        edge_diff = cv2.absdiff(orig_edges, rotated_edges)
        ax8.imshow(edge_diff, cmap='hot')
        ax8.set_title('Edge Difference Map', fontsize=12)
        ax8.axis('off')
        
        # Row 3: Metrics and scores
        ax9 = fig.add_subplot(gs[2, :2])
        self._plot_rotation_scores(ax9, orientation_result)
        
        ax10 = fig.add_subplot(gs[2, 2:])
        self._plot_metrics_summary(ax10, orientation_result)
        
        # Add quality indicator border
        color_map = {'high': 'green', 'medium': 'orange', 'low': 'red'}
        border_color = color_map.get(quality, 'gray')
        
        for spine in fig.patch.get_children():
            if hasattr(spine, 'set_edgecolor'):
                spine.set_edgecolor(border_color)
                spine.set_linewidth(3)
        
        plt.tight_layout()
        
        # Save the visualization
        output_path = self.output_dir / f"page_{page_num:03d}_orientation_analysis.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor=border_color)
        plt.close()
        
        logger.info(f"Orientation comparison saved to: {output_path}")
        return str(output_path)
    
    def _create_overlay_image(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Create an RGB overlay of two grayscale images."""
        # Ensure same dimensions
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
        
        # Normalize images
        img1_norm = cv2.normalize(img1, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        img2_norm = cv2.normalize(img2, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        
        # Create RGB overlay (red channel = img1, green channel = img2)
        overlay = np.zeros((img1.shape[0], img1.shape[1], 3), dtype=np.uint8)
        overlay[:, :, 0] = img1_norm  # Red channel
        overlay[:, :, 1] = img2_norm  # Green channel
        overlay[:, :, 2] = 0          # Blue channel
        
        return overlay
    
    def _plot_rotation_scores(self, ax, orientation_result: Dict[str, Any]):
        """Plot rotation scores for coarse detection."""
        coarse_result = orientation_result.get('coarse_result', {})
        all_results = coarse_result.get('all_results', {})
        
        if not all_results:
            ax.text(0.5, 0.5, 'No rotation scores available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Rotation Scores')
            return
        
        rotations = list(all_results.keys())
        scores = [result['combined_score'] for result in all_results.values()]
        
        # Create bar plot
        bars = ax.bar(rotations, scores, alpha=0.7, edgecolor='black')
        
        # Highlight best rotation
        best_rotation = coarse_result.get('best_rotation', 0)
        for i, rotation in enumerate(rotations):
            if rotation == best_rotation:
                bars[i].set_color('red')
                bars[i].set_alpha(1.0)
        
        ax.set_xlabel('Rotation Angle (degrees)')
        ax.set_ylabel('Combined Score')
        ax.set_title('Coarse Rotation Detection Scores')
        ax.grid(True, alpha=0.3)
        
        # Add score labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                   f'{score:.3f}', ha='center', va='bottom', fontsize=10)
    
    def _plot_metrics_summary(self, ax, orientation_result: Dict[str, Any]):
        """Plot summary metrics and information."""
        ax.axis('off')
        
        # Extract key information
        final_rotation = orientation_result.get('final_rotation', 0)
        confidence = orientation_result.get('final_confidence', 0)
        quality = orientation_result.get('quality', 'unknown')
        
        coarse_result = orientation_result.get('coarse_result', {})
        fine_result = orientation_result.get('fine_result', {})
        
        # Create summary text
        summary_text = f"""
ORIENTATION DETECTION SUMMARY

Final Results:
  • Total Rotation: {final_rotation:.1f}°
  • Confidence: {confidence:.3f}
  • Quality Level: {quality.upper()}

Coarse Detection:
  • Best Rotation: {coarse_result.get('best_rotation', 0)}°
  • Score: {coarse_result.get('best_score', 0):.3f}
  • Confidence: {coarse_result.get('confidence', 0):.3f}

Fine Detection:
"""
        
        if fine_result:
            summary_text += f"""  • Fine Angle: {fine_result.get('best_fine_angle', 0):.1f}°
  • Score: {fine_result.get('best_score', 0):.3f}
  • Confidence: {fine_result.get('confidence', 0):.3f}"""
        else:
            summary_text += "  • Skipped (low coarse confidence)"
        
        # Add method scores if available
        if 'all_results' in coarse_result:
            best_rot = coarse_result['best_rotation']
            if best_rot in coarse_result['all_results']:
                individual_scores = coarse_result['all_results'][best_rot].get('individual_scores', {})
                if individual_scores:
                    summary_text += f"""

Individual Method Scores:
  • SSIM: {individual_scores.get('ssim', 0):.3f}
  • Feature Matching: {individual_scores.get('feature_matching', 0):.3f}
  • Edge Correlation: {individual_scores.get('edge_correlation', 0):.3f}
  • Template Matching: {individual_scores.get('template_matching', 0):.3f}"""
        
        ax.text(0.05, 0.95, summary_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    def create_fine_angle_plot(self, orientation_result: Dict[str, Any], 
                              page_num: int = 1) -> Optional[str]:
        """
        Create a detailed plot of fine angle detection results.
        
        Args:
            orientation_result: Results from OrientationDetector.detect_orientation()
            page_num: Page number for labeling
            
        Returns:
            Path to saved plot, or None if no fine detection was performed
        """
        fine_result = orientation_result.get('fine_result')
        if not fine_result:
            logger.info("No fine detection results available for plotting")
            return None
        
        all_results = fine_result.get('all_results', {})
        if not all_results:
            return None
        
        logger.info(f"Creating fine angle plot for page {page_num}")
        
        # Extract data
        angles = list(all_results.keys())
        scores = [result['combined_score'] for result in all_results.values()]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Plot 1: Score vs angle
        ax1.plot(angles, scores, 'b-', linewidth=2, marker='o', markersize=4)
        
        # Highlight best angle
        best_angle = fine_result.get('best_fine_angle', 0)
        best_score = fine_result.get('best_score', 0)
        ax1.plot(best_angle, best_score, 'ro', markersize=10, label=f'Best: {best_angle:.1f}°')
        
        ax1.set_xlabel('Fine Angle Adjustment (degrees)')
        ax1.set_ylabel('Combined Score')
        ax1.set_title(f'Page {page_num} - Fine Angle Detection Results')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Plot 2: Individual method scores (if available)
        methods = ['ssim', 'edge_correlation']
        method_data = {method: [] for method in methods}
        
        for result in all_results.values():
            individual_scores = result.get('individual_scores', {})
            for method in methods:
                method_data[method].append(individual_scores.get(method, 0))
        
        for method, data in method_data.items():
            if data:  # Only plot if data is available
                ax2.plot(angles, data, label=method.replace('_', ' ').title(), 
                        linewidth=1.5, marker='s', markersize=3)
        
        ax2.set_xlabel('Fine Angle Adjustment (degrees)')
        ax2.set_ylabel('Individual Method Scores')
        ax2.set_title('Individual Method Performance')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        
        # Save the plot
        output_path = self.output_dir / f"page_{page_num:03d}_fine_angle_analysis.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Fine angle plot saved to: {output_path}")
        return str(output_path)
    
    def create_confidence_heatmap(self, multiple_results: List[Dict[str, Any]], 
                                page_numbers: List[int]) -> str:
        """
        Create a heatmap showing confidence scores across multiple pages.
        
        Args:
            multiple_results: List of orientation detection results
            page_numbers: Corresponding page numbers
            
        Returns:
            Path to saved heatmap
        """
        logger.info(f"Creating confidence heatmap for {len(multiple_results)} pages")
        
        # Extract data for heatmap
        rotations = [0, 90, 180, 270]
        confidence_matrix = []
        page_labels = []
        
        for i, result in enumerate(multiple_results):
            page_num = page_numbers[i] if i < len(page_numbers) else i + 1
            page_labels.append(f"Page {page_num}")
            
            coarse_result = result.get('coarse_result', {})
            all_results = coarse_result.get('all_results', {})
            
            # Get scores for each rotation
            row = []
            for rotation in rotations:
                if rotation in all_results:
                    score = all_results[rotation]['combined_score']
                else:
                    score = 0.0
                row.append(score)
            
            confidence_matrix.append(row)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, max(6, len(page_labels) * 0.4)))
        
        im = ax.imshow(confidence_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        # Set ticks and labels
        ax.set_xticks(range(len(rotations)))
        ax.set_xticklabels([f"{r}°" for r in rotations])
        ax.set_yticks(range(len(page_labels)))
        ax.set_yticklabels(page_labels)
        
        # Add text annotations
        for i in range(len(page_labels)):
            for j in range(len(rotations)):
                text = ax.text(j, i, f'{confidence_matrix[i][j]:.2f}',
                             ha="center", va="center", color="black", fontweight='bold')
        
        ax.set_xlabel('Rotation Angle')
        ax.set_ylabel('Pages')
        ax.set_title('Orientation Detection Confidence Scores Across Pages')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Confidence Score', rotation=270, labelpad=15)
        
        plt.tight_layout()
        
        # Save the heatmap
        output_path = self.output_dir / "confidence_heatmap.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Confidence heatmap saved to: {output_path}")
        return str(output_path)
    
    def create_summary_report(self, multiple_results: List[Dict[str, Any]], 
                            page_numbers: List[int], 
                            document_name: str = "Document") -> str:
        """
        Create a comprehensive summary report for multiple pages.
        
        Args:
            multiple_results: List of orientation detection results
            page_numbers: Corresponding page numbers
            document_name: Name of the document for the report
            
        Returns:
            Path to saved summary report
        """
        logger.info(f"Creating summary report for {document_name}")
        
        # Calculate statistics
        total_pages = len(multiple_results)
        rotations = [result.get('final_rotation', 0) for result in multiple_results]
        confidences = [result.get('final_confidence', 0) for result in multiple_results]
        qualities = [result.get('quality', 'unknown') for result in multiple_results]
        
        # Count quality levels
        quality_counts = {'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}
        for quality in qualities:
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        
        # Count rotation angles
        rotation_counts = {}
        for rotation in rotations:
            # Round to nearest degree for counting
            rounded_rotation = round(rotation)
            rotation_counts[rounded_rotation] = rotation_counts.get(rounded_rotation, 0) + 1
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(16, 12))
        gs = GridSpec(3, 3, figure=fig)
        
        fig.suptitle(f'Orientation Detection Summary Report - {document_name}\n'
                    f'Total Pages: {total_pages} | '
                    f'Average Confidence: {np.mean(confidences):.3f}',
                    fontsize=16, fontweight='bold')
        
        # Plot 1: Rotation distribution
        ax1 = fig.add_subplot(gs[0, 0])
        rotation_angles = list(rotation_counts.keys())
        rotation_counts_values = list(rotation_counts.values())
        
        bars1 = ax1.bar(rotation_angles, rotation_counts_values, alpha=0.7, edgecolor='black')
        ax1.set_xlabel('Detected Rotation (degrees)')
        ax1.set_ylabel('Number of Pages')
        ax1.set_title('Distribution of Detected Rotations')
        ax1.grid(True, alpha=0.3)
        
        # Add count labels on bars
        for bar, count in zip(bars1, rotation_counts_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    str(count), ha='center', va='bottom')
        
        # Plot 2: Quality distribution
        ax2 = fig.add_subplot(gs[0, 1])
        quality_labels = list(quality_counts.keys())
        quality_values = list(quality_counts.values())
        colors = ['green', 'orange', 'red', 'gray']
        
        wedges, texts, autotexts = ax2.pie(quality_values, labels=quality_labels, 
                                          colors=colors, autopct='%1.1f%%', startangle=90)
        ax2.set_title('Quality Distribution')
        
        # Plot 3: Confidence histogram
        ax3 = fig.add_subplot(gs[0, 2])
        ax3.hist(confidences, bins=20, alpha=0.7, edgecolor='black')
        ax3.axvline(np.mean(confidences), color='red', linestyle='--', 
                   label=f'Mean: {np.mean(confidences):.3f}')
        ax3.set_xlabel('Confidence Score')
        ax3.set_ylabel('Number of Pages')
        ax3.set_title('Confidence Score Distribution')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Page-by-page rotation
        ax4 = fig.add_subplot(gs[1, :])
        ax4.plot(page_numbers, rotations, 'b-o', linewidth=2, markersize=6)
        ax4.set_xlabel('Page Number')
        ax4.set_ylabel('Detected Rotation (degrees)')
        ax4.set_title('Detected Rotation by Page')
        ax4.grid(True, alpha=0.3)
        
        # Add horizontal lines for common rotations
        for angle in [0, 90, 180, 270]:
            ax4.axhline(y=angle, color='gray', linestyle=':', alpha=0.5)
        
        # Plot 5: Statistics table
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')
        
        # Calculate additional statistics
        most_common_rotation = max(rotation_counts, key=rotation_counts.get)
        rotation_std = np.std(rotations)
        confidence_std = np.std(confidences)
        
        stats_text = f"""
SUMMARY STATISTICS

Document: {document_name}
Total Pages Analyzed: {total_pages}
Processing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ROTATION ANALYSIS:
  • Most Common Rotation: {most_common_rotation}° ({rotation_counts[most_common_rotation]} pages)
  • Average Rotation: {np.mean(rotations):.1f}°
  • Rotation Std Dev: {rotation_std:.1f}°
  • Rotation Range: {min(rotations):.1f}° to {max(rotations):.1f}°

CONFIDENCE ANALYSIS:
  • Average Confidence: {np.mean(confidences):.3f}
  • Confidence Std Dev: {confidence_std:.3f}
  • Min Confidence: {min(confidences):.3f}
  • Max Confidence: {max(confidences):.3f}

QUALITY BREAKDOWN:
  • High Quality: {quality_counts['high']} pages ({quality_counts['high']/total_pages*100:.1f}%)
  • Medium Quality: {quality_counts['medium']} pages ({quality_counts['medium']/total_pages*100:.1f}%)
  • Low Quality: {quality_counts['low']} pages ({quality_counts['low']/total_pages*100:.1f}%)

RECOMMENDATIONS:
"""
        
        # Add recommendations based on results
        if np.mean(confidences) >= 0.7:
            stats_text += "  ✓ Overall high confidence - results are reliable\n"
        elif np.mean(confidences) >= 0.3:
            stats_text += "  ⚠ Medium confidence - manual verification recommended\n"
        else:
            stats_text += "  ✗ Low confidence - manual review required\n"
        
        if rotation_std < 5:
            stats_text += "  ✓ Consistent rotation across pages\n"
        else:
            stats_text += "  ⚠ Variable rotation - check individual pages\n"
        
        if quality_counts['high'] / total_pages >= 0.8:
            stats_text += "  ✓ High quality detection for most pages\n"
        else:
            stats_text += "  ⚠ Mixed quality results - review low-quality pages\n"
        
        ax5.text(0.05, 0.95, stats_text, transform=ax5.transAxes, 
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        plt.tight_layout()
        
        # Save the report
        output_path = self.output_dir / f"{document_name.replace(' ', '_')}_summary_report.png"
        plt.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Summary report saved to: {output_path}")
        return str(output_path)
    
    def save_results_json(self, results: List[Dict[str, Any]], 
                         page_numbers: List[int],
                         document_name: str = "Document") -> str:
        """
        Save orientation detection results to a JSON file.
        
        Args:
            results: List of orientation detection results
            page_numbers: Corresponding page numbers
            document_name: Name of the document
            
        Returns:
            Path to saved JSON file
        """
        # Prepare data for JSON export
        export_data = {
            'document_name': document_name,
            'timestamp': datetime.now().isoformat(),
            'total_pages': len(results),
            'summary_statistics': {
                'average_rotation': float(np.mean([r.get('final_rotation', 0) for r in results])),
                'average_confidence': float(np.mean([r.get('final_confidence', 0) for r in results])),
                'rotation_std': float(np.std([r.get('final_rotation', 0) for r in results])),
                'confidence_std': float(np.std([r.get('final_confidence', 0) for r in results]))
            },
            'page_results': []
        }
        
        # Add individual page results
        for i, result in enumerate(results):
            page_num = page_numbers[i] if i < len(page_numbers) else i + 1
            
            page_data = {
                'page_number': page_num,
                'final_rotation': result.get('final_rotation', 0),
                'final_confidence': result.get('final_confidence', 0),
                'quality': result.get('quality', 'unknown'),
                'coarse_rotation': result.get('coarse_result', {}).get('best_rotation', 0),
                'fine_angle': result.get('fine_result', {}).get('best_fine_angle', 0) if result.get('fine_result') else None,
                'timestamp': result.get('timestamp', datetime.now().isoformat())
            }
            
            export_data['page_results'].append(page_data)
        
        # Save to JSON file
        output_path = self.output_dir / f"{document_name.replace(' ', '_')}_orientation_results.json"
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"Results JSON saved to: {output_path}")
        return str(output_path)


def create_batch_visualization(original_images: List[np.ndarray],
                             reproduction_images: List[np.ndarray],
                             orientation_results: List[Dict[str, Any]],
                             page_numbers: List[int],
                             document_name: str = "Document",
                             output_dir: str = "orientation_results") -> Dict[str, str]:
    """
    Create comprehensive visualizations for a batch of pages.
    
    Args:
        original_images: List of original document images
        reproduction_images: List of reproduction images
        orientation_results: List of orientation detection results
        page_numbers: List of page numbers
        document_name: Name of the document
        output_dir: Output directory for visualizations
        
    Returns:
        Dictionary with paths to created visualizations
    """
    visualizer = OrientationVisualizer(output_dir)
    
    created_files = {}
    
    # Create individual page comparisons
    for i, (orig_img, repro_img, result) in enumerate(zip(original_images, reproduction_images, orientation_results)):
        page_num = page_numbers[i] if i < len(page_numbers) else i + 1
        
        # Main comparison
        comparison_path = visualizer.create_orientation_comparison(orig_img, repro_img, result, page_num)
        created_files[f'page_{page_num}_comparison'] = comparison_path
        
        # Fine angle plot (if available)
        fine_plot_path = visualizer.create_fine_angle_plot(result, page_num)
        if fine_plot_path:
            created_files[f'page_{page_num}_fine_angles'] = fine_plot_path
    
    # Create batch visualizations
    if len(orientation_results) > 1:
        # Confidence heatmap
        heatmap_path = visualizer.create_confidence_heatmap(orientation_results, page_numbers)
        created_files['confidence_heatmap'] = heatmap_path
        
        # Summary report
        summary_path = visualizer.create_summary_report(orientation_results, page_numbers, document_name)
        created_files['summary_report'] = summary_path
        
        # JSON export
        json_path = visualizer.save_results_json(orientation_results, page_numbers, document_name)
        created_files['results_json'] = json_path
    
    logger.info(f"Batch visualization complete. Created {len(created_files)} files in {output_dir}")
    
    return created_files
