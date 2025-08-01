import platform

from enum import Enum
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIRECTORY = PROJECT_ROOT / "out"
PACKAGE_DIRECTORY = BUILD_DIRECTORY / "torsion"

# Language-specific folders

# C++
CXXSOURCE_FOLDER = PROJECT_ROOT / "engine" / "native"
CXXOUT_FOLDER = BUILD_DIRECTORY / "cmake"

# C#
CSSOURCE_FOLDER = PROJECT_ROOT / "engine" / "managed"
CSOUT_FOLDER = BUILD_DIRECTORY / ".net"
CSTEMP_OUT_DIR = CSSOURCE_FOLDER / "out"

# SWIG
SWIG_BINDINGS_FOLDER = PROJECT_ROOT / "engine" / "bindings"
SWIG_OUT_FOLDER = PROJECT_ROOT / "swig-gen"

# Enums

class Platform(Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    ANDROID = "android"
    CURRENT = "current"

class BuildConfig(Enum):
    DEBUG = "Debug"
    RELEASE = "Release"

class Architecture(Enum):
    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"
    ARM = "arm"
    CURRENT = "current"

def platform_to_cs_platform(platform: Platform) -> str:
    """Returns a platform based on the enum that works with .NET

    Returns:
        str: The platform name for .NET building
    """
    match platform:
        case Platform.WINDOWS:
            return "win"
        case Platform.MACOS:
            return "osx"
        case _:
            return platform.value

def platform_to_vcpkg_platform(platform: Platform) -> str:
    """Returns a platform based on the enum that works with vcpkg

    Returns:
        str: The platform name for vcpkg packages
    """
    match platform:
        case Platform.MACOS:
            return "osx"
        case _:
            return platform.value

def get_host_platform() -> tuple[Platform, Architecture]:
    """Get the current host platform and architecture

    Returns:
        tuple[Platform, Architecture]: The platform and architecture that this user is on
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    match (system, machine):
        # Linux cases
        case ("linux", "amd64" | "x86_64"):
            return (Platform.LINUX, Architecture.X64)
        case ("linux", "arm64" | "aarch64"):
            return (Platform.LINUX, Architecture.ARM64)
        case ("linux", "arm"):
            return (Platform.LINUX, Architecture.ARM)
        case ("linux", _):
            return (Platform.LINUX, Architecture.X64)  # Default for unknown Linux arch
        
        # Windows cases
        case ("windows", "amd64" | "x86_64"):
            return (Platform.WINDOWS, Architecture.X64)
        case ("windows", "arm64" | "aarch64"):
            return (Platform.WINDOWS, Architecture.ARM64)
        case ("windows", "arm"):
            return (Platform.WINDOWS, Architecture.ARM)
        case ("windows", _):
            return (Platform.WINDOWS, Architecture.X64)  # Default for unknown Windows arch
        
        # macOS cases
        case ("darwin", "arm64" | "aarch64"):
            return (Platform.MACOS, Architecture.ARM64)
        case ("darwin", "amd64" | "x86_64"):
            return (Platform.MACOS, Architecture.X64)
        case ("darwin", _):
            return (Platform.MACOS, Architecture.X64)  # Default for unknown macOS arch
        
        # Default case for unknown systems
        case _:
            print(f"Warning: Unknown platform {system}-{machine}, defaulting to Linux x64")
            return (Platform.LINUX, Architecture.X64)