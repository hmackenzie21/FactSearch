import subprocess
import sys
import time
import os
import platform

def run_command(cmd):
    try:
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        return False

def check_installed(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

print("\nFactSearch Setup\n")

# checking Docker
if not check_installed("docker --version"):
    print("Error: Docker is not installed")
    print("Install Docker Desktop from: https://docs.docker.com/get-docker/")
    sys.exit(1)

# check docker compose  
if not check_installed("docker compose version"):
    print("Error: Docker Compose is not installed - check Docker Desktop installed")
    sys.exit(1)

print("Creating virtual environment...")
if not os.path.exists(".venv"):
    run_command(f"{sys.executable} -m venv .venv")

# get pip path
if platform.system() == "Windows":
    pip = ".venv\\Scripts\\pip"
else:
    pip = ".venv/bin/pip"

# install dependencies
print("Installing Python packages...")
run_command(f"{pip} install --upgrade pip --quiet")
run_command(f"{pip} install -r requirements.txt")

print("Starting SearXNG...")
run_command("docker compose up -d")

print("Waiting for SearXNG to start...")
time.sleep(10)

# check ollama
if check_installed("ollama --version"):
    print("Found Ollama")
    result = subprocess.run("ollama list", shell=True, capture_output=True, text=True)
    if "qwen3:1.7b" not in result.stdout:
        print("qwen3:1.7 not found! Install using ollama to use local model (optional).")

print("\nSetup complete!\n")
print("To run the application:")
if platform.system() == "Windows":
    print("  .venv\\Scripts\\activate")
else:
    print("  source .venv/bin/activate")
print("  streamlit run app.py")
print("\nThen open http://localhost:8501\n")