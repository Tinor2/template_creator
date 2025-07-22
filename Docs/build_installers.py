#!/usr/bin/env python3
"""
Build installers for Windows and macOS
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def create_macos_dmg():
    """Create a DMG file for macOS"""
    print("\n=== Creating macOS DMG ===")
    
    # Create DMG build directory
    dmg_dir = Path("dist/dmg")
    dmg_dir.mkdir(parents=True, exist_ok=True)
    
    # Find the app in the dist directory
    app_src = None
    for root, dirs, _ in os.walk("dist"):
        if "TemplateEditor.app" in dirs:
            app_src = os.path.join(root, "TemplateEditor.app")
            break
    
    if not app_src or not os.path.exists(app_src):
        print("❌ Error: Could not find TemplateEditor.app in dist directory")
        print("Please build the app first using build.py")
        return
    
    app_dest = dmg_dir / "TemplateEditor.app"
    
    if app_dest.exists():
        shutil.rmtree(app_dest)
    
    print(f"Copying {app_src} to {app_dest}")
    shutil.copytree(app_src, app_dest)
    
    # Create Applications symlink
    (dmg_dir / "Applications").symlink_to("/Applications")
    
    # Create background image directory
    bg_dir = dmg_dir / ".background"
    bg_dir.mkdir(exist_ok=True)
    
    # Create DMG using hdiutil
    dmg_path = "dist/TemplateEditor.dmg"
    if os.path.exists(dmg_path):
        os.remove(dmg_path)
    
    print("Creating DMG file...")
    try:
        subprocess.run([
            "hdiutil", "create",
            "-volname", "Template Editor",
            "-srcfolder", str(dmg_dir),
            "-ov", "-format", "UDZO",
            "-fs", "HFS+",
            dmg_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create DMG: {e}")
        print("Make sure you have hdiutil installed (comes with macOS)")
        return
    
    print(f"✅ DMG created at: {dmg_path}")

def create_windows_installer():
    """Create a Windows installer using Inno Setup"""
    print("\n=== Creating Windows Installer ===")
    
    # Check if Inno Setup is installed
    try:
        subprocess.run(["iscc", "/?"], 
                      capture_output=True, 
                      check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Inno Setup is not installed. Please install it from:")
        print("   https://jrsoftware.org/isdl.php")
        print("Skipping Windows installer creation.")
        return
    
    # Create Windows build directory
    win_dir = Path("dist/win")
    win_dir.mkdir(parents=True, exist_ok=True)
    
    # Create an Inno Setup script
    iss_path = "build/windows_installer.iss"
    os.makedirs(os.path.dirname(iss_path), exist_ok=True)
    
    with open(iss_path, "w", encoding="utf-8") as f:
        f.write("""
#define MyAppName "Template Editor"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "TemplateEditor.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-47H8-99I0-J1K2L3M4N5O6}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={{autopf}}\\{#MyAppName}
DisableProgramGroupPage=yes
OutputDir=../dist
OutputBaseFilename=TemplateEditor_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "../dist_package/TemplateEditor_windowsEXE"; DestDir: "{app}"; Flags: ignoreversion
Source: "../dist_package/*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
""")
    
    # Build the installer
    print("Building Windows installer...")
    subprocess.run(["iscc", iss_path], check=True)
    
    print("✅ Windows installer created at: dist/TemplateEditor_Setup.exe")

def main():
    """Main function"""
    # Ensure dist directory exists
    os.makedirs("dist", exist_ok=True)
    
    # Build for current platform
    if sys.platform == 'darwin':
        create_macos_dmg()
    elif sys.platform == 'win32':
        create_windows_installer()
    else:
        print("Unsupported platform. Please run on macOS or Windows.")
        return 1
    
    print("\n🎉 Installer creation complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
