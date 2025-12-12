#!/usr/bin/env python3
"""
Streamlit Dependency Fixer Script - UV Compatible
Fixes the rich<14 compatibility issue with streamlit for uv environments
"""

import subprocess
import sys
import json
import os
import platform

def run_command(cmd: str, check: bool = False) -> dict:
    """Run a shell command and return result"""
    print(f"\n{'='*60}")
    print(f"Running: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

def check_environment():
    """Check current environment"""
    print("\nðŸ” Checking Environment...")
    
    # Check if uv is available
    uv_check = run_command("uv --version")
    if uv_check['success']:
        print(f"âœ… Using uv: {uv_check['stdout'].strip()}")
        return 'uv'
    
    # Check if pip is available
    pip_check = run_command("pip --version")
    if pip_check['success']:
        print(f"âœ… Using pip")
        return 'pip'
    
    print("âŒ No package manager found")
    return None

def get_streamlit_info():
    """Get Streamlit information"""
    print("\nðŸ“Š Checking Streamlit Installation...")
    
    # Check if streamlit is installed
    result = run_command("python -c \"import streamlit; print(f'Streamlit version: {streamlit.__version__}')\"")
    if result['success']:
        print(f"âœ… {result['stdout'].strip()}")
        return True
    
    print("âŒ Streamlit not installed or import error")
    print(f"Error: {result.get('stderr', 'Unknown error')}")
    return False

def fix_uv_dependencies():
    """Fix dependencies when using uv"""
    print("\nðŸ”§ Fixing Dependencies with UV...")
    
    # Create a proper pyproject.toml or requirements.txt for uv
    pyproject_content = """[project]
name = "trading-ai-assistant"
version = "1.0.0"
description = "Trading AI Assistant"
requires-python = ">=3.8"

dependencies = [
    "streamlit==1.28.1",
    "rich>=10.14.0,<14",
    "markdown-it-py>=2.2.0",
    "mdurl==0.1.2",
    "pygments<3.0.0,>=2.13.0",
    "openai>=0.27.0",
    "pillow>=9.0.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
    
    with open("pyproject.toml", "w") as f:
        f.write(pyproject_content)
    
    print("âœ… Created pyproject.toml with compatible dependencies")
    
    # Install with uv
    result = run_command("uv pip install -e .")
    if result['success']:
        print("âœ… Dependencies installed successfully with uv")
    else:
        print("âŒ Failed to install with uv")
        print(f"Error: {result.get('stderr', 'Unknown error')}")

def create_streamlit_cloud_config():
    """Create configuration for Streamlit Cloud"""
    print("\nâ˜ï¸ Creating Streamlit Cloud Configuration...")
    
    # Create requirements.txt
    requirements = """# Streamlit Trading AI Assistant - Compatible Requirements
# For Streamlit Cloud Deployment

# Core Framework
streamlit==1.28.1

# Rich Console (must be <14 for Streamlit 1.28 compatibility)
rich>=10.14.0,<14

# Markdown Processing
markdown-it-py>=2.2.0
mdurl==0.1.2  # Fixed version for compatibility

# Syntax Highlighting
pygments>=2.13.0,<3.0.0

# AI Integration
openai>=0.27.0

# Image Processing
pillow>=9.0.0

# Optional: PDF Processing (uncomment if needed)
# pymupdf>=1.23.0

# Development
black>=23.0.0
flake8>=6.0.0
"""
    
    with open("requirements.txt", "w") as f:
        f.write(requirements)
    
    print("âœ… Created requirements.txt for Streamlit Cloud")
    
    # Create packages.txt if needed
    packages = """# System packages for Streamlit Cloud
libgl1-mesa-dev
libglib2.0-0
"""
    
    with open("packages.txt", "w") as f:
        f.write(packages)
    
    print("âœ… Created packages.txt for system dependencies")

def quick_fix_uv():
    """Quick fix for uv environment"""
    print("\nâš¡ Running Quick Fix for UV...")
    
    # Step 1: Check current state
    package_manager = check_environment()
    
    if not package_manager:
        print("âŒ No package manager found")
        return False
    
    # Step 2: Install compatible versions
    if package_manager == 'uv':
        commands = [
            "uv pip install \"streamlit==1.28.1\"",
            "uv pip install \"rich>=10.14.0,<14\"",
            "uv pip install \"markdown-it-py>=2.2.0\"",
            "uv pip install \"mdurl==0.1.2\"",
            "uv pip install \"pygments>=2.13.0,<3.0.0\""
        ]
    else:
        commands = [
            "pip install \"streamlit==1.28.1\"",
            "pip install \"rich>=10.14.0,<14\"",
            "pip install \"markdown-it-py>=2.2.0\"",
            "pip install \"mdurl==0.1.2\"",
            "pip install \"pygments>=2.13.0,<3.0.0\""
        ]
    
    print("\nðŸ“¦ Installing compatible packages...")
    for cmd in commands:
        result = run_command(cmd)
        if not result['success']:
            print(f"âš ï¸  Warning: {cmd} had issues")
            if result.get('stderr'):
                print(f"   Error: {result['stderr'][:200]}...")
    
    # Step 3: Verify
    print("\nâœ… Verification...")
    if get_streamlit_info():
        print("âœ… Streamlit is ready!")
        return True
    else:
        print("âŒ Issues remain")
        return False

def run_streamlit_app():
    """Run the Streamlit app"""
    print("\nðŸš€ Starting Streamlit App...")
    
    # Check if app.py exists
    if not os.path.exists("app.py"):
        print("âŒ app.py not found!")
        return False
    
    print("âœ… Found app.py")
    print("\nStarting Streamlit server...")
    print("The app will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop")
    
    # Run Streamlit
    result = run_command("streamlit run app.py", check=False)
    
    if not result['success']:
        print(f"\nâŒ Streamlit failed to start")
        print(f"Error: {result.get('stderr', 'Unknown error')}")
        return False
    
    return True

def create_minimal_app():
    """Create a minimal test app to verify"""
    minimal_app = """import streamlit as st

st.set_page_config(page_title="Test App", layout="wide")
st.title("âœ… Streamlit Working!")
st.success("If you can see this, Streamlit is working correctly!")

st.header("Dependency Check")
st.code(\"""
import streamlit
import rich
import markdown_it
import mdurl
import pygments

print(f"Streamlit: {streamlit.__version__}")
print(f"Rich: {rich.__version__}")
print(f"Markdown-it-py: {markdown_it.__version__}")
print(f"mdurl: {mdurl.__version__}")
print(f"Pygments: {pygments.__version__}")
\""")

if st.button("Run Check"):
    try:
        import streamlit
        import rich
        import markdown_it
        import mdurl
        import pygments
        
        st.success(f"Streamlit: {streamlit.__version__}")
        st.success(f"Rich: {rich.__version__}")
        st.success(f"Markdown-it-py: {markdown_it.__version__}")
        st.success(f"mdurl: {mdurl.__version__}")
        st.success(f"Pygments: {pygments.__version__}")
    except Exception as e:
        st.error(f"Error: {e}")

st.markdown("---")
st.info("This is a minimal test app to verify dependencies.")
"""
    
    with open("test_app.py", "w") as f:
        f.write(minimal_app)
    
    print("âœ… Created test_app.py")
    return "test_app.py"

def main_menu():
    """Main interactive menu"""
    print("\n" + "="*70)
    print("ðŸ› ï¸  STREAMLIT FIXER - UV EDITION")
    print("="*70)
    print("\nDetected you're using uv package manager")
    print("Streamlit 1.28.1 + rich<14 + mdurl==0.1.2")
    print("="*70)
    
    while True:
        print("\nðŸ“‹ MENU:")
        print("1. Quick Fix (Install compatible versions)")
        print("2. Check Current Installation")
        print("3. Create Streamlit Cloud Config")
        print("4. Run Test App")
        print("5. Run Your Main App")
        print("6. Create Minimal Test App")
        print("7. Exit")
        
        choice = input("\nSelect option (1-7): ").strip()
        
        if choice == '1':
            if quick_fix_uv():
                print("\nâœ… Quick fix completed!")
            else:
                print("\nâŒ Quick fix had issues")
        
        elif choice == '2':
            check_environment()
            get_streamlit_info()
            
            # Check specific packages
            packages = ['rich', 'markdown-it-py', 'mdurl', 'pygments']
            for pkg in packages:
                result = run_command(f"python -c \"import {pkg}; print(f'{pkg}: {pkg.__version__}')\"")
                if result['success']:
                    print(f"âœ… {result['stdout'].strip()}")
                else:
                    print(f"âŒ {pkg}: Not found or error")
        
        elif choice == '3':
            create_streamlit_cloud_config()
            print("\nâœ… Files created for Streamlit Cloud:")
            print("   - requirements.txt")
            print("   - packages.txt")
            print("\nRedeploy on Streamlit Cloud with these files.")
        
        elif choice == '4':
            test_app = create_minimal_app()
            print(f"\nRunning test app: {test_app}")
            run_command(f"streamlit run {test_app}", check=False)
            # Don't wait for it to finish
            break
        
        elif choice == '5':
            if os.path.exists("app.py"):
                print("\nRunning your main app: app.py")
                run_streamlit_app()
                break
            else:
                print("âŒ app.py not found!")
        
        elif choice == '6':
            create_minimal_app()
            print("\nâœ… Created test_app.py")
            print("Run: streamlit run test_app.py")
        
        elif choice == '7':
            print("\nðŸ‘‹ Exiting...")
            break
        
        else:
            print("âŒ Invalid choice")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("ðŸ”§ Streamlit Trading Assistant - Dependency Fixer")
    print("="*70)
    print("\nFrom your logs, I can see:")
    print("âœ… Streamlit 1.28.1 installed")
    print("âš ï¸  mdurl downgraded from 0.1.2 to 0.1.0")
    print("âœ… Using uv package manager")
    print("="*70)
    
    # Check if we have command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--fix':
            quick_fix_uv()
        elif sys.argv[1] == '--test':
            create_minimal_app()
            run_command("streamlit run test_app.py", check=False)
        elif sys.argv[1] == '--cloud':
            create_streamlit_cloud_config()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use: --fix, --test, or --cloud")
    else:
        # Show menu
        main_menu()
    
    print("\n" + "="*70)
    print("ðŸ“‹ Next Steps:")
    print("1. Your main app is at: app.py")
    print("2. Run with: streamlit run app.py")
    print("3. For Streamlit Cloud, use the created requirements.txt")
    print("="*70)
