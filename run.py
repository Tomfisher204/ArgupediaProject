import os
import subprocess
import sys

def run_command(command, cwd=None):
    print(f"\nRunning: {command}")
    subprocess.run(command, shell=True, check=True, cwd=cwd)

def main():
    if not os.path.exists("venv"):
        run_command(f"{sys.executable} -m venv venv")
    if os.name == "nt":
        python_path = os.path.join("venv", "Scripts", "python")
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:
        python_path = os.path.join("venv", "bin", "python")
        pip_path = os.path.join("venv", "bin", "pip")
    run_command(f"{pip_path} install -r requirements.txt")
    run_command(f"{python_path} manage.py migrate")
    run_command(f"{python_path} manage.py unseed")
    run_command(f"{python_path} manage.py seed")
    run_command("npm install", cwd="frontend")
    print("\nStarting backend and frontend...\n")
    backend = subprocess.Popen(f"{python_path} manage.py runserver", shell=True)
    frontend = subprocess.Popen("npm start", shell=True, cwd="frontend")
    backend.wait()
    frontend.wait()

if __name__ == "__main__":
    main()