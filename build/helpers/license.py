import os
import hashlib
import uuid
import platform
import subprocess
import sys


# -------------------------------
# 1) GET MACHINE HARDWARE ID
# -------------------------------
def get_cpu_id():
    system = platform.system()

    try:
        if system == "Windows":
            # Use WMIC to get CPU ID
            cmd = "wmic cpu get ProcessorId"
            result = subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
            if result:
                return result

        elif system == "Darwin":  # macOS
            cmd = "ioreg -rd1 -c IOPlatformExpertDevice | grep IOPlatformUUID"
            result = subprocess.check_output(cmd, shell=True).decode()

            cpu_id = result.split('=')[1].replace('"', '').strip()
            return cpu_id

        else:
            # Linux fallback
            return uuid.getnode()

    except:
        return uuid.getnode()  # fallback


def get_disk_serial():
    system = platform.system()

    try:
        if system == "Windows":
            cmd = "wmic diskdrive get SerialNumber"
            result = subprocess.check_output(cmd, shell=True).decode().split("\n")[1].strip()
            return result

        elif system == "Darwin":  # macOS
            cmd = "system_profiler SPStorageDataType | grep 'File System Personality'"
            return uuid.getnode()

    except:
        return str(uuid.getnode())


def get_mac_address():
    return hex(uuid.getnode())


# Combine everything into one machine ID
def generate_machine_id():
    cpu = str(get_cpu_id())
    disk = str(get_disk_serial())
    mac = str(get_mac_address())

    raw = cpu + disk + mac
    return hashlib.sha256(raw.encode()).hexdigest()


# -------------------------------
# 2) STORAGE PATH
# -------------------------------
# -------------------------------
# 2) STORAGE PATH
# -------------------------------
def get_license_file():
    """
    Returns the path where license.dat is stored.
    - For EXE → same folder as executable
    - For Python source → project root folder
    """
    if getattr(sys, "frozen", False):
        # Running as EXE
        app_dir = os.path.dirname(sys.executable)
    else:
        # Running in development from Python
        # Place license.dat in project root (one level up from helpers)
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(app_dir, "license.dat")



# -------------------------------
# 3) ACTIVATE (FIRST TIME)
# -------------------------------
def activate_software():
    machine_id = generate_machine_id()
    license_file = get_license_file()

    with open(license_file, "w") as f:
        f.write(machine_id)

    print("Software activated successfully!")
    print("Machine ID:", machine_id)


# -------------------------------
# 4) VERIFY ON EVERY RUN
# -------------------------------
def verify_license():
    license_file = get_license_file()

    if not os.path.exists(license_file):
        print("❌ License not found. Please activate.")
        return False

    with open(license_file, "r") as f:
        saved_id = f.read().strip()

    current_id = generate_machine_id()

    if saved_id != current_id:
        print("❌ Unauthorized computer detected!")
        return False

    return True
