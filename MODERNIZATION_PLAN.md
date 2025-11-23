# Pybinding Modernization Plan

## Current State (Last Updated: 2020)

### Issues
- **C++ Standard**: C++11 (from 2011) - Cannot use modern C++20/23 features
- **Python Support**: 3.6-3.8 (Python 3.6 reached EOL in 2021)
- **Dependency Versions**:
  - Eigen3: 3.3.3 (2017) → Latest 3.4.x available
  - pybind11: Very old version → Latest 2.13.x available
  - libsimdpp: 2.0-rc2 (release candidate) → Need stable version
  - CMake: 3.1 required → Latest 3.20+ features available
- **Compiler**: GCC 5.0/Clang 3.5 (from 2014)
- **Build System**: Manual download approach, conda dependency

### Performance Improvement Opportunities
1. Utilize C++17/20 optimization features (constexpr if, structured bindings, etc.)
2. Leverage modern compiler vectorization and optimizations
3. Take advantage of latest Eigen3 performance improvements
4. Reduce overhead with latest pybind11

## Modernization Goals

### Short-term Goals (Maintaining Compatibility)
- Upgrade to C++17 standard
- Support Python 3.9-3.14
- Use latest stable dependency versions
- Implement pyproject.toml-based build system

### Mid-term Goals (Performance Improvements)
- Upgrade to C++20 standard
- Leverage modern compiler optimizations
- Improve SIMD support (AVX-512)
- Enhance multithreading

### Long-term Goals (Ecosystem Integration)
- Integrate C++ package managers (vcpkg/Conan)
- Use modern build backends (uv/pip)
- Modernize CI/CD (GitHub Actions)

## Specific Changes

### 1. C++ Standard Upgrade (C++11 → C++17)

**Rationale**:
- C++17 is widely supported (GCC 7+, Clang 5+, MSVC 2017+)
- Many performance and code quality improvements
- C++20 still unstable on some platforms

**Key Improvements**:
- `if constexpr` - Compile-time branching
- Structured bindings - Code conciseness
- `std::optional`, `std::variant` - No external variant library needed
- Parallel algorithms - Standard parallelization
- `[[nodiscard]]`, `[[maybe_unused]]` - Better warnings

### 2. Python Support Upgrade (3.6-3.8 → 3.9-3.14)

**Rationale**:
- Python 3.6-3.8 all EOL (End of Life)
- Python 3.9+ has performance improvements and better type hinting
- Python 3.11+ has significant performance gains (10-60%)

**Changes**:
- Minimum Python version: 3.9
- setup.py → pyproject.toml + CMake
- Add type hints (PEP 484, 604)

### 3. Dependency Upgrades

| Library | Current | Target | Reason |
|---------|---------|--------|--------|
| Eigen3 | 3.3.3 (2017) | 3.4.0+ | Performance improvements, bug fixes |
| pybind11 | Old version | 2.13.x | Python 3.13+ support, performance |
| libsimdpp | 2.0-rc2 | Remove, use Eigen/std | Remove RC dependency |
| fmt | Download | Latest 11.x | Can replace with C++20 std::format |
| CMake | 3.1+ | 3.20+ | Modern CMake features |

### 4. Build System Modernization

**Current Issues**:
- setup.py-based (deprecated)
- Manual dependency downloads
- Forced conda dependency

**Improvements**:
```
pybinding/
├── pyproject.toml          # PEP 517/518 build definition
├── CMakeLists.txt          # Modern CMake
├── cmake/
│   └── dependencies.cmake  # Use FetchContent
└── setup.py               # Backward compatibility (optional)
```

### 5. Package Manager Integration

**Option 1: CMake FetchContent** (Recommended)
```cmake
include(FetchContent)
FetchContent_Declare(eigen URL https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz)
FetchContent_MakeAvailable(eigen)
```

**Option 2: vcpkg** (Windows-friendly)
```bash
vcpkg install eigen3 pybind11
```

**Option 3: Conan** (Cross-platform)
```python
# conanfile.txt
[requires]
eigen/3.4.0
pybind11/2.13.0
```

### 6. Compiler Requirements Update

| Platform | Current | Target |
|----------|---------|--------|
| Linux | GCC 5.0+ | GCC 9.0+ / Clang 10+ |
| macOS | Clang 3.5+ | Clang 12+ (Xcode 12+) |
| Windows | VS 2015+ | VS 2019+ |

### 7. Performance Optimization Opportunities

**Compiler Flags**:
```cmake
# C++17 mode
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Optimization flags
if(NOT MSVC)
    target_compile_options(cppcore PUBLIC
        -march=native        # Native architecture optimization
        -O3                  # Maximum optimization
        -funroll-loops       # Loop unrolling
        -ffast-math          # Fast math operations (use with care)
    )
endif()

# LTO (Link Time Optimization)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
```

**SIMD Improvements**:
- Remove libsimdpp
- Use Eigen's vectorization (more stable)
- Add AVX-512 support

**Multithreading**:
- Add OpenMP (optional)
- Utilize C++17 parallel algorithms

### 8. Development Environment Modernization

**CI/CD**:
- Travis CI + AppVeyor → GitHub Actions
- Automated build and test
- Automated releases (build wheels)

**Development Tools**:
- pre-commit hooks (clang-format, black)
- Type checking (mypy)
- Static analysis (clang-tidy, cppcheck)

## Phased Implementation Plan

### Phase 1: Foundation (Safe Upgrades)
1. ✅ Establish modernization plan
2. Create pyproject.toml
3. Utilize CMake 3.20+ features
4. Upgrade pybind11 to latest version
5. Upgrade Eigen3 to 3.4.0
6. Support Python 3.9+

### Phase 2: C++ Modernization
1. Apply C++17 standard
2. Refactor code (utilize C++17 features)
3. Remove libsimdpp (replace with Eigen)
4. Increase compiler warning levels

### Phase 3: Performance Optimization
1. Latest compiler optimization flags
2. Enable LTO (Link Time Optimization)
3. Profiling and bottleneck removal
4. Benchmark comparisons

### Phase 4: Ecosystem Integration
1. GitHub Actions CI/CD
2. Automated PyPI wheel builds
3. Documentation updates
4. Developer tools (pre-commit, formatting)

## Expected Performance Improvements

- **Compile Time**: 10-30% reduction (ccache + modern compiler)
- **Runtime Performance**: 15-40% improvement (C++17 + latest Eigen + optimizations)
- **Memory Usage**: 5-15% reduction (move semantics utilization)
- **Python Overhead**: 10-25% reduction (latest pybind11)

## Risks and Mitigation

### Risk Factors
1. **Breaking Backward Compatibility**: Old systems unsupported
2. **Build Failures**: New dependency issues
3. **Performance Regression**: Unexpected performance degradation
4. **User Inconvenience**: Build environment reconfiguration needed

### Mitigation Strategies
1. Gradual upgrade (major version bump)
2. Sufficient testing and CI
3. Automated benchmarking
4. Clear migration guide
5. Maintain legacy version branch

## Next Steps

To proceed:
1. Review and approve this plan
2. Start Phase 1 (create pyproject.toml)
3. Set up test environment
4. Implement and test step-by-step
