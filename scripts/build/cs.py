import os
import shutil
import subprocess

from enum import Enum
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[3]
CSSOURCE_FOLDER = PROJECT_ROOT / "engine" / "managed"

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
    """Compiles C# files and outputs the built files into a directory

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
    
    # Get out directory
    csout_dir = out_dir / "dotnet"
    clean(out_dir)

    csout_dir.mkdir(parents=True)

    # Find all .csproj files
    csproj_files = list(CSSOURCE_FOLDER.glob("**/*.csproj"))
    if not csproj_files:
        print(f"No .csproj files found in {CSSOURCE_FOLDER}")
        return False

    # Get optimal core count
    cpu_cores = os.cpu_count() or 1
    max_cores = max(1, cpu_cores - 1)

    print(f"Building {len(csproj_files)} C# project{len(csproj_files) > 1 and "s" or ""} with {max_cores} cpu cores")

    # Build project(s)
    current_index = 0
    for csproj in csproj_files:
        print(f"Building {csproj.name}...")

        result = subprocess.run([
            "dotnet", "publish", str(csproj),
            "-c", config.value,
            "-o", str(csout_dir),
            "--self-contained", "false",
            f"-maxcpucount:{max_cores}",
            "--verbosity", "minimal"
        ])

        if result.returncode != 0:
            print(f"Failed to build {csproj.name}, {result.stderr}")
            return False
        print(f"Successfully built {csproj} {current_index+1}/{len(csproj_files)}")
    print(f"Successfully built all C# projects ({len(csproj_files)}) at {csout_dir}")
    return True

def install(out_dir: Path, to_dir: Path) -> bool:
    """Installs all runtime files into a different directory

    Returns:
        bool: True if installation succeeded, or False if it failed
    """

    csout_dir = out_dir / "dotnet"
    if not csout_dir.exists():
        print(f"C# build directory not found: {csout_dir}")
        return False
    
    # Get bin folder
    bin_dir = to_dir / "bin"
    if bin_dir.exists():
        shutil.rmtree(bin_dir)
    bin_dir.mkdir(parents=True)

    print(f"Installing C# {csout_dir} -> {bin_dir}")

    for item in csout_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, bin_dir / item.name)
        elif item.is_dir():
            shutil.copytree(item, bin_dir / item.name)
    print(f"Succeeded in installing C# {csout_dir} -> {bin_dir}")
    return True