import os
import subprocess

PY_FILE = "src/pluto_control/__main__.py"

if not os.path.isfile(PY_FILE):
    open(PY_FILE, "w").close()

command = f" pyinstaller --name=pluto_control --onefile {PY_FILE} --distpath build/dist/windows"
result = subprocess.call(command, shell=True)

if result != 0:
    print("Error generating .exe ")
    exit(1)
else:
    print("exe file generated successfully")
