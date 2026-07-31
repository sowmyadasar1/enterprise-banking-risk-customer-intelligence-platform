import os
import glob
import subprocess
import sys

def main():
    # Directory setup
    eda_src_dir = os.path.dirname(os.path.abspath(__file__))
    notebooks_dir = os.path.abspath(os.path.join(eda_src_dir, '../../../notebooks/eda'))
    create_notebook_script = os.path.abspath(os.path.join(eda_src_dir, '../create_notebook.py'))
    
    os.makedirs(notebooks_dir, exist_ok=True)
    
    # Find all python files in the eda directory (excluding this script)
    py_files = sorted(glob.glob(os.path.join(eda_src_dir, '*.py')))
    py_files = [f for f in py_files if os.path.basename(f) != 'execute_notebooks.py']
    
    print(f"Found {len(py_files)} Python scripts to convert and execute.")
    
    for py_file in py_files:
        basename = os.path.basename(py_file)
        notebook_name = basename.replace('.py', '.ipynb')
        notebook_path = os.path.join(notebooks_dir, notebook_name)
        
        print(f"\n--- Processing {basename} ---")
        
        # 1. Convert to notebook
        print(f"Converting to notebook: {notebook_name}")
        convert_cmd = [sys.executable, create_notebook_script, py_file, notebook_path]
        try:
            subprocess.run(convert_cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error converting {basename}: {e}")
            continue
            
        # 2. Execute notebook in place
        print(f"Executing notebook: {notebook_name}")
        execute_cmd = [
            sys.executable, "-m", "jupyter", "nbconvert", 
            "--to", "notebook", 
            "--execute", 
            "--inplace", 
            notebook_path
        ]
        try:
            subprocess.run(execute_cmd, check=True)
            print(f"Successfully executed {notebook_name}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing {notebook_name}: {e}")

if __name__ == "__main__":
    main()
