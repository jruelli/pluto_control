import os
import subprocess

UI_FILE = "ui/pluto_control.ui"
PY_FILE = "src/pluto_control/pluto_control_ui.py"

if not os.path.isfile(PY_FILE):
    open(PY_FILE, "w").close()

command = f"pyuic5 {UI_FILE} -o {PY_FILE}"
result = subprocess.call(command, shell=True)

if result != 0:
    print("Error generating UI file")
    exit(1)
else:
    print("UI file generated successfully")
