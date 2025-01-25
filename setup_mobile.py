import os
import sys
import subprocess
import requests
import zipfile
import platform

def install_requirements():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def install_appium():
    """Install Appium using npm"""
    try:
        print("Installing Appium...")
        subprocess.check_call(["npm", "install", "-g", "appium"])
        subprocess.check_call(["npm", "install", "-g", "appium-doctor"])
        print("Appium installed successfully")
    except Exception as e:
        print(f"Error installing Appium: {str(e)}")
        print("Please install Node.js from https://nodejs.org/ and try again")
        sys.exit(1)

def download_chromedriver():
    """Download appropriate ChromeDriver"""
    try:
        print("Downloading ChromeDriver...")
        # Get latest ChromeDriver version
        response = requests.get("https://chromedriver.storage.googleapis.com/LATEST_RELEASE")
        version = response.text.strip()
        
        # Determine platform
        if platform.system() == "Windows":
            platform_name = "win32"
        elif platform.system() == "Linux":
            platform_name = "linux64"
        else:
            platform_name = "mac64"
            
        # Download ChromeDriver
        url = f"https://chromedriver.storage.googleapis.com/{version}/chromedriver_{platform_name}.zip"
        response = requests.get(url)
        
        # Save and extract
        with open("chromedriver.zip", "wb") as f:
            f.write(response.content)
            
        with zipfile.ZipFile("chromedriver.zip", "r") as zip_ref:
            zip_ref.extractall(".")
            
        # Make executable on Unix systems
        if platform.system() != "Windows":
            os.chmod("chromedriver", 0o755)
            
        # Clean up
        os.remove("chromedriver.zip")
        print("ChromeDriver downloaded successfully")
    except Exception as e:
        print(f"Error downloading ChromeDriver: {str(e)}")
        sys.exit(1)

def setup_appium_server():
    """Configure Appium server"""
    try:
        print("Configuring Appium server...")
        # Create default capabilities file
        capabilities = {
            "platformName": "Android",
            "automationName": "UiAutomator2",
            "browserName": "Chrome",
            "noReset": True
        }
        
        # Save capabilities
        with open("appium_capabilities.json", "w") as f:
            import json
            json.dump(capabilities, f, indent=2)
            
        print("Appium server configured successfully")
    except Exception as e:
        print(f"Error configuring Appium server: {str(e)}")
        sys.exit(1)

def main():
    print("Setting up mobile testing environment...")
    
    # Install Python dependencies
    install_requirements()
    
    # Install Appium (if npm is available)
    try:
        subprocess.check_call(["npm", "--version"])
        install_appium()
    except:
        print("Node.js/npm not found. Please install from https://nodejs.org/")
        print("After installing Node.js, run: npm install -g appium appium-doctor")
    
    # Download ChromeDriver
    download_chromedriver()
    
    # Setup Appium server
    setup_appium_server()
    
    print("\nSetup completed!")
    print("\nTo start testing:")
    print("1. Connect your Android phone via USB")
    print("2. Enable USB debugging in Developer options")
    print("3. Run: appium")
    print("4. In another terminal, run: python mobile_test.py")

if __name__ == "__main__":
    main() 