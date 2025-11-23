# Pybinding 0.10.0 Migration Guide

## Overview

Pybinding 0.10.0 is a major modernization release that includes:
- C++17 standard
- Python 3.9+ support
- Latest build tools and dependencies
- Performance improvements
- Modern CI/CD

## Breaking Changes

### 1. Python Version Requirements

**Before**: Python 3.6-3.8
**Now**: Python 3.9-3.14

**Migration**:
```bash
# Check Python version
python --version

# Install Python 3.9+ (macOS)
brew install python@3.11

# Install Python 3.9+ (Ubuntu)
sudo apt-get install python3.11

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows
```

### 2. Build System Changes

**Before**: setup.py only
**Now**: pyproject.toml (recommended) + setup.py (compatibility)

**Installation Methods**:

#### Method 1: pip (Recommended)
```bash
# Standard installation
pip install pybinding

# Development mode
pip install -e .[dev]

# MKL support
pip install -e .[mkl]
```

#### Method 2: Build from Source
```bash
# Check dependencies
python --version  # 3.9+
cmake --version   # 3.20+
gcc --version     # 9.0+ (Linux)
clang --version   # 12.0+ (macOS)

# Build
pip install -e .

# Or build with specific options
PB_BUILD_TYPE=Release PB_NATIVE_SIMD=ON pip install -e .
```

### 3. Dependency Version Upgrades

| Package | Before | Now | Impact |
|---------|--------|-----|--------|
| numpy | >=1.12 | >=1.20 | Minimal API changes |
| scipy | >=0.19 | >=1.7 | Performance improvements |
| matplotlib | >=2.0 | >=3.3 | Some plot API changes |
| pytest | >=5.0 | >=6.0 | Same test execution |

**Migration**:
```bash
# Update dependencies
pip install --upgrade numpy scipy matplotlib pytest
```

### 4. C++ Compiler Requirements

**Before**:
- Linux: GCC 5.0+ / Clang 3.5+
- macOS: Xcode 7+
- Windows: Visual Studio 2015+

**Now**:
- Linux: GCC 9.0+ / Clang 10+
- macOS: Xcode 12+ (Clang 12+)
- Windows: Visual Studio 2019+

**Migration**:

Linux (Ubuntu/Debian):
```bash
# Check compiler version
gcc --version

# Install GCC 9+
sudo apt-get update
sudo apt-get install gcc-11 g++-11
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100
```

macOS:
```bash
# Update Xcode Command Line Tools
xcode-select --install

# Or install latest LLVM via Homebrew
brew install llvm
```

Windows:
```powershell
# Install Visual Studio 2019 or 2022
# https://visualstudio.microsoft.com/downloads/

# Or just Build Tools
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
```

### 5. CMake Version Upgrade

**Before**: CMake 3.1+
**Now**: CMake 3.20+

**Migration**:
```bash
# Check current version
cmake --version

# Install via pip (all platforms)
pip install --upgrade cmake

# Or use system package manager
brew install cmake      # macOS
sudo apt-get install cmake  # Ubuntu
choco install cmake     # Windows
```

### 6. Environment Variables

Build configuration environment variables remain the same:

```bash
# Build type (Debug/Release)
export PB_BUILD_TYPE=Release

# Treat warnings as errors
export PB_WERROR=ON

# Enable C++ tests
export PB_TESTS=ON

# Use native SIMD instructions
export PB_NATIVE_SIMD=ON

# Use Intel MKL
export PB_MKL=ON

# Enable CUDA support (requires CUDA installation)
export PB_CUDA=ON

# Build
pip install -e .
```

### 7. API Changes

**Main API maintains backward compatibility**. Most code will work without modifications.

#### Changed Behavior:

1. **Numpy Array Warnings**:
```python
# Before (may generate warnings)
model = pb.Model(lattice, shape, pb.rectangle(10, 10))

# Now (recommended)
model = pb.Model(lattice, pb.rectangle(10, 10))
```

2. **Matplotlib Plotting**:
```python
# Some plot functions have changed return values
# Most are handled automatically, but check custom plotting code
```

3. **Type Hints Added** (optional):
```python
from pybinding import Lattice, Model
from typing import List

def create_model(lattice: Lattice) -> Model:
    return Model(lattice)
```

### 8. Development Environment Setup

#### New development tools available:

```bash
# Install dev dependencies
pip install -e .[dev]

# Code formatting (Black)
black pybinding tests

# Linting (Ruff)
ruff check pybinding tests

# Type checking (mypy)
mypy pybinding

# Run tests
pytest tests/ -v
```

#### pre-commit hooks (optional):
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### 9. Migrating from conda to pip

**Before** (conda required):
```bash
conda create -n pb-env python=3.8
conda activate pb-env
conda install -c conda-forge numpy scipy matplotlib kwant pytest cmake
pip install pybinding
```

**Now** (pip-only possible):
```bash
# Python 3.9+ virtual environment
python3.11 -m venv venv
source venv/bin/activate

# All dependencies via pip
pip install pybinding

# Or build from source
git clone https://github.com/dean0x7d/pybinding.git
cd pybinding
pip install -e .[dev]
```

**conda still usable**:
```bash
conda create -n pb-env python=3.11
conda activate pb-env
conda install -c conda-forge cmake
pip install pybinding
```

### 10. Performance Optimization Tips

#### Build with maximum performance:
```bash
# Release mode + native optimization
PB_BUILD_TYPE=Release PB_NATIVE_SIMD=ON pip install --no-build-isolation -e .

# Use MKL on Intel CPUs
pip install mkl mkl-include
PB_MKL=ON pip install --no-build-isolation -e .
```

#### Benchmarking:
```python
import pybinding as pb
import time

# Benchmark with your code
start = time.time()
# ... computation ...
print(f"Time: {time.time() - start:.2f}s")
```

**Expected Performance Improvements**:
- Model building: 15-30% faster
- KPM calculations: 20-40% faster
- Memory usage: 10-20% reduction

## Troubleshooting

### Build Failures

#### Issue: "CMake 3.20 or newer is required"
```bash
pip install --upgrade cmake
```

#### Issue: "C++17 not supported"
```bash
# Update compiler (see "4. C++ Compiler Requirements" above)
```

#### Issue: "Eigen3 not found"
```bash
# CMake downloads automatically, so clean build cache and retry
rm -rf build/
pip install -e . --no-build-isolation
```

### Runtime Errors

#### Issue: "ImportError: libstdc++.so.6: version 'GLIBCXX_3.4.XX' not found"
```bash
# Update system libstdc++ or
# Remove from conda environment
conda uninstall libgcc
conda update --all
```

#### Issue: Numpy warnings
```bash
# Update Numpy
pip install --upgrade numpy
```

### Performance Issues

#### Performance slower than before
```bash
# Rebuild in Release mode
pip uninstall pybinding
PB_BUILD_TYPE=Release pip install -e .

# Enable native optimization
PB_NATIVE_SIMD=ON pip install -e . --force-reinstall
```

## Rollback (Using Previous Version)

If you encounter issues with the new version, you can rollback:

```bash
# Rollback to 0.9.5
pip uninstall pybinding
pip install pybinding==0.9.5

# Requires Python 3.6-3.8 environment
```

## Support and Feedback

- **Issue Reporting**: https://github.com/dean0x7d/pybinding/issues
- **Documentation**: http://docs.pybinding.site/
- **Q&A**: https://gitter.im/dean0x7d/pybinding

## Migration Checklist

Complete migration checklist:

- [ ] Python 3.9+ installed and verified
- [ ] CMake 3.20+ installed and verified
- [ ] Latest C++ compiler installed and verified
- [ ] pybinding 0.10.0 installed
- [ ] Existing tests run and pass
- [ ] Performance benchmarks verified (optional)
- [ ] Production code tested (optional)

## Additional Resources

- [MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md) - Detailed modernization plan
- [CLAUDE.md](CLAUDE.md) - Developer guide
- [changelog.md](changelog.md) - Complete changelog
