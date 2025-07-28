from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
BUILD_DIRECTORY = PROJECT_ROOT / "out"
PACKAGE_DIRECTORY = BUILD_DIRECTORY / "torsion"

# Language-specific folders
CXXSOURCE_FOLDER = PROJECT_ROOT / "engine" / "native"
CSSOURCE_FOLDER = PROJECT_ROOT / "engine" / "managed"
SWIG_BINDINGS_FOLDER = PROJECT_ROOT / "engine" / "bindings"
SWIG_OUT_FOLDER = PROJECT_ROOT / "swig-gen"
CSTEMP_OUT_DIR = CSSOURCE_FOLDER / "out"