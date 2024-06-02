import os
import subprocess

UI_FOLDER = "ui"
PY_FOLDER = "src/pluto_control"

# Ensure the output folder exists
os.makedirs(PY_FOLDER, exist_ok=True)

# Compile all .ui files in the designated folder
for ui_file in os.listdir(UI_FOLDER):
    if ui_file.endswith(".ui"):
        ui_file_path = os.path.join(UI_FOLDER, ui_file)
        py_file_name = os.path.splitext(ui_file)[0] + "_ui.py"
        py_file_path = os.path.join(PY_FOLDER, py_file_name)

        # Ensure the .py file exists
        if not os.path.isfile(py_file_path):
            open(py_file_path, "w").close()

        # Compile the .ui file
        command = f"pyuic5 {ui_file_path} -o {py_file_path}"
        result = subprocess.call(command, shell=True)

        if result != 0:
            print(f"Error generating {py_file_path}")
        else:
            print(f"{py_file_path} generated successfully")

print("All UI files processed")
