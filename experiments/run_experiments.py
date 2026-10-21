
import os
import subprocess
import sys

project_root = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

main_script = os.path.join(
    project_root, "src", "fuzzstop.py"
)

if not os.path.exists(main_script):
    print("Error: src/fuzzstop.py was not found.")
    sys.exit(1)

print("Starting FuzzStop-Lab experiments...")
print("Running the main experiment script.\n")

result = subprocess.run(
    [sys.executable, main_script],
    cwd=project_root
)

if result.returncode != 0:
    print("Experiment failed. Check the error messages above.")
    sys.exit(result.returncode)

print("\nExperiment completed successfully.")
print("Check the results/ directory for CSV files and the graph.")
