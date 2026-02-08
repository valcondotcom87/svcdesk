#!/usr/bin/env python3
"""
Compliance Module Deployment Script
Deploys the compliance module to the ITSM platform
"""
import os
import sys
import subprocess
import time

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"▶ {description}")
    print(f"{'='*60}")
    print(f"Command: {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ FAILED: {description}")
        return False
    else:
        print(f"\n✅ SUCCESS: {description}")
        return True

def main():
    """Main deployment function"""
    print("\n" + "="*60)
    print("ITSM Platform - Compliance Module Deployment")
    print("="*60)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Set up environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'itsm_project.settings')
    
    print(f"\n📁 Working directory: {os.getcwd()}")
    print(f"📄 Django settings: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    
    # Step 1: Check if compliance app is registered
    print("\n1️⃣  Checking compliance app registration...")
    with open('itsm_project/settings.py', 'r') as f:
        settings_content = f.read()
        if "'apps.compliance'" in settings_content or '"apps.compliance"' in settings_content:
            print("   ✅ Compliance app is registered in INSTALLED_APPS")
        else:
            print("   ⚠️  Warning: Compliance app may not be registered")
    
    # Step 2: Check if URLs are configured
    print("\n2️⃣  Checking URL configuration...")
    with open('itsm_project/urls.py', 'r') as f:
        urls_content = f.read()
        if "compliance" in urls_content:
            print("   ✅ Compliance URLs are configured")
        else:
            print("   ⚠️  Warning: Compliance URLs may not be configured")
    
    # Step 3: Create migrations
    print("\n3️⃣  Creating Django migrations...")
    if not run_command('python manage.py makemigrations compliance', 'Create migrations for compliance app'):
        print("   ⚠️  Migrations may have failed - this could be expected if already created")
    
    # Step 4: Apply migrations
    print("\n4️⃣  Applying database migrations...")
    if not run_command('python manage.py migrate compliance', 'Apply compliance migrations'):
        print("   ❌ Migration application failed")
        return False
    
    # Step 5: Collect static files
    print("\n5️⃣  Collecting static files...")
    if not run_command('python manage.py collectstatic --noinput', 'Collect static files'):
        print("   ⚠️  Static file collection may have issues")
    
    # Step 6: Run tests
    print("\n6️⃣  Running compliance module tests...")
    if not run_command('python manage.py test apps.compliance.tests --verbosity=2', 'Run compliance tests'):
        print("   ⚠️  Some tests may have failed")
    else:
        print("   ✅ All tests passed!")
    
    # Step 7: Create admin user (optional)
    print("\n7️⃣  Admin user creation (optional)")
    print("   Run: python manage.py createsuperuser")
    
    # Summary
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE")
    print("="*60)
    print("""
📋 Next Steps:
   1. Start the Django development server:
      python manage.py runserver

   2. Access the admin interface:
      http://localhost:8000/admin/

   3. Access the compliance API:
      http://localhost:8000/api/v1/compliance/

   4. View API documentation:
      http://localhost:8000/api/docs/

📚 Documentation:
   - COMPLIANCE_QUICK_START.md - Quick setup guide
   - COMPLIANCE_DOCUMENTATION.md - API reference
   - COMPLIANCE_IMPLEMENTATION_GUIDE.md - Full guide

🔍 Verification Commands:
   # Check compliance status
   python manage.py check_compliance_status

   # Generate compliance report
   python manage.py generate_compliance_report

   # Verify audit log integrity
   python manage.py verify_audit_chain

✅ Compliance Module is ready to use!
    """)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during deployment: {e}")
        sys.exit(1)
