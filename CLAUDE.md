# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Pybinding is a Python package for numerical tight-binding calculations in solid state physics. It features:
- Declarative model construction for tight-binding systems
- Fast computation using the Kernel Polynomial Method (KPM)
- Python interface with C++11 performance-critical code
- Support for 1D, 2D, and 3D lattices with arbitrary geometries

## Build System

### Building from source
```bash
# Create build directory
mkdir build && cd build

# Configure with CMake
cmake -DPYTHON_EXECUTABLE=$(which python) ..

# Build (use -j for parallel builds)
make -j2

# Run tests
make tests
```

### Installing in development mode
```bash
# Install with pip (builds C++ extension automatically)
pip install -e .

# Build with specific options using environment variables
PB_WERROR=ON PB_BUILD_TYPE=Debug pip install -v .
```

### Build configuration options
Control build via environment variables in `setup.py`:
- `PB_WERROR`: Treat warnings as errors (default: OFF)
- `PB_TESTS`: Enable C++ tests (default: OFF)
- `PB_NATIVE_SIMD`: Enable native SIMD instructions (default: ON)
- `PB_MKL`: Use Intel Math Kernel Library (default: OFF)
- `PB_CUDA`: Enable CUDA support (default: OFF)
- `PB_BUILD_TYPE`: Release or Debug (default: Release)

## Testing

### Running Python tests
```bash
# Run all tests using pytest
pytest

# Run specific test file
pytest tests/test_model.py

# Run tests from within Python
python -c "import pybinding as pb; pb.tests()"

# Run with custom pytest options
python -c "import pybinding as pb; pb.tests('-v -k test_name')"
```

### Running C++ tests
```bash
# From build directory (if PB_TESTS=ON)
cd build
make tests
```

### Test configuration
Pytest configuration in `setup.cfg`:
- Tests run with doctests enabled
- Test paths: `pybinding`, `tests`, `docs`
- Custom fixtures in `tests/conftest.py` for baseline comparison and plotting

## Code Architecture

### High-level structure
The codebase is split into three main parts:

1. **Python layer** (`pybinding/`): User-facing API
   - `lattice.py`: Lattice specification (primitive vectors, sublattices, hoppings)
   - `model.py`: Main model builder that assembles system from lattice + modifiers
   - `shape.py`: Geometric shapes for finite systems
   - `modifier.py`: Functions to modify onsite/hopping energies
   - `solver.py`: Eigenvalue solvers for exact diagonalization
   - `chebyshev.py`: KPM-based calculations (DOS, LDOS, conductivity)
   - `results.py`: Result objects with plotting capabilities

2. **C++ core** (`cppcore/`): Performance-critical computations
   - `include/`: Header-only interface
     - `Lattice.hpp`, `Model.hpp`, `KPM.hpp`: Core data structures
     - `system/`: System building (Foundation, Shape, Symmetry, Registry)
     - `hamiltonian/`: Hamiltonian construction and modifiers
     - `kpm/`: Kernel Polynomial Method implementation
     - `solver/`: Eigenvalue solvers (including FEAST for MKL)
     - `leads/`: Semi-infinite lead structures
   - `src/`: Implementation files

3. **Python-C++ bindings** (`cppmodule/`): pybind11 wrappers
   - `src/main.cpp`: Module initialization, calls wrap_* functions
   - Uses pybind11 to expose C++ classes to Python

### Model building workflow
The typical flow for building a tight-binding model:

1. **Lattice** → defines unit cell (primitive vectors, sublattices, hopping terms)
2. **Model** → takes Lattice + Shape + Modifiers
   - Shape determines finite system geometry
   - Modifiers alter onsite energies or hoppings (e.g., fields, disorder)
3. **System** → structural data (site positions, neighbor lists)
4. **Hamiltonian** → sparse matrix representation
5. **Solver/KPM** → compute physical properties

The C++ Model class (cppcore/include/Model.hpp) orchestrates:
- System construction via System class
- Hamiltonian building via Hamiltonian class
- Application of modifiers (structure and Hamiltonian modifiers)
- Lead attachment for transport calculations

### KPM (Kernel Polynomial Method)
Core algorithm for fast spectral calculations:
- Located in `cppcore/include/kpm/` and `pybinding/chebyshev.py`
- Computes moments of Chebyshev expansion
- Supports CUDA acceleration when compiled with PB_CUDA=ON
- Used for: DOS, LDOS, Green's functions, conductivity

### Material repository
Pre-built lattices in `pybinding/repository/`:
- `graphene/`: Graphene lattice with common modifiers
- `group6_tmd.py`: Transition metal dichalcogenides
- `phosphorene.py`: Black phosphorus

## Development Notes

### C++ compilation requirements
- C++11 or newer (controlled by `PB_CPP_STANDARD` in CMake)
- CMake >= 3.1
- On Linux: GCC >= 5.0 or Clang >= 3.5
- On Windows: Visual Studio 2015 or newer

### Dependencies downloaded by CMake
CMake automatically downloads during build:
- Eigen3 (3.3.3): Linear algebra
- pybind11: Python-C++ bindings (in cppmodule/deps/)
- fmt: String formatting
- variant (mapbox): Variant type for C++11
- libsimdpp: SIMD abstractions
- Catch: C++ testing framework (if PB_TESTS=ON)

### Python dependencies
Listed in `setup.py`:
- numpy >= 1.12
- scipy >= 0.19
- matplotlib >= 2.0
- pytest >= 5.0

### Special notes
- **MKL dlopen flags**: On Linux with MKL, special dlopen flags (RTLD_GLOBAL) are required. This is handled in `pybinding/__init__.py` by pre-importing scipy modules to avoid segfaults.
- **ccache**: Build system automatically uses ccache if available for faster rebuilds
- **Version injection**: C++ code receives version string via `-DCPB_VERSION` in setup.py

### Modifier system
Modifiers are user-defined functions that alter the model:
- **Structure modifiers**: Modify positions or disable sites (applied before Hamiltonian)
  - SiteStateModifier, PositionModifier
- **Hamiltonian modifiers**: Modify energies (applied to Hamiltonian matrix)
  - OnsiteModifier, HoppingModifier
- Modifiers can depend on position, sublattice, site index, etc.
- The C++ side stores these as functors and applies them during construction
