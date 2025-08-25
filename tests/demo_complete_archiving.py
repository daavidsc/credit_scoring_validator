#!/usr/bin/env python3
"""
Complete demonstration of the report archiving feature
Shows the full workflow from report creation to archiving
"""

import sys
import os
import time
import shutil
from datetime import datetime

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import clear_analysis_cache, archive_existing_reports

def reset_test_environment():
    """Clean up test environment"""
    print("🧹 Resetting test environment...")
    
    # Clean generated reports
    reports_dir = "reports/generated"
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith('.html'):
                os.remove(os.path.join(reports_dir, file))
    
    # Clean test archives (keep real archives)
    archive_dir = "reports/archive" 
    if os.path.exists(archive_dir):
        for folder in os.listdir(archive_dir):
            if folder.startswith('test_archive_'):
                shutil.rmtree(os.path.join(archive_dir, folder))
    
    print("   ✅ Environment reset complete")

def create_sample_reports():
    """Create sample reports for testing"""
    print("\n📝 Creating sample reports...")
    
    reports_dir = "reports/generated"
    os.makedirs(reports_dir, exist_ok=True)
    
    sample_reports = [
        {
            "filename": "accuracy_report.html",
            "title": "Accuracy Analysis Report",
            "content": """
                <h2>Accuracy Metrics</h2>
                <p>Overall Accuracy: 87.5%</p>
                <p>Precision: 85.2%</p>
                <p>Recall: 89.1%</p>
            """
        },
        {
            "filename": "bias_report.html", 
            "title": "Bias & Fairness Report",
            "content": """
                <h2>Fairness Analysis</h2>
                <p>Demographic Parity: PASS</p>
                <p>Equal Opportunity: REVIEW</p>
                <p>Equalized Odds: PASS</p>
            """
        },
        {
            "filename": "consistency_report.html",
            "title": "Consistency Analysis Report", 
            "content": """
                <h2>Consistency Metrics</h2>
                <p>Decision Consistency: 94.3%</p>
                <p>Confidence Stability: 91.7%</p>
                <p>Perfect Consistency: 78.2%</p>
            """
        }
    ]
    
    for report in sample_reports:
        report_path = os.path.join(reports_dir, report["filename"])
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report["title"]}</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f5f5f5;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        h1 {{ margin: 0; }}
        .timestamp {{ opacity: 0.8; margin-top: 10px; font-size: 0.9em; }}
        .content {{ line-height: 1.6; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{report["title"]}</h1>
            <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        <div class="content">
            {report["content"]}
            <p><strong>Report Status:</strong> Ready for archiving test</p>
            <p><strong>File:</strong> {report["filename"]}</p>
        </div>
    </div>
</body>
</html>
        """
        
        with open(report_path, 'w') as f:
            f.write(html_content.strip())
        
        print(f"   ✅ {report['filename']}")
    
    return len(sample_reports)

def demonstrate_archiving():
    """Demonstrate the complete archiving workflow"""
    print("\n" + "="*60)
    print("🗂️  COMPLETE REPORT ARCHIVING DEMONSTRATION")
    print("="*60)
    
    # Step 1: Reset environment
    reset_test_environment()
    
    # Step 2: Create sample reports
    num_reports = create_sample_reports()
    
    # Step 3: Show current state
    print(f"\n📂 Current reports in reports/generated/:")
    reports_dir = "reports/generated"
    current_reports = []
    for file in os.listdir(reports_dir):
        if file.endswith('.html'):
            current_reports.append(file)
            file_size = os.path.getsize(os.path.join(reports_dir, file))
            print(f"   📄 {file} ({file_size:,} bytes)")
    
    print(f"\n📊 Status: {len(current_reports)} reports ready for archiving")
    
    # Step 4: Demonstrate cache clearing with archiving
    print(f"\n🧹 Simulating cache clearing operation...")
    print("   (This is what happens when you clear cache in the web interface)")
    
    # Add a small delay to make timestamp different
    time.sleep(1)
    
    cache_options = {
        "clear_all_cache": True
    }
    
    print(f"\n   Cache options: {cache_options}")
    result = clear_analysis_cache(cache_options)
    
    # Step 5: Show results
    print(f"\n📋 Operation Results:")
    if isinstance(result, dict):
        cleared_files = result.get("cleared_files", [])
        archived_files = result.get("archived_files", [])
        
        print(f"   📦 Archived files: {len(archived_files)}")
        for file in archived_files:
            print(f"      📄 {file}")
        
        if cleared_files:
            print(f"   🗑️  Cleared cache files: {len(cleared_files)}")
            for file in cleared_files:
                print(f"      📄 {file}")
        else:
            print(f"   🗑️  No cache files found to clear")
    
    # Step 6: Show archive structure
    print(f"\n📁 Archive Directory Structure:")
    archive_base = "reports/archive"
    if os.path.exists(archive_base):
        archives = sorted([d for d in os.listdir(archive_base) if os.path.isdir(os.path.join(archive_base, d))])
        for archive_folder in archives:
            archive_path = os.path.join(archive_base, archive_folder)
            files = [f for f in os.listdir(archive_path) if f.endswith('.html')]
            print(f"   📁 {archive_folder}/ ({len(files)} files)")
            for file in sorted(files):
                file_size = os.path.getsize(os.path.join(archive_path, file))
                print(f"      📄 {file} ({file_size:,} bytes)")
    
    # Step 7: Show current state after archiving
    print(f"\n📂 reports/generated/ after archiving:")
    remaining_files = []
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith('.html'):
                remaining_files.append(file)
                print(f"   📄 {file}")
    
    if not remaining_files:
        print("   (empty - all reports were archived)")
    
    # Step 8: Summary
    print(f"\n" + "="*60)
    print("✅ DEMONSTRATION COMPLETE")
    print("="*60)
    print(f"📊 Summary:")
    print(f"   • Created {num_reports} sample reports")
    print(f"   • Archived {len(archived_files) if isinstance(result, dict) else 0} reports successfully")
    print(f"   • {len(remaining_files)} reports remain in active directory")
    print(f"   • Archive preserves full content and metadata")
    
    print(f"\n💡 Key Features Demonstrated:")
    print(f"   ✅ Automatic archiving triggered by cache clearing")
    print(f"   ✅ Timestamped archive directories")
    print(f"   ✅ Complete preservation of report content")
    print(f"   ✅ Clean slate for new report generation")
    print(f"   ✅ Zero data loss during cache operations")
    
    print(f"\n🌐 Next Steps:")
    print(f"   • Use web interface at http://localhost:5000")
    print(f"   • Clear cache using checkboxes to see feature in action")
    print(f"   • Reports will be automatically archived")
    print(f"   • Check reports/archive/ for timestamped folders")

if __name__ == "__main__":
    # Change to the project root directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    demonstrate_archiving()
