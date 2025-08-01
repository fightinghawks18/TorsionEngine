from scripts.build import cs
from scripts.build import cxx
from scripts.build import swig
from scripts.build import vcpkg

import argparse
import shutil
import sys
import time

from pathlib import Path

from scripts import util

def parse_args():
    parser = argparse.ArgumentParser(description="TorsionEngineBuilder")
    parser.add_argument(
        "--compiler",
        choices=["gcc", "clang", "any"],
        default="any",
        help="What tool to compile C++ with")
    parser.add_argument(
        "--config",
        choices=["Debug", "Release"],
        default="Debug",
        help="Build configuration (Debug has debug symbols, while Release has none and is ready for distribution)")
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos", "current"],
        default="current",
        help="The platform to build for")
    parser.add_argument(
        "--arch",
        choices=["x64", "x86", "arm64", "arm86", "current"],
        default="current",
        help="The architecture to build for")
    return parser.parse_args()

def compile():
    args = parse_args() # Parse arguments from cli

    # Get arguments
    build_config = util.BuildConfig(args.config)
    cxx_compiler = cxx.CXXCompiler(args.compiler)

    platform = util.Platform(args.platform)
    arch = util.Architecture(args.arch)

    # Get host platform info
    host_platform, host_arch = util.get_host_platform()

    if arch == util.Architecture.CURRENT:
        arch = host_arch
    if platform == util.Platform.CURRENT:
        platform = host_platform

    vcpkg_triplet = vcpkg.get_vcpkg_triplet(platform, arch)

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
        vcpkg_build_res = vcpkg.build_packages(vcpkg_triplet)
        if not vcpkg_build_res:
            raise AssertionError("Failed to build vcpkg packages...")

        # Compile C++ (C# depends on it)
        print("Compiling C++ components...")
        cxx_compilation_res = cxx.compile(
            util.CXXOUT_FOLDER, 
            build_config, 
            cxx_compiler, 
            platform, 
            arch)
        if not cxx_compilation_res:
            raise AssertionError("Failed to compile C++ components...")

        # Generate C# bindings from C++
        print("Generating C# bindings from C++ components...")
        swig_generation_res = swig.generate_cs_from_swig(util.SWIG_OUT_FOLDER)
        if not swig_generation_res:
            raise AssertionError("Failed to generate C# bindings from C++ components...")
    
        # Compile C#
        print("Compiling C# components...")
        cs_compilation_res = cs.compile(
            util.CSOUT_FOLDER, 
            build_config, 
            platform, 
            arch)
        if not cs_compilation_res:
            raise AssertionError("Failed to compile C# components...")

        # Install C++ to package directory
        print("Installing C++ components...")
        cxx_installation_res = cxx.install(util.CXXOUT_FOLDER, util.PACKAGE_DIRECTORY)
        if not cxx_installation_res:
            raise AssertionError("Failed to install C++ components...")
    
        # Install C# to package directory
        print("Installing C# components...")
        cs_installation_res = cs.install(util.CSOUT_FOLDER, util.PACKAGE_DIRECTORY)
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