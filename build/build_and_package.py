# build_and_package.py
import os
import subprocess
import sys
import shutil
import urllib.request

# -----------------------------
# CONFIGURATION
# -----------------------------
APP_NAME = "ITMS"
MAIN_FILE = "main.py"
EXE_NAME = f"{APP_NAME}.exe"
ICON_FILE = "static/logo.ico"
ARIAL_FONT = r"C:\Windows\Fonts\arial.ttf"
INSTALLER_OUTPUT_DIR = "installer"

VENV = ".venv"
VENV_PYTHON = os.path.join(VENV, "Scripts", "python.exe")
VENV_PIP = os.path.join(VENV, "Scripts", "pip.exe")
VENV_PYINSTALLER = os.path.join(VENV, "Scripts", "pyinstaller.exe")

# -----------------------------
# Helper: Run command safely
# -----------------------------
def run(cmd, check=True):
    print("➡", " ".join(cmd))
    subprocess.run(cmd, check=check)

# -----------------------------
# Step 1: Create virtual environment
# -----------------------------
def create_venv():
    if not os.path.exists(VENV):
        print("🔧 Creating virtual environment...")
        run([sys.executable, "-m", "venv", VENV])
        print("✓ Virtual environment created.\n")
    else:
        print("✓ Virtual environment already exists.\n")

# -----------------------------
# Step 2: Install dependencies
# -----------------------------
def install_dependencies():
    print("📦 Installing dependencies...")
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        sys.exit(1)
    run([VENV_PIP, "install", "--upgrade", "pip"])
    run([VENV_PIP, "install", "-r", "requirements.txt"])
    print("✓ Dependencies installed.\n")

# -----------------------------
# Step 3: Ensure PyInstaller installed
# -----------------------------
def ensure_pyinstaller():
    if not os.path.exists(VENV_PYINSTALLER):
        print("📦 Installing PyInstaller...")
        run([VENV_PIP, "install", "pyinstaller"])
    else:
        print("✓ PyInstaller already installed.\n")

# -----------------------------
# Step 4: Build EXE using PyInstaller (embed python.db)
# -----------------------------
def build_pyinstaller():
    print("🚀 Running PyInstaller...")
    for folder in ("build", "dist"):
        if os.path.exists(folder):
            shutil.rmtree(folder)

    icon_path = os.path.abspath(ICON_FILE)
    if not os.path.exists(icon_path):
        print(f"❌ Icon not found: {icon_path}. Skipping.")
        icon_path = None

    cmd = [
        VENV_PYINSTALLER,
        "--noconfirm",
        "--windowed",
        "--onefile",
        "--name", APP_NAME,
        MAIN_FILE
    ]

    if icon_path:
        cmd.extend(["--icon", icon_path])
        print(f"Using icon: {icon_path}")

    # Add data files/folders (embed python.db inside EXE)
    datas = [
        ("python.db", "."),          # Embed DB
        ("templates", "templates"),
        ("static", "static"),
        ("routes", "routes"),
        ("helpers", "helpers")
    ]
    for src, dest in datas:
        src_path = os.path.abspath(src)
        if os.path.exists(src_path):
            cmd.extend(["--add-data", f"{src_path};{dest}"])
        else:
            print(f"⚠ Missing folder/file: {src}. Will skip.")

    run(cmd)
    print(f"✓ EXE built: dist/{EXE_NAME}\n")

# -----------------------------
# Step 5: Copy additional files (arial.ttf only)
# -----------------------------
def copy_additional_files():
    os.makedirs("dist", exist_ok=True)

    # Copy arial.ttf
    if os.path.exists(ARIAL_FONT):
        shutil.copy(ARIAL_FONT, os.path.join("dist", "arial.ttf"))
        print("✓ Arial.ttf copied.")
    else:
        print("⚠ Arial.ttf not found. Skipping.")

# -----------------------------
# Step 6: Ensure Inno Setup
# -----------------------------
def ensure_innosetup():
    paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]
    for p in paths:
        if os.path.exists(p):
            print("✓ Inno Setup found:", p)
            return p

    print("❌ Inno Setup not found. Installing...")
    installer_url = "https://files.jrsoftware.org/is/6/innosetup-6.2.2.exe"
    installer_path = "innosetup-installer.exe"
    urllib.request.urlretrieve(installer_url, installer_path)
    run([installer_path, "/VERYSILENT", "/NORESTART"])

    for p in paths:
        if os.path.exists(p):
            print("✓ Installed successfully:", p)
            return p

    print("❌ Could not install Inno Setup. Please install manually.")
    sys.exit(1)

# -----------------------------
# Step 7: Generate Inno Setup script dynamically
# -----------------------------
def generate_inno_script():
    os.makedirs(INSTALLER_OUTPUT_DIR, exist_ok=True)
    iss_content = f"""
[Setup]
AppName={APP_NAME}
AppVersion=1.0
DefaultDirName={{pf}}\\{APP_NAME}
DefaultGroupName={APP_NAME}
OutputDir={INSTALLER_OUTPUT_DIR}
OutputBaseFilename={APP_NAME}-setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=static\\logo.ico

[Files]
"""

    sources = [
        (f"dist\\{EXE_NAME}", "{app}"),
        ("dist\\arial.ttf", "{app}"),
        ("dist\\templates\\*", "{app}\\templates"),
        ("dist\\static\\*", "{app}\\static"),
        ("dist\\routes\\*", "{app}\\routes"),
        ("dist\\helpers\\*", "{app}\\helpers"),
    ]

    for src, dest in sources:
        check_src = src.replace("\\*", "")
        if os.path.exists(check_src):
            iss_content += f'Source: "{src}"; DestDir: "{dest}"; Flags: ignoreversion recursesubdirs createallsubdirs\n'
        else:
            print(f"⚠ Skipping missing: {src}")

    iss_content += f"""
[Icons]
Name: "{{group}}\\{APP_NAME}"; Filename: "{{app}}\\{EXE_NAME}"; IconFilename: "static\\logo.ico"
Name: "{{userdesktop}}\\{APP_NAME}"; Filename: "{{app}}\\{EXE_NAME}"; IconFilename: "static\\logo.ico"
"""

    with open("installer.iss", "w", encoding="utf-8") as f:
        f.write(iss_content)

    print("✓ Inno Setup script generated (installer.iss)\n")

# -----------------------------
# Step 8: Build Inno Setup installer
# -----------------------------
def build_innosetup():
    generate_inno_script()
    iscc = ensure_innosetup()
    run([iscc, "installer.iss"])
    print("✓ Installer created in 'installer' folder.\n")

# -----------------------------
# Build activator.exe
# -----------------------------
def build_activator():
    print("🚀 Building activator.exe...")
    activator_file = "activator.py"
    exe_name = "activator.exe"

    if not os.path.exists(activator_file):
        print(f"❌ {activator_file} not found!")
        return

    cmd = [
        VENV_PYINSTALLER,
        "--noconfirm",
        "--onefile",
        "--name", exe_name.replace(".exe", ""),
        activator_file
    ]

    # Include helpers folder
    helpers_path = os.path.abspath("helpers")
    if os.path.exists(helpers_path):
        cmd.extend(["--add-data", f"{helpers_path};helpers"])
    else:
        print("⚠ helpers folder not found. Activator may fail.")

    run(cmd)
    print(f"✓ Activator EXE built: dist/{exe_name}\n")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    print("\n========== ITMS APP BUILDER ==========\n")
    create_venv()
    install_dependencies()
    ensure_pyinstaller()
    build_pyinstaller()
    copy_additional_files()
    build_innosetup()
    build_activator()  # build activator.exe
    print("\n🎉 ALL DONE! Your installer is ready.\n")
