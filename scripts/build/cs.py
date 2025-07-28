import os
import shutil
import subprocess

from enum import Enum
from pathlib import Path

from scripts import util

class CSBuildConfig(Enum):
    DEBUG = "Debug"
    RELEASE = "Release"


def is_dotnet_available() -> bool:
    """Checks if this system installed .NET

    Returns:
        bool: True if .NET is available, or False if it isn't
    """

    return shutil.which("dotnet") is not None

def clean(out_dir: Path):
    csout_dir = out_dir / "dotnet"
    if csout_dir.exists():
        shutil.rmtree(csout_dir)
        print(f"C# output folder at {csout_dir} exists, removing...")

def compile(out_dir: Path, config: CSBuildConfig = CSBuildConfig.DEBUG) -> bool:
    """Compiles C# solutions (.sln) and outputs into a directory

    Args:
        out_dir: The path to the output directory
        config: The configuration to use for the build (Debug/Release Build)

    Returns:
        bool: True if .NET compilation succeeded, or False if it failed to compile
    """

    # Ensure .NET exists
    dotnet = shutil.which("dotnet")
    if dotnet is None:
        print(f"Failed to start compilation due to .NET SDK not being installed, please install it.")
        return False

    if util.CSTEMP_OUT_DIR.exists():
        shutil.rmtree(util.CSTEMP_OUT_DIR)
    
    # Get out directory
    csout_dir = out_dir / "dotnet"
    clean(out_dir)

    csout_dir.mkdir(parents=True)

    # Get optimal core count
    cpu_cores = os.cpu_count() or 1
    max_cores = max(1, cpu_cores - 1)

    # Get root solution
    solution_file = None
    for file in util.CSSOURCE_FOLDER.iterdir():
        if not file.name.endswith(".sln"):
            continue
        solution_file = file
        break

    if solution_file is None:
        print(f"No solutions (.sln) found in {util.CSSOURCE_FOLDER}, please create one.")
        return False

    print(f"Building C# root solution at {solution_file}")

    # Build project
    result = subprocess.run([
        "dotnet", "publish", str(solution_file),
        "-c", config.value,
        "--self-contained", "false",
        f"-maxcpucount:{max_cores}",
        "--verbosity", "minimal"
    ])

    if result.returncode != 0:
       print(f"Failed to build {solution_file.name}, {result.stderr}")
       return False

    print(f"Successfully built C# project to {csout_dir}")

    return True

def install(out_dir: Path, to_dir: Path) -> bool:
    """Installs all runtime files into a different directory

    Returns:
        bool: True if installation succeeded, or False if it failed
    """

    # Find designated C# output folder
    csout_dir = out_dir / "dotnet"

    # Move all built C# files into C# output folder
    for item in util.CSTEMP_OUT_DIR.iterdir():
        if item.is_file():
            shutil.copy2(item, csout_dir / item.name)
    shutil.rmtree(util.CSTEMP_OUT_DIR) # We don't need it anymore now

    # Ensure the output exists
    if not csout_dir.exists():
        print(f"C# build directory not found! {csout_dir}")
        return False

    # Ensure it's not empty
    if len(os.listdir(csout_dir)) == 0:
        print(f"C# build directory is empty! {csout_dir}")
        return False
    
    # Get bin folder from package directory
    bin_dir = to_dir / "bin"
    if not bin_dir.exists():
        print(f"Packaged directory has no bin folder! {bin_dir}")
        return False

    print(f"Installing C# {csout_dir} -> {bin_dir}")

    # Copy all files from C# output folder to packaged directory
    for item in csout_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, bin_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, bin_dir / item.name)
    print(f"Succeeded in installing C# {csout_dir} -> {bin_dir}")
    return True