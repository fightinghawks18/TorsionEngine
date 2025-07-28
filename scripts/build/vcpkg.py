import os
import platform
import shutil
import subprocess

from enum import Enum
from pathlib import Path
from scripts.util import Platform, Architecture

from scripts import util

class VTriplet(Enum):
    # Windows triplets
    X64_WINDOWS = "x64-windows"
    X86_WINDOWS = "x86-windows"
    ARM64_WINDOWS = "arm64-windows"
    X64_WINDOWS_STATIC = "x64-windows-static"
    
    # Linux triplets
    X64_LINUX = "x64-linux"
    ARM64_LINUX = "arm64-linux"
    X86_LINUX = "x86-linux"
    
    # macOS triplets
    X64_OSX = "x64-osx"
    ARM64_OSX = "arm64-osx"
    
    # Android triplets
    ARM_ANDROID = "arm-android"
    ARM64_ANDROID = "arm64-android"
    X64_ANDROID = "x64-android"
    
    # Unknown or no selection
    NONE = "none"


def is_vcpkg_available() -> bool:
    """Checks if vcpkg is in PATH

    Returns:
        bool: True if vcpkg is in PATH, or False if it isn't
    """
    return shutil.which("vcpkg") is not None

def get_toolchain_file() -> Path | None:
    """Queries the filesystem for vcpkg's cmake toolchain

    Returns:
        Path | None: The path to the cmake toolchain, or None if it wasn't found
    """

    # Ensure vcpkg exists
    vcpkg = shutil.which("vcpkg")
    if vcpkg == None:
        print("Cannot fetch vcpkg toolchain as it is not added to PATH yet, please install or add it.")
        return None

    # Look for toolchain file from vcpkg path
    vcpkg_folder = Path(vcpkg).parent
    vcpkg_toolchain = vcpkg_folder / "scripts" / "buildsystems" / "vcpkg.cmake"

    if not vcpkg_toolchain.exists():
        print(f"Cannot fetch vcpkg toolchain file since expected path doesn't exist! Path: {vcpkg_toolchain}")
        return None
    return vcpkg_toolchain

def get_host_triplet() -> VTriplet:
    """Get the host triplet for the current build machine

    Note:
        The host triplet is just the current system the user is on, this is useful for cross compilation (I.E: Compiling on Windows for Macintosh)
        
    Returns:
        VTriplet: The user's system triplet
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    match (system, machine):
        case ("windows", "amd64" | "x86_64"):
            return VTriplet.X64_WINDOWS
        case ("windows", "arm64" | "aarch64"):
            return VTriplet.ARM64_WINDOWS
        case ("windows", _):
            return VTriplet.X86_WINDOWS
            
        case ("linux", "amd64" | "x86_64"):
            return VTriplet.X64_LINUX
        case ("linux", "arm64" | "aarch64"):
            return VTriplet.ARM64_LINUX
        case ("linux", _):
            return VTriplet.X86_LINUX
        
        # MacOS
        case ("darwin", "arm64" | "aarch64"):
            return VTriplet.ARM64_OSX
        case ("darwin", _):
            return VTriplet.X64_OSX
            
        # Unknown
        case _:
            print(f"Warning: Unknown platform {system}-{machine}")
            if system == "linux":
                return VTriplet.X64_LINUX
            elif system == "windows":
                return VTriplet.X64_WINDOWS
            elif system == "darwin":
                return VTriplet.X64_OSX
            else:
                print("Defaulting to x64-linux")
                return VTriplet.X64_LINUX

def get_vcpkg_triplet(platform: Platform, arch: Architecture) -> VTriplet:
    print(f"Getting vcpkg triplet from: {platform.value}, {arch.value}")
    match (platform, arch):
        # Windows
        case (Platform.WINDOWS, Architecture.X64):
            return VTriplet.X64_WINDOWS
        case (Platform.WINDOWS, Architecture.X86):
            return VTriplet.X86_WINDOWS
        case (Platform.WINDOWS, Architecture.ARM64):
            return VTriplet.ARM64_WINDOWS
        # Linux
        case (Platform.LINUX, Architecture.X64):
            return VTriplet.X64_LINUX
        case (Platform.LINUX, Architecture.X86):
            return VTriplet.X86_LINUX
        case (Platform.LINUX, Architecture.ARM64):
            return VTriplet.ARM64_LINUX
        # macOS
        case (Platform.MACOS, Architecture.X64):
            return VTriplet.X64_OSX
        case (Platform.MACOS, Architecture.ARM64):
            return VTriplet.ARM64_OSX
        # Android
        case (Platform.ANDROID, Architecture.ARM):
            return VTriplet.ARM_ANDROID
        case (Platform.ANDROID, Architecture.ARM64):
            return VTriplet.ARM64_ANDROID
        case (Platform.ANDROID, Architecture.X64):
            return VTriplet.X64_ANDROID
        # Fallback
        case _:
            return VTriplet.NONE


def build_packages(triplet: VTriplet = VTriplet.NONE) -> bool:
    """Builds vcpkg packages

    Note:
        Downloading packages will automatically use one less cpu core (CPU_CORES - 1), this may be problematic

    Returns:
        bool: True if vcpkg packages installed successfully, or False if it didn't
    """

    # Ensure vcpkg exists
    vcpkg = shutil.which("vcpkg")
    if not vcpkg:
        print("Vcpkg not found in PATH, please install or add it.")
        return False
    
    # Determine triplet to use
    host_triplet = get_host_triplet()
    if triplet == VTriplet.NONE:
        triplet = host_triplet

    cpu_cores = os.cpu_count()
    if cpu_cores is None:
        print("Unable to query cpu cores for vcpkg, defaulting to 1")
        cores_used = 1
    else:
        cores_used = max(1, cpu_cores - 1) # Use one less core

    print(f"Installing vcpkg packages with {cores_used} cores from platform {host_triplet.value} to {triplet.value} platform.")

    # Set env variables to allow parallel builds
    env = os.environ.copy()
    env["VCPKG_MAX_CONCURRENCY"] = str(cores_used)

    # Move to cxx source folder as it has the vcpkg.json

    os.chdir(util.CXXSOURCE_FOLDER)
    
    # Build packages
    vcpkg_cmd = [
        vcpkg, "install",
        f"--triplet={triplet.value}",
        f"--host-triplet={host_triplet.value}"
    ]

    # If we are cross-compiling, allow unsupported packages
    # This ensures we can build packages that aren't supported on host platforms
    if triplet != host_triplet:
        vcpkg_cmd.append("--allow-unsupported")

    result = subprocess.run(vcpkg_cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Failed to build vcpkg packages: {result.stderr}")
        return False
    print("Successfully built vcpkg packages.")
    return True

    
