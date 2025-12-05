import subprocess
import sys
import os

def generate_requirements(output_file="requirements.txt"):
    """Generate requirements.txt dynamically from installed packages."""

    try:
        print("📦 Detecting installed packages...")

        # Run pip freeze
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            capture_output=True,
            text=True,
            check=True
        )

        packages = result.stdout.strip()

        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(packages)

        print(f"✅ requirements.txt generated successfully at: {os.path.abspath(output_file)}")

    except subprocess.CalledProcessError as e:
        print("❌ Error running pip freeze:", e)

if __name__ == "__main__":
    generate_requirements()
