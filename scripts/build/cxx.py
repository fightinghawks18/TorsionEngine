from . import vcpkg

import platform
import shutil
import subprocess

from enum import Enum
from pathlib import Path

from scripts import util

class CXXBuildConfig(Enum):
    DEBUG = "Debug"
    RELEASE = "Release"

class CXXCompiler(Enum):
    GCC = "gcc"
    CLANG = "clang"
    MSVC = "msvc"

class CXXArchitecture(Enum):
    X64 = "x64"
    X86 = "x86"
    ARM64 = "arm64"
    ARM = "arm"
    NONE = "none"

class CXXPlatform(Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    MACOS = "macos"
    ANDROID = "android"
    NONE = "none"

CXXCOMPILER_MAP = {
    CXXCompiler.GCC: [("gcc", "g++")],
    CXXCompiler.CLANG: [("clang", "clang++")],
    CXXCompiler.MSVC: [("cl", "cl")]
}

def get_c_compilers(compiler: CXXCompiler) -> tuple[Path, Path] | None:
    """Queries for C and C++ compiler executables for the specified compiler

    Args:
        compiler: The compiler enum to check
    
    Returns:
        tuple[Path, Path]|None: paths to the compilers (C compiler Path, C++ compiler path), or None if failed to find both
    """
    
    for c_compiler, cxx_compiler in CXXCOMPILER_MAP[compiler]:
        c_path = shutil.which(c_compiler)
        cxx_path = shutil.which(cxx_compiler)

        if not c_path or not cxx_path:
            continue
        return (Path(c_path), Path(cxx_path))
    return None

def get_host_platform() -> tuple[CXXPlatform, CXXArchitecture]:
    """Get the current host platform and architecture

    Returns:
        tuple[CXXPlatform, CXXArchitecture]: The platform and architecture that this user is on
    """
    system = platform.system().lower()
    machine = platform.machine().lower()
    
    match (system, machine):
        # Linux cases
        case ("linux", "amd64" | "x86_64"):
            return (CXXPlatform.LINUX, CXXArchitecture.X64)
        case ("linux", "arm64" | "aarch64"):
            return (CXXPlatform.LINUX, CXXArchitecture.ARM64)
        case ("linux", "arm"):
            return (CXXPlatform.LINUX, CXXArchitecture.ARM)
        case ("linux", _):
            return (CXXPlatform.LINUX, CXXArchitecture.X64)  # Default for unknown Linux arch
        
        # Windows cases
        case ("windows", "amd64" | "x86_64"):
            return (CXXPlatform.WINDOWS, CXXArchitecture.X64)
        case ("windows", "arm64" | "aarch64"):
            return (CXXPlatform.WINDOWS, CXXArchitecture.ARM64)
        case ("windows", "arm"):
            return (CXXPlatform.WINDOWS, CXXArchitecture.ARM)
        case ("windows", _):
            return (CXXPlatform.WINDOWS, CXXArchitecture.X64)  # Default for unknown Windows arch
        
        # macOS cases
        case ("darwin", "arm64" | "aarch64"):
            return (CXXPlatform.MACOS, CXXArchitecture.ARM64)
        case ("darwin", "amd64" | "x86_64"):
            return (CXXPlatform.MACOS, CXXArchitecture.X64)
        case ("darwin", _):
            return (CXXPlatform.MACOS, CXXArchitecture.X64)  # Default for unknown macOS arch
        
        # Default case for unknown systems
        case _:
            print(f"Warning: Unknown platform {system}-{machine}, defaulting to Linux x64")
            return (CXXPlatform.LINUX, CXXArchitecture.X64)

def clean(out_dir: Path):
    """Cleans the cmake folder at the specified directory"""

    cxxout_dir = out_dir / "cmake"
    if cxxout_dir.exists():
        shutil.rmtree(cxxout_dir)
        print(f"C++ output folder at {cxxout_dir} exists, removing...")

def compile(out_dir: Path, 
                config: CXXBuildConfig = CXXBuildConfig.DEBUG, 
                compiler: CXXCompiler = CXXCompiler.MSVC,
                target_platform: CXXPlatform = CXXPlatform.NONE,
                target_arch: CXXArchitecture = CXXArchitecture.NONE) -> bool:
    """
    Compiles all engine/native code into a out directory for installation

    Args:
        out_dir: The folder to output the compiled files
        config: The build config to use
        compiler: The compiler to use

    Returns:
        bool: True if CMake compilation succeeded, or False if it failed to compile
    """

    # Ensure CMake exists
    cmake = shutil.which("cmake")
    if cmake is None:
        print("CMake cannot be discovered, please install or add it to PATH and run this script again.")
        return False
    
    # Get host platform info
    host_platform, host_arch = get_host_platform()

    # Use host platform is we aren't cross compiling (aka no platform is specified)
    if target_platform == CXXPlatform.NONE:
        target_platform = host_platform
    if target_arch == CXXArchitecture.NONE:
        target_arch = host_arch

    # Check if we are cross-compiling
    is_cross_compiling = (target_platform != host_platform) or (target_arch != host_arch)
    
    # Get C and CXX compilers for the compiler type
    compilers = get_c_compilers(compiler)
    if compilers is None:
        print(f"Attempted to search for {compiler.value} c and cxx compilers, failed to find a match. Please install these compilers again, or add them to PATH.")
        return False
    
    c_compiler, cxx_compiler = compilers
    
    # Get CMake output folder
    cxxout_dir = out_dir / "cmake"
    clean(out_dir)

    cxxout_dir.mkdir(parents=True)
    
    # Configure CMake build
    configure_cmd = [
        "cmake",
        "-G", "Ninja",
        "-S", str(util.CXXSOURCE_FOLDER),
        "-B", str(cxxout_dir),
        f"-DCMAKE_BUILD_TYPE={config.value}",
        f"-DCMAKE_C_COMPILER={c_compiler}",
        f"-DCMAKE_CXX_COMPILER={cxx_compiler}"
    ]

    # Only add vcpkg toolchain if it exists
    toolchain = vcpkg.get_toolchain_file()
    if toolchain:
        configure_cmd.append(f"-DCMAKE_TOOLCHAIN_FILE={toolchain}")
        print(f"Using vcpkg toolchain: {toolchain}")

    # Add cross compilation flags if we are compiling to a different platform/architecture
    if is_cross_compiling:
        print(f"Cross-compiling: {host_platform.value}-{host_arch.value} → {target_platform.value}-{target_arch.value}")
        configure_cmd.extend(_get_cross_compile_flags(target_platform, target_arch))
    else:
        print(f"Building for host platform: {target_platform.value}-{target_arch.value}")

    print("Configuring CMake...")
    result = subprocess.run(configure_cmd)
    if result.returncode != 0:
        print(f"CMake failed to configure the project: {result.stderr}")
        return False
    
    print("CMake successfully configured the project")

    # Build CMake project
    print("Building CMake...")
    result = subprocess.run([
        "cmake",
        "--build", str(cxxout_dir),
        "--parallel" # Helps with build times by using all available cores
    ])
    if result.returncode != 0:
        print(f"CMake failed to build project to {cxxout_dir}, {result.stderr}")
        return False
    
    print(f"CMake build succeeded, see: {cxxout_dir}")
    return True

def _get_cross_compile_flags(platform: CXXPlatform, arch: CXXArchitecture) -> list[str]:
    """Get CMake flags for cross-compilation"""
    flags: list[str] = []
    
    # Set system name
    if platform == CXXPlatform.LINUX:
        flags.append("-DCMAKE_SYSTEM_NAME=Linux")
    elif platform == CXXPlatform.WINDOWS:
        flags.append("-DCMAKE_SYSTEM_NAME=Windows")
    elif platform == CXXPlatform.MACOS:
        flags.append("-DCMAKE_SYSTEM_NAME=Darwin")
    elif platform == CXXPlatform.ANDROID:
        flags.append("-DCMAKE_SYSTEM_NAME=Android")
    
    # Set processor architecture
    if arch == CXXArchitecture.X64:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=x86_64")
    elif arch == CXXArchitecture.X86:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=i386")
    elif arch == CXXArchitecture.ARM64:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=aarch64")
    elif arch == CXXArchitecture.ARM:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=arm")
    
    return flags

def install(out_dir: Path, to_dir: Path) -> bool:
    """Installs the built cmake project into a directory

    Returns:
        bool: True if the installation succeeded, or False if it didn't
    """

    cxxout_folder = out_dir / "cmake"

    result = subprocess.run([
        "cmake",
        "--install", str(cxxout_folder),
        "--prefix", str(to_dir)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"CMake failed to install project to {to_dir}, {result.stderr}")
        return False
    print(f"CMake successfully installed project to {to_dir}")
    return True
    