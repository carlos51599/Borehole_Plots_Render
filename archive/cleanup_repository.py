#!/usr/bin/env python3
"""
Repository Cleanup Script

This script organizes the repository by:
1. Moving test scripts from root to tests/ directory
2. Moving legacy/unused files to archive/ directory
3. Ensuring reports are in reports/ directory

Based on dependency analysis from app.py through the modular architecture.
"""

import os
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Define the root directory
ROOT_DIR = Path(__file__).parent

def ensure_directory_exists(directory: Path):
    """Ensure a directory exists, create if not."""
    directory.mkdir(exist_ok=True)
    logger.info(f"✓ Directory ensured: {directory}")

def move_file_safely(src: Path, dst: Path):
    """Move a file safely, creating destination directory if needed."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    if dst.exists():
        logger.warning(f"Destination exists, skipping: {dst.name}")
        return False
    
    try:
        shutil.move(str(src), str(dst))
        logger.info(f"✓ Moved: {src.name} → {dst}")
        return True
    except Exception as e:
        logger.error(f"✗ Failed to move {src.name}: {e}")
        return False

def cleanup_repository():
    """Main cleanup function."""
    logger.info("🧹 Starting repository cleanup...")
    
    # Ensure required directories exist
    tests_dir = ROOT_DIR / "tests"
    archive_dir = ROOT_DIR / "archive"
    reports_dir = ROOT_DIR / "reports"
    
    ensure_directory_exists(tests_dir)
    ensure_directory_exists(archive_dir)
    ensure_directory_exists(reports_dir)
    
    # Define files used by current modular app (DO NOT ARCHIVE)
    ACTIVE_FILES = {
        # Main entry point
        "app.py",
        
        # Core utilities (heavily imported)
        "app_factory.py",
        "app_constants.py", 
        "coordinate_service.py",
        "geology_code_utils.py",
        "data_loader.py",
        "dataframe_optimizer.py",
        "memory_manager.py",
        "loading_indicators.py",
        "lazy_marker_manager.py",
        "map_utils.py",
        "polyline_utils.py",
        "enhanced_error_handling.py",
        "error_handling.py",
        "error_recovery.py",
        
        # Required data files
        "Geology Codes BGS.csv",
        "requirements.txt",
        "render.yaml",
        
        # AGS data files
        "FLRG - 2025-03-17 1445 - Preliminary - 3.ags",
        "FLRG - 2025-03-17 1445 - Preliminary - 3.txt",
    }
    
    ACTIVE_DIRECTORIES = {
        "app_modules",
        "callbacks", 
        "section",
        "config_modules",
        "state_management",
        "borehole_log",
        "tests",
        "reports",
        "archive",
        "assets",
        "__pycache__",
        "test_results",
        ".github"
    }
    
    # Files to move to tests/ directory
    TEST_FILES_IN_ROOT = [
        "test_archive_exact_proportions.py",
        "test_archive_import.py", 
        "test_archive_numeric_geol_leg.py",
        "test_complete_section_plotting.py",
        "test_footer_layout_fix.py",
        "test_modular_plot_fix.py",
        "test_proper_numeric_geol_leg.py"
    ]
    
    # Legacy files to archive
    LEGACY_FILES = [
        "app_original.py",
        "app_new.py", 
        "config.py",
        "config_original.py",
        "borehole_log_professional.py",
        
        # Debug scripts
        "debug_module.py",
        "debug_data_structure.py",
        "debug_geol_leg_columns.py",
        "debug_geology_mappings.py",
        "debug_offset_layout.py",
        "debug_parser_comparison.py",
        
        # Analysis/diagnostic scripts
        "analyze_config.py",
        "comprehensive_diagnostics.py",
        "comprehensive_optimization_validation.py",
        "fix_layout.py",
        
        # Results files that should be in appropriate directories
        "diagnostic_results.json",
    ]
    
    moved_count = 0
    
    # 1. Move test files from root to tests/
    logger.info("\n📋 Moving test files to tests/ directory...")
    for test_file in TEST_FILES_IN_ROOT:
        src = ROOT_DIR / test_file
        if src.exists():
            dst = tests_dir / test_file
            if move_file_safely(src, dst):
                moved_count += 1
    
    # 2. Move legacy files to archive/
    logger.info("\n📦 Moving legacy files to archive/...")
    for legacy_file in LEGACY_FILES:
        src = ROOT_DIR / legacy_file
        if src.exists():
            dst = archive_dir / legacy_file
            if move_file_safely(src, dst):
                moved_count += 1
    
    # 3. Check for any remaining root files that might need archiving
    logger.info("\n🔍 Checking for other files that might need archiving...")
    for item in ROOT_DIR.iterdir():
        if item.is_file() and item.suffix == ".py":
            if item.name not in ACTIVE_FILES and not item.name.startswith('.'):
                logger.warning(f"⚠️  Unclassified Python file: {item.name}")
                # Ask for manual review rather than auto-archiving
        elif item.is_file() and item.suffix in [".md", ".txt", ".log", ".pdf"]:
            if item.name.endswith(".md") and item.name not in ["README.md"]:
                # Check if this should be in reports/
                logger.info(f"ℹ️  Report file that could go to reports/: {item.name}")
    
    # 4. Summary
    logger.info(f"\n✅ Cleanup complete! Moved {moved_count} files.")
    logger.info("\n📊 Current structure:")
    logger.info(f"  Active app files: {len(ACTIVE_FILES)} core files")
    logger.info(f"  Active packages: {len(ACTIVE_DIRECTORIES)} directories")
    logger.info(f"  Tests organized: {len(TEST_FILES_IN_ROOT)} test files → tests/")
    logger.info(f"  Legacy archived: {len(LEGACY_FILES)} files → archive/")
    
    return moved_count

if __name__ == "__main__":
    try:
        moved = cleanup_repository()
        print(f"\n🎉 Repository cleanup successful! Moved {moved} files.")
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")
        raise
