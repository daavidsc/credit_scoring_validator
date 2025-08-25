#!/usr/bin/env python3
"""
Test the report archiving functionality
"""

import sys
import os
import tempfile
import shutil
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import archive_existing_reports, clear_analysis_cache

def test_archiving():
    """Test that report archiving works correctly"""
    
    print("🗂️  Testing Report Archiving Functionality")
    print("=" * 50)
    
    # Ensure reports directory exists
    reports_dir = "reports/generated"
    os.makedirs(reports_dir, exist_ok=True)
    
    # Create some sample reports for testing
    sample_reports = [
        "test_bias_report.html",
        "test_accuracy_report.html", 
        "test_consistency_report.html"
    ]
    
    print("📝 Creating sample reports for testing...")
    for report in sample_reports:
        report_path = os.path.join(reports_dir, report)
        with open(report_path, "w") as f:
            f.write(f"<html><body><h1>Test Report: {report}</h1></body></html>")
        print(f"   ✅ Created {report}")
    
    # Check initial state
    print(f"\n📂 Initial reports in {reports_dir}:")
    for file in os.listdir(reports_dir):
        if file.endswith('.html'):
            print(f"   📄 {file}")
    
    # Test archiving function
    print("\n🗃️  Testing archive_existing_reports()...")
    archived_files = archive_existing_reports()
    print(f"   Archived files: {archived_files}")
    
    # Check reports directory after archiving
    print(f"\n📂 Reports remaining in {reports_dir} after archiving:")
    remaining_files = []
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith('.html'):
                remaining_files.append(file)
                print(f"   📄 {file}")
    
    if not remaining_files:
        print("   (none - all reports were archived)")
    
    # Check archive directory
    archive_dir = "reports/archive"
    print(f"\n📁 Archive directory contents:")
    if os.path.exists(archive_dir):
        for folder in os.listdir(archive_dir):
            folder_path = os.path.join(archive_dir, folder)
            if os.path.isdir(folder_path):
                print(f"   📁 {folder}/")
                for file in os.listdir(folder_path):
                    print(f"      📄 {file}")
    else:
        print("   (archive directory not found)")
    
    # Test full cache clearing with archiving
    print(f"\n🧹 Testing full cache clearing with archiving...")
    
    # Create new sample reports
    for report in sample_reports:
        report_path = os.path.join(reports_dir, report)
        with open(report_path, "w") as f:
            f.write(f"<html><body><h1>New Test Report: {report}</h1></body></html>")
    
    # Test clearing all cache (should archive reports)
    cache_options = {"clear_all_cache": True}
    result = clear_analysis_cache(cache_options)
    
    if isinstance(result, dict):
        cleared = result.get("cleared_files", [])
        archived = result.get("archived_files", [])
        print(f"   Cleared cache files: {cleared}")
        print(f"   Archived report files: {archived}")
    else:
        print(f"   Result: {result}")
    
    print("\n✅ Report archiving functionality test completed!")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    test_archiving()
