import os
import subprocess

command = f"mkdocs build --strict --verbose --site-dir build/docs"
result = subprocess.call(command, shell=True)

if result != 0:
    print("Error generating docs ")
    exit(1)
else:
    print("docs file generated successfully")
