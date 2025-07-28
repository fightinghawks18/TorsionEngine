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
