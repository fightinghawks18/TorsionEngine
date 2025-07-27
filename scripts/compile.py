from build import cs
from build import cxx
from build import vcpkg

import shutil
import sys
import time

from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
BUILD_DIRECTORY = PROJECT_ROOT / "out"
PACKAGE_DIRECTORY = BUILD_DIRECTORY / "torsion"

def parse_args():
    return NotImplemented

def compile():
    cxx_config = cxx.CXXBuildConfig.DEBUG
    cxx_compiler = cxx.CXXCompiler.MSVC

    cs_config = cs.CSBuildConfig.DEBUG

    start = time.time()

    # Clean build directory
    if BUILD_DIRECTORY.exists():
        print("Cleaning build directory...")
        shutil.rmtree(BUILD_DIRECTORY)
    BUILD_DIRECTORY.mkdir(parents=True)

    did_compilation_succeed = False
    elapsed = 0
    status = "unk"

    # Begin building project
    try:
        # Build vcpkg packages (C++ depends on it, unless they have already been built)
        vcpkg_build_res = vcpkg.build_packages()
        if not vcpkg_build_res:
            raise AssertionError("Failed to build vcpkg packages...")

        # Compile C++ (C# depends on it)
        print("Compiling C++ components...")
        cxx_compilation_res = cxx.compile(BUILD_DIRECTORY, cxx_config, cxx_compiler)
        if not cxx_compilation_res:
            raise AssertionError("Failed to compile C++ components...")

        # TODO: Create swig.py to create easy bindings for C++ -> C#
    
        # Compile C#
        print("Compiling C# components...")
        cs_compilation_res = cs.compile(BUILD_DIRECTORY, cs_config)
        if not cs_compilation_res:
            raise AssertionError("Failed to compile C# components...")

        # Install C++ to package directory
        print("Installing C++ components...")
        cxx_installation_res = cxx.install(BUILD_DIRECTORY, PACKAGE_DIRECTORY)
        if not cxx_installation_res:
            raise AssertionError("Failed to install C++ components...")
    
        # Install C# to package directory
        print("Installing C# components...")
        cs_installation_res = cs.install(BUILD_DIRECTORY, PACKAGE_DIRECTORY)
        if not cs_installation_res:
            raise AssertionError("Failed to install C# components...")
    except AssertionError as err:
        print(f"Torsion failed to finish compilation: {err}")
    else:
        print(f"Torsion successfully compiled project to {BUILD_DIRECTORY} and packaged it into {PACKAGE_DIRECTORY}.")
        did_compilation_succeed = True
    finally:
        elapsed = time.time()-start
        status = did_compilation_succeed and "succeed" or "fail"
    print(f"Torsion compilation time took {elapsed:.2f}s to {status}")

if __name__ == "__main__":
    compile()