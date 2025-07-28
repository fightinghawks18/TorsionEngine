import shutil
import subprocess
from pathlib import Path

from scripts import util

def generate_cs_from_swig(out_dir: Path) -> bool:
    """Generates C# files from SWIG bindings

    Args:
        out_dir: The path where the generated bindings should go

    Returns:
        bool: True if the binding generation succeeded, or False if it failed
    """

    # Ensure SWIG is available on this system
    swig = shutil.which("swig")
    if swig is None:
        print("SWIG is not detected on this system, please install or add it to PATH.")
        return False

    # Iterate through bindings and collect each file
    swig_interfaces: list[Path] = []

    for item in util.SWIG_BINDINGS_FOLDER.rglob("*.i"):
        swig_interfaces.append(item)

    # Clean output directory
    if util.SWIG_OUT_FOLDER.exists():
        shutil.rmtree(util.SWIG_OUT_FOLDER)
    util.SWIG_OUT_FOLDER.mkdir(parents=True)

    successful_generations = 0

    # Iterate through SWIG interfaces and generate C# files
    for interface in swig_interfaces:
        result = subprocess.run([
            "swig",
            "-c++",
            "-csharp",
            "-I" + str(util.CXXSOURCE_FOLDER),
            "-outdir", str(out_dir),
            "-o", str(out_dir / f"{interface.stem}_wrap.cpp"),
            str(interface)
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"SWIG failed to generate C# from interface {interface.name}, {result.stderr}")
            continue
        print(f"Successfully generated C# from interface {interface.name}")
        successful_generations += 1

    if successful_generations == 0: # Check C# generation result
        print("Failed to generate C# files with SWIG")
        return False
    print(f"Generated {successful_generations} C# files, see: {out_dir}")
    return True


        
