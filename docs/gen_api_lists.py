import importlib
import inspect

import os
import pkgutil
import sys

sys.path.insert(0, os.path.abspath(".."))

os.makedirs("_gen", exist_ok=True)


def write_class(f, module: str, name: str):
    f.write(f".. autoclass:: {module}.{name}\n")
    f.write(f"   :members:\n")
    f.write(f"   :undoc-members:\n")
    f.write(f"   :show-inheritance:\n")


def write_submodule(module_path: str, module_name: str):
    full_name = f"{module_path}.{module_name}"
    file = module_path.replace("celi_framework", "_gen").replace(".", "/")
    os.makedirs(file, exist_ok=True)
    with open(f"{file}/{module_name}.rst", "w") as f:
        underline = "=" * len(module_name)
        f.write(f"{module_name}\n{underline}\n\n")
        m = importlib.import_module(full_name)
        if m.__doc__:
            f.write(f"\n{m.__doc__}\n\n")
        submodules = []
        for name, obj in inspect.getmembers(m):
            # print(f"Obj is {obj}")
            if inspect.isfunction(obj) and obj.__module__.startswith("celi_framework"):
                f.write(f".. autofunction:: {module_path}.{module_name}.{name}\n")
            elif inspect.isclass(obj) and obj.__module__.startswith(
                f"{module_path}.{module_name}"
            ):
                # print(f"{name} {obj} {obj.__module__} {module_path}.{module_name}\n")
                write_class(f, f"{module_path}.{module_name}", name)
            elif inspect.ismodule(obj) and obj.__name__.startswith(
                f"{module_path}.{module_name}"
            ):
                # print(f"Submodule {module_path}.{module_name}.{name}\n")
                submodules.append(name)

                write_submodule(f"{module_path}.{module_name}", name)
            # else:
            #     print(f"Unknown type: {module_path} {module_name} {name}")
        if len(submodules) > 0:
            for name in submodules:
                f.write(f"`{name} <../{file}/{module_name}/{name}>`_\n")
            f.write("\n.. toctree::\n   :hidden:\n\n")
            for name in submodules:
                f.write(f"   ../{file}/{module_name}/{name}\n")


import celi_framework

write_submodule("celi_framework", "main")
write_submodule("celi_framework", "core")
write_submodule("celi_framework", "utils")
write_submodule("celi_framework", "examples")
write_submodule("celi_framework", "experimental")
