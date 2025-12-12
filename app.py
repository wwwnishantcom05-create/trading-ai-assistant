#!/usr/bin/env python3
"""
Streamlit Dependency Fixer Script
Fixes the rich<14 compatibility issue with streamlit
Usage: python fix_streamlit_deps.py
"""

import subprocess
import sys
import json
import re
import os
from typing import Optional, List, Dict

def run_command(cmd: str, check: bool = True, capture: bool = True) -> Optional[subprocess.CompletedProcess]:
    """Run a shell command and return result"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        else:
            result = subprocess.run(cmd, shell=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {e}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"Error details: {e.stderr[:500]}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def check_python_environment():
    """Check Python and pip versions"""
    print("\n🔍 Checking Python environment...")
    
    # Python version
    result = run_command("python --version")
    if result and result.stdout:
        print(f"Python: {result.stdout.strip()}")
    
    # Pip version
    result = run_command("pip --version")
    if result and result.stdout:
        pip_version = result.stdout.split()[1]
        print(f"Pip: {pip_version}")
        
        # Check if pip needs update
        if "24.0" in pip_version:
            print("⚠️  Pip is outdated (24.0). Consider updating with: pip install --upgrade pip")

def get_installed_packages() -> Dict[str, str]:
    """Get all installed packages with versions"""
    print("\n📦 Checking installed packages...")
    
    packages = {}
    result = run_command("pip list --format=json")
    
    if result and result.stdout:
        try:
            installed_packages = json.loads(result.stdout)
            for pkg in installed_packages:
                packages[pkg['name'].lower()] = pkg['version']
            
            print(f"Found {len(packages)} installed packages")
            return packages
        except json.JSONDecodeError:
            # Fallback to text parsing
            result = run_command("pip list")
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')[2:]  # Skip headers
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 2:
                        packages[parts[0].lower()] = parts[1]
    
    return packages

def check_dependency_conflicts():
    """Check for specific dependency conflicts"""
    print("\n⚡ Checking for dependency conflicts...")
    
    packages = get_installed_packages()
    
    conflicts = []
    
    # Check streamlit and rich
    streamlit_ver = packages.get('streamlit')
    rich_ver = packages.get('rich')
    
    if streamlit_ver and rich_ver:
        print(f"Streamlit version: {streamlit_ver}")
        print(f"Rich version: {rich_ver}")
        
        # Check if rich version is incompatible
        # Streamlit 1.28.1 requires rich<14
        if rich_ver.startswith('14') and streamlit_ver.startswith('1.28'):
            conflicts.append({
                'package': 'rich',
                'installed': rich_ver,
                'required': '<14',
                'reason': f'Streamlit {streamlit_ver} requires rich<14'
            })
    
    # Check other common conflicts
    for pkg, ver in packages.items():
        if 'markdown-it' in pkg:
            # Check markdown-it-py
            pass
    
    return conflicts

def fix_rich_dependency():
    """Fix the rich dependency to be compatible with streamlit"""
    print("\n🔧 Fixing rich dependency...")
    
    # Option 1: Downgrade rich to compatible version
    print("\n1️⃣ Downgrading rich to compatible version (<14)...")
    
    # First uninstall current rich
    result = run_command("pip uninstall rich -y", check=False)
    
    # Install compatible version
    result = run_command("pip install \"rich<14,>=10.14.0\"")
    
    if result and result.returncode == 0:
        print("✅ Successfully installed compatible rich version")
    else:
        print("❌ Failed to install compatible rich version")
        
        # Try alternative method
        print("\n2️⃣ Trying alternative fix method...")
        result = run_command("pip install \"rich==13.7.0\" --force-reinstall")
        
        if result and result.returncode == 0:
            print("✅ Successfully installed rich 13.7.0")
        else:
            print("❌ Alternative method also failed")

def verify_streamlit_installation():
    """Verify streamlit works correctly"""
    print("\n✅ Verifying Streamlit installation...")
    
    # Check if streamlit can be imported
    test_script = """
import sys
try:
    import streamlit
    print(f"✓ Streamlit version: {streamlit.__version__}")
    
    import rich
    print(f"✓ Rich version: {rich.__version__}")
    
    # Check compatibility
    from packaging import version
    streamlit_ver = version.parse(streamlit.__version__)
    rich_ver = version.parse(rich.__version__)
    
    if streamlit_ver >= version.parse("1.28.0") and rich_ver >= version.parse("14.0.0"):
        print("⚠️  WARNING: Potential compatibility issue detected")
    else:
        print("✓ Compatibility check passed")
        
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
"""
    
    # Write and run test script
    with open("test_import.py", "w") as f:
        f.write(test_script)
    
    result = run_command("python test_import.py", check=False)
    
    # Clean up
    if os.path.exists("test_import.py"):
        os.remove("test_import.py")
    
    return result and result.returncode == 0

def create_compatible_requirements():
    """Create a compatible requirements.txt file"""
    print("\n📝 Creating compatible requirements.txt...")
    
    requirements = """# Compatible Streamlit Trading App Requirements
# Generated by fix script

# Core dependencies
streamlit==1.28.1
rich>=10.14.0,<14  # Must be <14 for Streamlit 1.28 compatibility

# Optional dependencies (uncomment as needed)
# openai>=0.27.0
# pillow>=9.0.0  # For image processing
# pymupdf>=1.23.0  # For PDF processing (install locally)

# Development dependencies
# black>=23.0.0
# flake8>=6.0.0

# To install:
# pip install -r requirements.txt
"""
    
    with open("requirements_fixed.txt", "w") as f:
        f.write(requirements)
    
    print("✅ Created requirements_fixed.txt")
    print("\nTo install all compatible dependencies:")
    print("pip install -r requirements_fixed.txt")

def install_all_compatible():
    """Install all dependencies with compatible versions"""
    print("\n🚀 Installing all compatible dependencies...")
    
    commands = [
        # First upgrade pip
        "pip install --upgrade pip",
        
        # Install streamlit with compatible rich
        "pip install \"streamlit==1.28.1\" \"rich<14,>=10.14.0\"",
        
        # Install markdown-it-py with compatible version
        "pip install \"markdown-it-py>=2.2.0\"",
        
        # Install mdurl
        "pip install \"mdurl==0.1\"",
        
        # Install pygments
        "pip install \"pygments<3.0.0,>=2.13.0\"",
    ]
    
    for cmd in commands:
        result = run_command(cmd, check=False)
        if result and result.returncode != 0:
            print(f"⚠️  Command had issues: {cmd}")
    
    print("\n✅ Installation complete!")

def cleanup_old_installations():
    """Clean up potentially conflicting installations"""
    print("\n🧹 Cleaning up old installations...")
    
    packages_to_check = ['rich', 'markdown-it-py', 'mdurl', 'pygments']
    
    for pkg in packages_to_check:
        print(f"\nChecking {pkg}...")
        result = run_command(f"pip show {pkg}", check=False)
        if result and result.returncode == 0:
            # Package exists, check version
            uninstall = input(f"  Found {pkg}. Force reinstall? (y/n): ")
            if uninstall.lower() == 'y':
                run_command(f"pip uninstall {pkg} -y", check=False)

def interactive_mode():
    """Interactive mode for fixing dependencies"""
    print("\n" + "="*70)
    print("🎯 STREAMLIT DEPENDENCY FIXER")
    print("="*70)
    
    while True:
        print("\n📋 Menu:")
        print("1. Check current environment")
        print("2. Check for conflicts")
        print("3. Fix rich dependency only")
        print("4. Install all compatible dependencies")
        print("5. Create requirements.txt")
        print("6. Clean up old installations")
        print("7. Verify installation")
        print("8. Run all fixes (recommended)")
        print("9. Exit")
        
        choice = input("\nSelect option (1-9): ").strip()
        
        if choice == '1':
            check_python_environment()
            get_installed_packages()
        
        elif choice == '2':
            conflicts = check_dependency_conflicts()
            if conflicts:
                print("\n❌ Found conflicts:")
                for conflict in conflicts:
                    print(f"  - {conflict['package']}: {conflict['installed']} (requires {conflict['required']})")
                    print(f"    Reason: {conflict['reason']}")
            else:
                print("\n✅ No conflicts found!")
        
        elif choice == '3':
            fix_rich_dependency()
        
        elif choice == '4':
            install_all_compatible()
        
        elif choice == '5':
            create_compatible_requirements()
        
        elif choice == '6':
            cleanup_old_installations()
        
        elif choice == '7':
            if verify_streamlit_installation():
                print("\n✅ Streamlit is working correctly!")
            else:
                print("\n❌ There are still issues with Streamlit")
        
        elif choice == '8':
            print("\n🔄 Running comprehensive fix...")
            check_python_environment()
            conflicts = check_dependency_conflicts()
            if conflicts:
                fix_rich_dependency()
            install_all_compatible()
            verify_streamlit_installation()
            create_compatible_requirements()
            print("\n✅ Comprehensive fix complete!")
        
        elif choice == '9':
            print("\n👋 Exiting. Good luck with your trading app!")
            break
        
        else:
            print("❌ Invalid choice. Please select 1-9.")
        
        input("\nPress Enter to continue...")

def quick_fix():
    """Quick one-command fix"""
    print("\n⚡ Running quick fix...")
    
    # Run the most likely fix
    result = run_command("pip install \"streamlit==1.28.1\" \"rich<14,>=10.14.0\" --force-reinstall")
    
    if result and result.returncode == 0:
        print("\n✅ Quick fix successful!")
        
        # Verify
        if verify_streamlit_installation():
            print("✅ Streamlit is now working correctly!")
        else:
            print("⚠️  There might still be issues. Run interactive mode for detailed fixes.")
    else:
        print("\n❌ Quick fix failed. Try interactive mode.")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("🛠️  Streamlit Trading App Dependency Fixer")
    print("="*70)
    print("\nThis script fixes the 'rich' dependency conflict with Streamlit")
    print("Streamlit 1.28.1 requires rich<14, but rich 14.2.0 is installed")
    print("="*70)
    
    # Check if we have command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--quick':
            quick_fix()
        elif sys.argv[1] == '--interactive':
            interactive_mode()
        elif sys.argv[1] == '--check':
            check_python_environment()
            check_dependency_conflicts()
        elif sys.argv[1] == '--help':
            print("\nUsage:")
            print("  python fix_streamlit_deps.py [option]")
            print("\nOptions:")
            print("  --quick       : Run quick one-command fix")
            print("  --interactive : Run interactive mode")
            print("  --check       : Check for conflicts only")
            print("  --help        : Show this help")
            print("\nExamples:")
            print("  python fix_streamlit_deps.py --quick")
            print("  python fix_streamlit_deps.py --interactive")
    else:
        # Default: ask user
        print("\nChoose mode:")
        print("1. Quick fix (recommended)")
        print("2. Interactive mode (more control)")
        print("3. Check only")
        print("4. Exit")
        
        choice = input("\nSelect (1-4): ").strip()
        
        if choice == '1':
            quick_fix()
        elif choice == '2':
            interactive_mode()
        elif choice == '3':
            check_python_environment()
            check_dependency_conflicts()
        elif choice == '4':
            print("Exiting...")
        else:
            print("Invalid choice. Running quick fix...")
            quick_fix()
    
    # Final message
    print("\n" + "="*70)
    print("📋 Next steps:")
    print("1. Run your Streamlit app: streamlit run app.py")
    print("2. If issues persist, run: python fix_streamlit_deps.py --interactive")
    print("3. For production, use: pip install -r requirements_fixed.txt")
    print("="*70)

if __name__ == "__main__":
    main()
