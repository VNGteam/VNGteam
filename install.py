#!/usr/bin/env python3
"""
Installation script for Advanced CMD/Script Manager
This script helps set up the environment and install dependencies.
"""

import sys
import subprocess
import os
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_tkinter():
    """Check if tkinter is available"""
    try:
        import tkinter
        print("✅ Tkinter is available")
        return True
    except ImportError:
        print("❌ Error: Tkinter is not available")
        print("   Install tkinter:")
        if platform.system() == "Linux":
            print("   - Ubuntu/Debian: sudo apt-get install python3-tk")
            print("   - CentOS/RHEL: sudo yum install tkinter")
            print("   - Arch Linux: sudo pacman -S tk")
        elif platform.system() == "Darwin":
            print("   - macOS: brew install python-tk")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    
    requirements = ["requests>=2.25.1", "aiohttp>=3.8.0", "typing_extensions>=4.0.0"]
    
    for package in requirements:
        try:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True

def check_optional_dependencies():
    """Check for optional dependencies (Node.js for JavaScript support)"""
    print("\n🔍 Checking optional dependencies...")
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js is available: {result.stdout.strip()}")
        else:
            print("⚠️  Node.js not found - JavaScript (.js) scripts won't work")
            print("   Install Node.js from: https://nodejs.org/")
    except FileNotFoundError:
        print("⚠️  Node.js not found - JavaScript (.js) scripts won't work")
        print("   Install Node.js from: https://nodejs.org/")

def create_desktop_shortcut():
    """Create desktop shortcut (Windows only)"""
    if platform.system() != "Windows":
        return
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        script_path = os.path.abspath("cmd_manager_app.py")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortcut(os.path.join(desktop, "CMD Manager.lnk"))
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.Description = "Advanced CMD/Script Manager & Cloudflare DNS Updater"
        shortcut.save()
        
        print("✅ Desktop shortcut created")
        
    except ImportError:
        print("⚠️  Desktop shortcut creation requires pywin32 and winshell")
        print("   Install with: pip install pywin32 winshell")
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")

def setup_startup_option():
    """Offer to add to startup (Windows only)"""
    if platform.system() != "Windows":
        return
    
    response = input("\n❓ Add to Windows startup? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        try:
            script_path = os.path.abspath("cmd_manager_app.py")
            subprocess.run([sys.executable, script_path, "--add-startup"], check=True)
            print("✅ Added to Windows startup")
        except Exception as e:
            print(f"❌ Failed to add to startup: {e}")

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test importing main modules
        print("Testing imports...")
        import tkinter
        import requests
        import aiohttp
        print("✅ All imports successful")
        
        # Test creating a simple window
        print("Testing GUI creation...")
        root = tkinter.Tk()
        root.withdraw()  # Hide the window
        root.destroy()
        print("✅ GUI test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed: {e}")
        return False

def main():
    """Main installation function"""
    print("🚀 Advanced CMD/Script Manager Installation")
    print("=" * 50)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    if not check_tkinter():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check optional dependencies
    check_optional_dependencies()
    
    # Test installation
    if not test_installation():
        print("\n❌ Installation test failed. Please check the errors above.")
        sys.exit(1)
    
    print("\n✅ Installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the application: python cmd_manager_app.py")
    print("2. Add your scripts in the Scripts tab")
    print("3. Configure Cloudflare DNS in the Cloudflare tab")
    print("4. Check the logs for any issues")
    
    # Windows-specific options
    if platform.system() == "Windows":
        print("\n🪟 Windows-specific options:")
        create_desktop_shortcut()
        setup_startup_option()
    
    print(f"\n📚 Documentation: README.md")
    print(f"🧪 Test scripts available: test_script.py, test_script.js, test_script.bat")
    
    # Offer to run the application
    response = input("\n❓ Run the application now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        try:
            subprocess.run([sys.executable, "cmd_manager_app.py"])
        except KeyboardInterrupt:
            print("\n👋 Application closed by user")
        except Exception as e:
            print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    main()