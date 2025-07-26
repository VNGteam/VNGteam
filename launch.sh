#!/bin/bash
# Launch script for Advanced CMD/Script Manager
# This script helps launch the application on Unix-like systems

echo "🚀 Advanced CMD/Script Manager Launcher"
echo "========================================"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python -c "import sys; print(sys.version_info.major)")
    if [ "$PYTHON_VERSION" = "3" ]; then
        PYTHON_CMD="python"
    else
        echo "❌ Error: Python 3 is required but only Python 2 was found"
        exit 1
    fi
else
    echo "❌ Error: Python is not installed or not in PATH"
    exit 1
fi

echo "✅ Using Python: $PYTHON_CMD"

# Check if the main script exists
if [ ! -f "cmd_manager_app.py" ]; then
    echo "❌ Error: cmd_manager_app.py not found in current directory"
    echo "   Make sure you're running this script from the application directory"
    exit 1
fi

# Check if dependencies are installed
echo "🔍 Checking dependencies..."
MISSING_DEPS=0

for module in "tkinter" "requests" "aiohttp"; do
    if ! $PYTHON_CMD -c "import $module" 2>/dev/null; then
        echo "❌ Missing dependency: $module"
        MISSING_DEPS=1
    fi
done

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo "⚠️  Missing dependencies detected!"
    echo "   Run the installation script first: $PYTHON_CMD install.py"
    echo "   Or install manually: pip install -r requirements.txt"
    echo ""
    read -p "❓ Try to install dependencies now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if [ -f "install.py" ]; then
            $PYTHON_CMD install.py
        else
            echo "Installing from requirements.txt..."
            $PYTHON_CMD -m pip install -r requirements.txt
        fi
    else
        echo "👋 Exiting. Please install dependencies and try again."
        exit 1
    fi
fi

echo "✅ All dependencies available"

# Optional: Check for Node.js if user wants to run JS scripts
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js available: $NODE_VERSION"
else
    echo "⚠️  Node.js not found - JavaScript (.js) scripts won't work"
fi

echo ""
echo "🎯 Launching Advanced CMD/Script Manager..."
echo "   To exit, close the application window or press Ctrl+C here"
echo ""

# Launch the application
exec $PYTHON_CMD cmd_manager_app.py "$@"