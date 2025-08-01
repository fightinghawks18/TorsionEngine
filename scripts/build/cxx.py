from . import vcpkg

import glob
import platform
import shutil
import subprocess

from enum import Enum
from pathlib import Path

from scripts import util
import os

class CXXCompiler(Enum):
    GCC = "gcc"
    CLANG = "clang"
    ANY = "any"

CXXCOMPILER_MAP = {
    CXXCompiler.GCC: [("gcc", "g++")],
    CXXCompiler.CLANG: [("clang", "clang++")]
}

def get_any_compiler(platform: util.Platform) -> tuple[str, str] | None:
    """Looks for any C and C++ compiler available on the system
    
    Returns:
        tuple[str, str]|None: strings of the native C and C++ compilers, or None if not found
    """
    
    compilers = get_c_compilers(CXXCompiler.CLANG)
    if compilers:
        return compilers
    
    compilers = get_c_compilers(CXXCompiler.GCC)
    if compilers:
        return compilers

    return None  # No compiler found

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
        return (c_compiler, cxx_compiler)
    return None

def clean(out_dir: Path):
    """Cleans the cmake folder at the specified directory"""
    if out_dir.exists():
        shutil.rmtree(out_dir)
        print(f"C++ output folder at {out_dir} exists, removing...")

def compile(out_dir: Path, 
                config: util.BuildConfig = util.BuildConfig.DEBUG, 
                compiler: CXXCompiler = CXXCompiler.GCC,
                target_platform: util.Platform = util.Platform.CURRENT,
                target_arch: util.Architecture = util.Architecture.CURRENT) -> bool:
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
    host_platform, host_arch = util.get_host_platform()
    
    # Check if we are cross-compiling
    is_cross_compiling = (target_platform != host_platform) or (target_arch != host_arch)
    
    # Get C and CXX compilers for the compiler type
    if compiler == CXXCompiler.ANY:
        compilers = get_any_compiler(target_platform)
    else:
        compilers = get_c_compilers(compiler)

    if compilers is None:
        print(f"Attempted to search for {compiler.value} c and cxx compilers, failed to find a match. Please install these compilers again, or add them to PATH.")
        return False
    
    c_compiler, cxx_compiler = compilers
    
    # Get CMake output folder
    clean(out_dir)

    out_dir.mkdir(parents=True)
    
    # Configure CMake build
    configure_cmd = [
        "cmake",
        "-G", "Ninja",
        "-S", str(util.CXXSOURCE_FOLDER),
        "-B", str(out_dir),
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
        "--build", str(out_dir),
        "--parallel" # Helps with build times by using all available cores
    ])
    if result.returncode != 0:
        print(f"CMake failed to build project to {out_dir}, {result.stderr}")
        return False
    
    print(f"CMake build succeeded, see: {out_dir}")
    return True

def _get_cross_compile_flags(platform: util.Platform, arch: util.Architecture) -> list[str]:
    """Get CMake flags for cross-compilation"""
    flags: list[str] = []
    
    # Set system name
    if platform == util.Platform.LINUX:
        flags.append("-DCMAKE_SYSTEM_NAME=Linux")
    elif platform == util.Platform.WINDOWS:
        flags.append("-DCMAKE_SYSTEM_NAME=Windows")
    elif platform == util.Platform.MACOS:
        flags.append("-DCMAKE_SYSTEM_NAME=Darwin")
    elif platform == util.Platform.ANDROID:
        flags.append("-DCMAKE_SYSTEM_NAME=Android")
    
    # Set processor architecture
    if arch == util.Architecture.X64:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=x86_64")
    elif arch == util.Architecture.X86:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=i386")
    elif arch == util.Architecture.ARM64:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=aarch64")
    elif arch == util.Architecture.ARM:
        flags.append("-DCMAKE_SYSTEM_PROCESSOR=arm")
    
    return flags

def install(out_dir: Path, to_dir: Path) -> bool:
    """Installs the built cmake project into a directory

    Returns:
        bool: True if the installation succeeded, or False if it didn't
    """
    result = subprocess.run([
        "cmake",
        "--install", str(out_dir),
        "--prefix", str(to_dir)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"CMake failed to install project to {to_dir}, {result.stderr}")
        return False
    print(f"CMake successfully installed project to {to_dir}")
    return True
    