import json
import sys
import os

def py_to_ipynb(py_filepath, ipynb_filepath):
    with open(py_filepath, 'r') as f:
        lines = f.readlines()

    cells = []
    current_cell_type = 'code'
    current_source = []

    def add_cell():
        nonlocal current_source, current_cell_type
        if current_source:
            if current_cell_type == 'markdown':
                # Remove '# ' prefix from markdown lines
                source = []
                for line in current_source:
                    if line.startswith('# '):
                        source.append(line[2:])
                    elif line.startswith('#\n'):
                        source.append('\n')
                    else:
                        source.append(line)
            else:
                source = current_source
            
            cells.append({
                "cell_type": current_cell_type,
                "metadata": {},
                "source": source,
                **({"execution_count": None, "outputs": []} if current_cell_type == 'code' else {})
            })
            current_source = []

    for line in lines:
        if line.strip() == '# %% [markdown]':
            add_cell()
            current_cell_type = 'markdown'
        elif line.strip() == '# %%':
            add_cell()
            current_cell_type = 'code'
        else:
            current_source.append(line)

    add_cell()

    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    with open(ipynb_filepath, 'w') as f:
        json.dump(notebook, f, indent=1)
    
    print(f"Created {ipynb_filepath}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_notebook.py <input.py> <output.ipynb>")
        sys.exit(1)
    
    py_to_ipynb(sys.argv[1], sys.argv[2])
