#!/usr/bin/env python3
"""
Demo of the report archiving feature
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import clear_analysis_cache

def demo_archiving():
    """Demonstrate the archiving feature"""
    
    print("🗂️  Report Archiving Feature Demo")
    print("=" * 40)
    print()
    
    # Create some sample reports
    reports_dir = "reports/generated"
    os.makedirs(reports_dir, exist_ok=True)
    
    sample_reports = [
        ("bias_report.html", "Bias & Fairness Analysis Report"),
        ("accuracy_report.html", "Accuracy Analysis Report"), 
        ("consistency_report.html", "Consistency Analysis Report"),
        ("robustness_report.html", "Robustness Analysis Report")
    ]
    
    print("📝 Creating sample reports...")
    for filename, title in sample_reports:
        report_path = os.path.join(reports_dir, filename)
        with open(report_path, "w") as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .header {{ background: #f0f0f0; padding: 10px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    <div class="content">
        <p>This is a sample report for demonstration purposes.</p>
        <p>Report type: {filename}</p>
    </div>
</body>
</html>
            """)
        print(f"   ✅ {filename}")
    
    print(f"\n📂 Current reports in {reports_dir}:")
    for file in os.listdir(reports_dir):
        if file.endswith('.html'):
            print(f"   📄 {file}")
    
    print("\n🧹 Simulating cache clearing (which triggers archiving)...")
    print("   This happens automatically when you clear cache in the web interface")
    
    # Simulate cache clearing
    cache_options = {"clear_all_cache": True}
    result = clear_analysis_cache(cache_options)
    
    if isinstance(result, dict):
        cleared = result.get("cleared_files", [])
        archived = result.get("archived_files", [])
        print(f"\n📦 Archived {len(archived)} reports:")
        for file in archived:
            print(f"   📄 {file}")
        
        if cleared:
            print(f"\n🗑️  Cleared {len(cleared)} cache files:")
            for file in cleared:
                print(f"   📄 {file}")
        else:
            print(f"\n🗑️  No cache files found to clear")
    
    # Show archive structure
    archive_dir = "reports/archive"
    print(f"\n📁 Archive directory structure:")
    if os.path.exists(archive_dir):
        for folder in sorted(os.listdir(archive_dir)):
            folder_path = os.path.join(archive_dir, folder)
            if os.path.isdir(folder_path):
                print(f"   📁 {folder}/")
                for file in sorted(os.listdir(folder_path)):
                    print(f"      📄 {file}")
    
    print(f"\n📂 Reports remaining in {reports_dir}:")
    remaining = []
    if os.path.exists(reports_dir):
        for file in os.listdir(reports_dir):
            if file.endswith('.html'):
                remaining.append(file)
                print(f"   📄 {file}")
    
    if not remaining:
        print("   (none - all reports were archived)")
    
    print("\n✅ Demo completed!")
    print()
    print("💡 Key Benefits:")
    print("   • Never lose reports when clearing cache")
    print("   • Timestamped archives for version tracking") 
    print("   • Automatic process - no manual steps required")
    print("   • Clean reports directory for new analyses")

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    demo_archiving()
