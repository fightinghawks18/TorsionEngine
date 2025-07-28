from scripts.build import cs
from scripts.build import cxx
from scripts.build import swig
from scripts.build import vcpkg

import shutil
import sys
import time

from pathlib import Path

from scripts import util

def parse_args():
    return NotImplemented

def compile():
    cxx_config = cxx.CXXBuildConfig.DEBUG
    cxx_compiler = cxx.CXXCompiler.MSVC

    cs_config = cs.CSBuildConfig.DEBUG

    start = time.time()

    # Clean build directory
    if util.BUILD_DIRECTORY.exists():
        print("Cleaning build directory...")
        shutil.rmtree(util.BUILD_DIRECTORY)
    util.BUILD_DIRECTORY.mkdir(parents=True)

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
        cxx_compilation_res = cxx.compile(util.BUILD_DIRECTORY, cxx_config, cxx_compiler)
        if not cxx_compilation_res:
            raise AssertionError("Failed to compile C++ components...")

        # Generate C# bindings from C++
        print("Generating C# bindings from C++ components...")
        swig_generation_res = swig.generate_cs_from_swig(util.SWIG_OUT_FOLDER)
        if not swig_generation_res:
            raise AssertionError("Failed to generate C# bindings from C++ components...")
    
        # Compile C#
        print("Compiling C# components...")
        cs_compilation_res = cs.compile(util.BUILD_DIRECTORY, cs_config)
        if not cs_compilation_res:
            raise AssertionError("Failed to compile C# components...")

        # Install C++ to package directory
        print("Installing C++ components...")
        cxx_installation_res = cxx.install(util.BUILD_DIRECTORY, util.PACKAGE_DIRECTORY)
        if not cxx_installation_res:
            raise AssertionError("Failed to install C++ components...")
    
        # Install C# to package directory
        print("Installing C# components...")
        cs_installation_res = cs.install(util.BUILD_DIRECTORY, util.PACKAGE_DIRECTORY)
        if not cs_installation_res:
            raise AssertionError("Failed to install C# components...")
    except AssertionError as err:
        print(f"Torsion failed to finish compilation: {err}")
    else:
        print(f"Torsion successfully compiled project to {util.BUILD_DIRECTORY} and packaged it into {util.PACKAGE_DIRECTORY}.")
        did_compilation_succeed = True
    finally:
        elapsed = time.time()-start
        status = did_compilation_succeed and "succeed" or "fail"
    print(f"Torsion compilation time took {elapsed:.2f}s to {status}")

if __name__ == "__main__":
    compile()