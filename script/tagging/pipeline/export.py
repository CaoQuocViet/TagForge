#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger("export")

class MetadataExporter:
    """Export metadata to CSV and manage output directories"""
    
    def __init__(self, output_base_dir="E:/WORK/canva/output"):
        self.output_base_dir = Path(output_base_dir)
        
        # Create base output directory if it doesn't exist
        os.makedirs(output_base_dir, exist_ok=True)
        
        logger.info(f"MetadataExporter initialized with output_dir: {output_base_dir}")
    
    def export_metadata(self, target_dir, metadata_list, input_root_dir):
        """
        Export metadata to CSV and create output directory structure
        
        Args:
            target_dir: Target directory name (e.g., "110790-speeches")
            metadata_list: List of metadata for images
            input_root_dir: Input root directory to locate svg directory
            
        Returns:
            Bool indicating success
        """
        if not metadata_list:
            logger.warning(f"Empty metadata list for {target_dir}")
            return False
        
        # Create target directory
        output_dir = self.output_base_dir / target_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Path to CSV file
        csv_path = output_dir / "metadata.csv"
        
        try:
            # Create DataFrame from metadata
            df = pd.DataFrame(metadata_list)
            
            # Ensure columns are in required order
            column_order = ["filename", "title", "keywords", "Artist", "description"]
            df = df[column_order]
            
            # Write to CSV with proper quoting
            df.to_csv(csv_path, 
                     index=False,
                     encoding='utf-8',
                     quoting=1,  # Quote all non-numeric fields
                     quotechar='"',
                     escapechar='\\')
            
            logger.info(f"Metadata exported successfully: {csv_path}")
            
            # Copy SVG and PNG directories if needed
            self._copy_asset_folders(target_dir, input_root_dir)
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting metadata for {target_dir}: {e}")
            return False
    
    def export_batch_results(self, batch_results, input_root_dir):
        """
        Export batch results
        
        Args:
            batch_results: Dict with directory name as key and metadata list as value
            input_root_dir: Input root directory
            
        Returns:
            Number of successfully processed directories
        """
        success_count = 0
        
        for target_dir, metadata_list in batch_results.items():
            if self.export_metadata(target_dir, metadata_list, input_root_dir):
                success_count += 1
        
        logger.info(f"Successfully exported {success_count}/{len(batch_results)} directories")
        return success_count
    
    def _copy_asset_folders(self, target_dir, input_root_dir):
        """
        Copy svg and png directories if needed
        
        Args:
            target_dir: Target directory name
            input_root_dir: Input root directory
        """
        # Theme directory in input
        input_theme_dir = Path(input_root_dir) / target_dir
        
        # Destination
        output_theme_dir = self.output_base_dir / target_dir
        
        # Directories to copy
        asset_folders = ["svg"]  # Only copy svg, png not needed as we have metadata
        
        for folder in asset_folders:
            src_dir = input_theme_dir / folder
            dst_dir = output_theme_dir / folder
            
            if src_dir.exists() and src_dir.is_dir():
                if dst_dir.exists():
                    logger.info(f"Removing old destination directory: {dst_dir}")
                    shutil.rmtree(dst_dir)
                
                logger.info(f"Copying {folder} directory from {src_dir} to {dst_dir}")
                shutil.copytree(src_dir, dst_dir)
            else:
                logger.warning(f"Source directory not found: {src_dir}") 