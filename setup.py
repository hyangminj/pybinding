"""
Modern setup.py for pybinding with PEP 517/518 support.

This file is maintained for backward compatibility and editable installs.
The primary build configuration is in pyproject.toml.
"""
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):
    """Extension built using CMake"""

    def __init__(self, name, sourcedir=""):
        super().__init__(name, sources=[])
        self.sourcedir = os.path.abspath(sourcedir)


class CMakeBuild(build_ext):
    """Custom build_ext to build CMake projects"""

    def run(self):
        # Check CMake is available
        try:
            out = subprocess.check_output(["cmake", "--version"])
        except OSError:
            raise RuntimeError(
                "CMake not found. Please install CMake 3.20 or newer.\n"
                "On macOS: brew install cmake\n"
                "On Ubuntu/Debian: sudo apt-get install cmake\n"
                "On Windows: https://cmake.org/download/"
            )

        # Check CMake version
        import re
        from packaging.version import Version

        cmake_version = Version(
            re.search(r"version\s*([\d.]+)", out.decode()).group(1)
        )
        if cmake_version < Version("3.20.0"):
            raise RuntimeError("CMake 3.20 or newer is required")

        for ext in self.extensions:
            self.build_extension(ext)

    def build_extension(self, ext):
        extdir = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))

        # Modern CMake configuration
        cmake_args = [
            f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={extdir}",
            f"-DPYTHON_EXECUTABLE={sys.executable}",
            f"-DCMAKE_BUILD_TYPE={os.environ.get('PB_BUILD_TYPE', 'Release')}",
        ]

        # Build configuration from environment variables
        cmake_args.extend([
            f"-DPB_WERROR={os.environ.get('PB_WERROR', 'OFF')}",
            f"-DPB_TESTS={os.environ.get('PB_TESTS', 'OFF')}",
            f"-DPB_NATIVE_SIMD={os.environ.get('PB_NATIVE_SIMD', 'ON')}",
            f"-DPB_MKL={os.environ.get('PB_MKL', 'OFF')}",
            f"-DPB_CUDA={os.environ.get('PB_CUDA', 'OFF')}",
        ])

        build_args = ["--config", os.environ.get("PB_BUILD_TYPE", "Release")]

        # Platform-specific configuration
        if platform.system() == "Windows":
            cmake_args.append(
                f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY_{os.environ.get('PB_BUILD_TYPE', 'Release').upper()}={extdir}"
            )
            cmake_args.append("-A x64" if sys.maxsize > 2**32 else "Win32")
            build_args.extend(["--", "/v:m", "/m"])
        else:
            # Use parallel builds on Unix-like systems
            import multiprocessing

            max_jobs = os.environ.get("CMAKE_BUILD_PARALLEL_LEVEL")
            if not max_jobs:
                # Use 75% of available cores
                max_jobs = max(1, int(multiprocessing.cpu_count() * 0.75))

            build_args.extend(["--", f"-j{max_jobs}"])
            print(f"Building with {max_jobs} parallel jobs")

        # Version injection
        env = os.environ.copy()
        version = self.distribution.get_version()
        env["CXXFLAGS"] = f'{env.get("CXXFLAGS", "")} -DCPB_VERSION=\\"{version}\\"'

        # Build directory
        build_temp = Path(self.build_temp)
        build_temp.mkdir(parents=True, exist_ok=True)

        def build():
            """Execute CMake configure and build"""
            print(f"CMake args: {' '.join(cmake_args)}")
            subprocess.check_call(
                ["cmake", ext.sourcedir] + cmake_args, cwd=build_temp, env=env
            )
            subprocess.check_call(
                ["cmake", "--build", "."] + build_args, cwd=build_temp
            )

        try:
            build()
        except subprocess.CalledProcessError as e:
            # If build fails, try cleaning build cache and retry
            print("Build failed, cleaning build cache and retrying...")
            shutil.rmtree(build_temp, ignore_errors=True)
            build_temp.mkdir(parents=True, exist_ok=True)
            try:
                build()
            except subprocess.CalledProcessError:
                print("\n" + "=" * 60)
                print("Build failed. Common solutions:")
                print("1. Ensure you have a C++17 compatible compiler")
                print("2. Update CMake: pip install --upgrade cmake")
                print("3. Check build logs above for specific errors")
                print("4. Set environment variables for custom configuration:")
                print("   PB_BUILD_TYPE=Debug pip install -e .")
                print("=" * 60 + "\n")
                raise


def get_version():
    """Read version from __about__.py"""
    about = {}
    here = Path(__file__).parent
    with open(here / "pybinding" / "__about__.py", encoding="utf-8") as f:
        exec(f.read(), about)
    return about["__version__"]


def get_long_description():
    """Read README and latest changelog"""
    here = Path(__file__).parent

    readme = ""
    if (here / "readme.md").exists():
        with open(here / "readme.md", encoding="utf-8") as f:
            readme = f.read()

    changelog = ""
    if (here / "changelog.md").exists():
        with open(here / "changelog.md", encoding="utf-8") as f:
            content = f.read()
            # Extract latest version from changelog
            import re
            match = re.search(r"## ([\s\S]*?)\n##\s", content)
            if match:
                changelog = match.group(1)

    return f"{readme}\n\n## Latest Changes\n\n{changelog}" if changelog else readme


if __name__ == "__main__":
    # Only run setup if not building with pyproject.toml
    # (pyproject.toml is the preferred method)

    setup(
        name="pybinding-hj",
        version=get_version(),
        packages=find_packages(exclude=["cppcore", "cppmodule", "test*"]) + ["pybinding.tests"],
        package_dir={"pybinding.tests": "tests"},
        ext_modules=[CMakeExtension("_pybinding")],
        cmdclass={"build_ext": CMakeBuild},
        include_package_data=True,
        zip_safe=False,
        python_requires=">=3.10",
        install_requires=[
            "numpy>=1.20",
            "scipy>=1.7",
            "matplotlib>=3.3",
            "pytest>=6.0",
        ],
        extras_require={
            "dev": [
                "pytest>=6.0",
                "pytest-cov",
                "black>=22.0",
                "mypy>=0.950",
                "ruff>=0.1.0",
            ],
            "mkl": ["mkl>=2021.0"],
            "docs": ["sphinx>=4.0", "sphinx-rtd-theme"],
        },
        long_description=get_long_description(),
        long_description_content_type="text/markdown",
    )
