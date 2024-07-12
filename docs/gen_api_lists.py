import importlib
import inspect
import os
import sys
import logging
from typing import List, TextIO
import pkgutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
ROOT_MODULE = "celi_framework"
OUTPUT_DIR = "_gen"

# Setup
sys.path.insert(0, os.path.abspath(".."))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def write_class(f: TextIO, module: str, name: str) -> None:
    """
    Write class documentation to the given file object.

    Args:
        f (TextIO): The file object to write to.
        module (str): The module path.
        name (str): The class name.
    """
    f.write(f".. autoclass:: {module}.{name}\n")
    f.write(f"    :members:\n")
    f.write(f"    :undoc-members:\n")
    f.write(f"    :no-index:\n")
    f.write(f"    :show-inheritance:\n")

def write_module_header(f: TextIO, full_module_name: str) -> None:
    """
    Write the module header to the given file object.

    Args:
        f (TextIO): The file object to write to.
        full_module_name (str): The full name of the module.
    """
    underline = "=" * len(full_module_name)
    f.write(f"{full_module_name}\n{underline}\n\n")

def write_module_docstring(f: TextIO, module: object) -> None:
    """
    Write the module's docstring to the given file object.

    Args:
        f (TextIO): The file object to write to.
        module (object): The imported module object.
    """
    if module.__doc__:
        f.write(f"\n{module.__doc__}\n\n")

def process_module_members(f: TextIO, module_path: str, module_name: str, module: object) -> List[str]:
    """
    Process the members of a module and write their documentation.

    Args:
        f (TextIO): The file object to write to.
        module_path (str): The path of the parent module.
        module_name (str): The name of the current module.
        module (object): The imported module object.

    Returns:
        List[str]: A list of submodule names.
    """
    submodules = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and obj.__module__.startswith(ROOT_MODULE):
            f.write(f".. autofunction:: {module_path}.{module_name}.{name}\n")
        elif inspect.isclass(obj) and obj.__module__.startswith(f"{module_path}.{module_name}"):
            write_class(f, f"{module_path}.{module_name}", name)
        elif inspect.ismodule(obj) and obj.__name__.startswith(f"{module_path}.{module_name}"):
            submodules.append(name)
            write_submodule(f"{module_path}.{module_name}", name)
    return submodules

def write_submodules_toc(f: TextIO, file: str, module_name: str, submodules: List[str]) -> None:
    """
    Write the table of contents for submodules.

    Args:
        f (TextIO): The file object to write to.
        file (str): The file path.
        module_name (str): The name of the current module.
        submodules (List[str]): A list of submodule names.
    """
    for name in submodules:
        f.write(f"`{name} <../{file}/{module_name}/{name}>`_\n")
    f.write("\n.. toctree::\n    :hidden:\n\n")
    for name in submodules:
        f.write(f"    ../{file}/{module_name}/{name}\n")



def write_submodule(module_path: str, module_name: str) -> None:
    full_name = f"{module_path}.{module_name}"
    file = module_path.replace(ROOT_MODULE, OUTPUT_DIR).replace(".", os.path.sep)
    os.makedirs(file, exist_ok=True)
    
    output_file = os.path.join(file, f"{module_name}.rst")
    
    try:
        with open(output_file, "w") as f:
            full_module_name = module_name if module_path == ROOT_MODULE else f"{module_path.replace(f'{ROOT_MODULE}.', '')}.{module_name}"
            write_module_header(f, full_module_name)
            
            module = importlib.import_module(full_name)
            write_module_docstring(f, module)
            
            submodules = process_module_members(f, module_path, module_name, module)
            
            # Add this block to handle subpackages
            package = importlib.import_module(full_name)
            for _, submodule_name, ispkg in pkgutil.iter_modules(package.__path__):
                submodule_full_name = f"{full_name}.{submodule_name}"
                if submodule_name not in submodules:
                    submodules.append(submodule_name)
                    write_submodule(full_name, submodule_name)
            
            if submodules:
                write_submodules_toc(f, file, module_name, submodules)
        
        logging.info(f"Generated documentation for {full_name}")
    except Exception as e:
        logging.error(f"Error generating documentation for {full_name}: {str(e)}")
        
import celi_framework

# write_submodule("celi_framework", "main")
# write_submodule("celi_framework", "core")
# write_submodule("celi_framework", "utils")
# write_submodule("celi_framework", "examples")
# write_submodule("celi_framework", "experimental")

def main():
    """Main function to generate documentation for all modules."""
    modules_to_document = ["main", "core", "utils", "examples", "experimental"]
    for module in modules_to_document:
        write_submodule(ROOT_MODULE, module)

if __name__ == "__main__":
    main()