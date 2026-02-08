#!/usr/bin/env python
"""
COMPLIANCE MODULE - AUTOMATED DEPLOYMENT VERIFICATION

This script verifies that all compliance module files are present and ready for deployment.
Run this before executing deployment scripts to ensure everything is in place.
"""

import os
import sys
from pathlib import Path

# Define the expected file structure
EXPECTED_FILES = {
    'compliance_module': [
        'apps/compliance/__init__.py',
        'apps/compliance/apps.py',
        'apps/compliance/models.py',
        'apps/compliance/serializers.py',
        'apps/compliance/views.py',
        'apps/compliance/urls.py',
        'apps/compliance/admin.py',
        'apps/compliance/signals.py',
        'apps/compliance/tests.py',
        'apps/compliance/management/__init__.py',
        'apps/compliance/management/commands/__init__.py',
        'apps/compliance/management/commands/generate_compliance_report.py',
        'apps/compliance/management/commands/verify_audit_chain.py',
        'apps/compliance/management/commands/check_compliance_status.py',
    ],
    'documentation': [
        'COMPLIANCE_DOCUMENTATION.md',
        'COMPLIANCE_SETTINGS.md',
        'COMPLIANCE_IMPLEMENTATION_GUIDE.md',
        'COMPLIANCE_SUMMARY.md',
        'COMPLIANCE_QUICK_START.md',
        'README_COMPLIANCE_PHASE4.md',
        'COMPLIANCE_CHECKLIST.md',
        'DEPLOYMENT_READY.md',
        'PHASE_4_COMPLETE.md',
        'DEPLOYMENT_INSTRUCTIONS.md',
        'START_DEPLOYMENT.md',
    ],
    'deployment_scripts': [
        'deploy_compliance.py',
        'deploy_compliance.bat',
        'deploy_compliance.ps1',
    ]
}

def check_file_exists(filepath):
    """Check if a file exists."""
    full_path = Path(filepath)
    return full_path.exists()

def get_file_size(filepath):
    """Get file size in KB."""
    full_path = Path(filepath)
    if full_path.exists():
        size_bytes = full_path.stat().st_size
        return f"{size_bytes / 1024:.1f}KB"
    return "N/A"

def main():
    """Main verification function."""
    print("\n" + "="*70)
    print("  COMPLIANCE MODULE - DEPLOYMENT READINESS VERIFICATION")
    print("="*70)
    
    backend_dir = Path.cwd()
    if backend_dir.name != 'backend':
        print("\n⚠️  WARNING: Not running from 'backend' directory!")
        print(f"   Current: {backend_dir}")
        print("   Expected: c:\\Users\\arama\\Documents\\itsm-system\\backend")
        backend_dir = Path('c:/Users/arama/Documents/itsm-system/backend')
    
    all_good = True
    file_count = 0
    total_size = 0
    
    for category, files in EXPECTED_FILES.items():
        print(f"\n📁 {category.upper().replace('_', ' ')}")
        print("-" * 70)
        
        category_good = True
        category_files = 0
        category_size = 0
        
        for file_path in files:
            full_path = backend_dir / file_path
            exists = check_file_exists(full_path)
            size = get_file_size(full_path)
            
            status = "✅ OK" if exists else "❌ MISSING"
            print(f"  {status}  {file_path:<50} {size:>8}")
            
            if exists:
                category_files += 1
                if size != "N/A":
                    try:
                        total_size += int(float(size.replace("KB", "")) * 1024)
                    except:
                        pass
            else:
                category_good = False
                all_good = False
            
            file_count += 1
        
        status_text = f"✅ {category_files}/{len(files)} files present"
        if not category_good:
            status_text = f"❌ {len(files) - category_files} files missing"
        print(f"\n  Status: {status_text}")
    
    # Summary
    print("\n" + "="*70)
    print("  DEPLOYMENT READINESS SUMMARY")
    print("="*70)
    
    print(f"\n📊 Statistics:")
    print(f"  Total files expected: {file_count}")
    print(f"  Total files found: {len([f for cat in EXPECTED_FILES.values() for _ in f if check_file_exists(backend_dir / _)])}")
    print(f"  Total size: {total_size / 1024 / 1024:.1f}MB")
    
    print(f"\n🎯 Status: {'✅ READY FOR DEPLOYMENT' if all_good else '❌ MISSING FILES - FIX BEFORE DEPLOYMENT'}")
    
    # Deployment instructions
    if all_good:
        print("\n" + "="*70)
        print("  NEXT STEPS - CHOOSE ONE DEPLOYMENT METHOD")
        print("="*70)
        
        print("\n🚀 Option 1: PowerShell (Recommended for Windows)")
        print("   Command: .\\deploy_compliance.ps1")
        print("   Location: c:\\Users\\arama\\Documents\\itsm-system\\backend")
        
        print("\n🚀 Option 2: Batch File (Command Prompt)")
        print("   Command: deploy_compliance.bat")
        print("   Location: c:\\Users\\arama\\Documents\\itsm-system\\backend")
        
        print("\n🚀 Option 3: Python Script (Cross-platform)")
        print("   Command: python deploy_compliance.py")
        print("   Location: c:\\Users\\arama\\Documents\\itsm-system\\backend")
        
        print("\n🚀 Option 4: Manual Steps")
        print("   1. python manage.py makemigrations compliance")
        print("   2. python manage.py migrate compliance")
        print("   3. python manage.py test apps.compliance.tests")
        print("   4. python manage.py runserver")
        
        print("\n📚 Documentation:")
        print("   - Quick Start: COMPLIANCE_QUICK_START.md")
        print("   - Full Guide: COMPLIANCE_IMPLEMENTATION_GUIDE.md")
        print("   - Deployment: DEPLOYMENT_INSTRUCTIONS.md")
        print("   - Start Here: START_DEPLOYMENT.md ⭐")
        
        print("\n" + "="*70)
        return 0
    else:
        print("\n❌ Please ensure all files are created before deploying.")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
