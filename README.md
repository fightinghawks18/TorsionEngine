CURRENTLY, THIS PROJECT IS NOT PRODUCTION READY

# Building

If you don't know how to add stuff to your path please refer to these links based on your system.

* Windows - https://learn.microsoft.com/en-us/windows/win32/procthread/environment-variables
* MacOS/Linux - https://www.gnu.org/software/bash/manual/bash.html#Shell-Variables

## To be able to compile this project you'll need a few things installed on your system and in your path
* *OPTIONAL* **Make** - Methods vary, check below (Helps with quicker building, instead of calling python3 -m to.scripts --release, you can call make all in terminal, view Makefile for other commands)
    * Windows - https://gnuwin32.sourceforge.net/packages/make.htm
    * Linux - sudo apt install make (Make may be already on your distro by default)
    * MacOS - xcode-select --install
* **Python3** - https://www.python.org/downloads/ (Needed to build the system)
* **Vcpkg** [C++ Package Manager] - https://learn.microsoft.com/en-us/vcpkg/get_started/get-started?pivots=shell-powershell
* **CMake** [C++ Build System] - https://cmake.org/download/
* **.NET** [Cross-Platform C# Platform] - https://dotnet.microsoft.com/en-us/download
* **SWIG** [Simplified Wrapper and Interface Generator] - https://www.swig.org/download.html (Needed for C++ -> C#, check the unix note below the windows installation)

After installing all required libraries, you can now run `make all` if you installed Make, or `python3 -m scripts.compile` if you wanna use Python instead.

## Commands For Make
* **Build the project** `make build` *aka `make all`*

## Arguments for Python
* **Build configuration** `--config`
    * The build type you are using
    * Choices: Debug, Release
    * Default: Debug
* **Build platform** `--platform`
    * The platform you are building for
    * Choices: windows, linux, macos
    * Default: **Your current platform**
* **Build architecture** `--arch`
    * The architecture you are building for
    * Choices: x64, x86 *[32-bit]*, arm64, arm
    * Default: **Your current architecture**
* **C++ compiler** `--compiler`
    * The compiler you wanna use for c++
        * *You must install the compiler you wanna use if it's not native to your system*
    * Choices: msvc, gcc, clang
    * Default: **Your platform's native compiler** [e.g. Windows uses MSVC]

## Arguments for Make (Refer to Python)
* **Build configuration** `CONFIG=`
* **Build platform** `PLATFORM=`
* **Build architecture** `ARCH=`
* **C++ compiler** `COMPILER=`