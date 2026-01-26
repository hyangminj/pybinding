cmake_minimum_required(VERSION 3.20)
project(pybinding_cppcore CXX)

# Modern CMake: Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build" FORCE)
    set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release" "RelWithDebInfo" "MinSizeRel")
endif()

# Options
option(PB_WERROR "Make all warnings into errors" OFF)
option(PB_TESTS "Enable testing" ON)
option(PB_NATIVE_SIMD "Enable all instruction sets supported by the local machine" ON)
option(PB_USE_SIMD "Use libsimdpp for SIMD optimizations (disable for C++17 compatibility)" ON)
option(PB_MKL "Use Intel's Math Kernel Library" OFF)
option(PB_CUDA "Enable compilation of components written in CUDA" OFF)
option(PB_USE_CCACHE "Use ccache if available" ON)

# ccache support
if(PB_USE_CCACHE)
    find_program(CCACHE_PROGRAM ccache)
    if(CCACHE_PROGRAM)
        set(CMAKE_CXX_COMPILER_LAUNCHER "${CCACHE_PROGRAM}")
        message(STATUS "Using ccache: ${CCACHE_PROGRAM}")
    endif()
endif()

# Enable IPO/LTO if supported
include(CheckIPOSupported)
check_ipo_supported(RESULT ipo_supported OUTPUT ipo_error)
if(ipo_supported AND CMAKE_BUILD_TYPE STREQUAL "Release")
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
    message(STATUS "IPO/LTO enabled")
else()
    message(STATUS "IPO/LTO not supported: ${ipo_error}")
endif()

# Dependencies using FetchContent (modern CMake way)
include(FetchContent)

# Eigen3 - Latest stable version
FetchContent_Declare(
    eigen3
    URL https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz
    URL_HASH SHA256=8586084f71f9bde545ee7fa6d00288b264a2b7ac3607b974e54d13e7162c1c72
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(eigen3)

# fmt - Modern formatting library
FetchContent_Declare(
    fmt
    URL https://github.com/fmtlib/fmt/archive/refs/tags/11.0.2.tar.gz
    URL_HASH SHA256=6cb1e6d37bdcb756dbbe59be438790db409cdb4868c66e888d5df9f13f7c027f
    DOWNLOAD_EXTRACT_TIMESTAMP TRUE
)
FetchContent_MakeAvailable(fmt)

# libsimdpp - SIMD abstraction library (header-only)
# Note: v2.1 has C++17 compilation issues with modern GCC (see #140), but master has API changes.
# Set PB_USE_SIMD=OFF to disable libsimdpp entirely (recommended for CI builds).
# Don't use MakeAvailable because libsimdpp's CMakeLists.txt requires CMake < 3.5
if(PB_USE_SIMD)
    FetchContent_Declare(
        libsimdpp
        URL https://github.com/p12tic/libsimdpp/archive/refs/tags/v2.1.tar.gz
        URL_HASH SHA256=b0e986b20bef77cd17004dd02db0c1ad9fab9c70d4e99594a9db1ee6a345be93
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
    )
    FetchContent_GetProperties(libsimdpp)
    if(NOT libsimdpp_POPULATED)
        FetchContent_Populate(libsimdpp)
    endif()
endif()

# Note: pybind11 is provided by the parent CMakeLists.txt through the Python package

# Source files
set(CPPCORE_HEADERS
    include/compute/eigen3/lanczos.hpp
    include/compute/detail.hpp
    include/compute/kernel_polynomial.hpp
    include/compute/lanczos.hpp
    include/detail/algorithm.hpp
    include/detail/config.hpp
    include/detail/macros.hpp
    include/detail/opaque_alias.hpp
    include/detail/slice.hpp
    include/detail/strategy.hpp
    include/detail/sugar.hpp
    include/detail/thread.hpp
    include/detail/typelist.hpp
    include/hamiltonian/Hamiltonian.hpp
    include/hamiltonian/HamiltonianModifiers.hpp
    include/kpm/default/collectors.hpp
    include/kpm/default/Compute.hpp
    include/kpm/Bounds.hpp
    include/kpm/calc_moments.hpp
    include/kpm/Config.hpp
    include/kpm/Core.hpp
    include/kpm/Kernel.hpp
    include/kpm/Moments.hpp
    include/kpm/OptimizedHamiltonian.hpp
    include/kpm/reconstruct.hpp
    include/kpm/Starter.hpp
    include/kpm/Stats.hpp
    include/leads/HamiltonianPair.hpp
    include/leads/Leads.hpp
    include/leads/Spec.hpp
    include/leads/Structure.hpp
    include/numeric/arrayref.hpp
    include/numeric/constant.hpp
    include/numeric/dense.hpp
    include/numeric/ellmatrix.hpp
    include/numeric/random.hpp
    include/numeric/sparse.hpp
    include/numeric/sparseref.hpp
    include/numeric/traits.hpp
    include/solver/FEAST.hpp
    include/solver/Solver.hpp
    include/support/cppfuture.hpp
    include/support/format.hpp
    include/support/simd.hpp
    include/system/CompressedSublattices.hpp
    include/system/Foundation.hpp
    include/system/HoppingBlocks.hpp
    include/system/Registry.hpp
    include/system/Shape.hpp
    include/system/StructureModifiers.hpp
    include/system/Symmetry.hpp
    include/system/System.hpp
    include/utils/Chrono.hpp
    include/KPM.hpp
    include/Lattice.hpp
    include/Model.hpp
)

set(CPPCORE_SOURCES
    src/hamiltonian/Hamiltonian.cpp
    src/hamiltonian/HamiltonianModifiers.cpp
    src/kpm/default/collectors.cpp
    src/kpm/default/Compute.cpp
    src/kpm/Bounds.cpp
    src/kpm/Core.cpp
    src/kpm/Kernel.cpp
    src/kpm/Moments.cpp
    src/kpm/OptimizedHamiltonian.cpp
    src/kpm/Starter.cpp
    src/kpm/Stats.cpp
    src/leads/Leads.cpp
    src/leads/Spec.cpp
    src/leads/Structure.cpp
    src/solver/FEAST.cpp
    src/solver/Solver.cpp
    src/system/CompressedSublattices.cpp
    src/system/Foundation.cpp
    src/system/HoppingBlocks.cpp
    src/system/Registry.cpp
    src/system/Shape.cpp
    src/system/StructureModifiers.cpp
    src/system/Symmetry.cpp
    src/system/System.cpp
    src/utils/Chrono.cpp
    src/KPM.cpp
    src/Lattice.cpp
    src/Model.cpp
)

# Create library (modern CMake: only sources in add_library)
add_library(cppcore ${CPPCORE_SOURCES})
target_sources(cppcore PRIVATE ${CPPCORE_HEADERS})
add_library(pybinding::cppcore ALIAS cppcore)

# Include directories
target_include_directories(cppcore PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

# SIMD library include (only when SIMD is enabled)
if(PB_USE_SIMD)
    # Use PUBLIC because cppcore headers (like support/simd.hpp) include libsimdpp headers
    # Use BUILD_INTERFACE to avoid CMake error about build directory paths in INTERFACE properties
    target_include_directories(cppcore SYSTEM PUBLIC
        $<BUILD_INTERFACE:${libsimdpp_SOURCE_DIR}>
    )
    target_compile_definitions(cppcore PUBLIC CPB_USE_SIMD=1)
else()
    target_compile_definitions(cppcore PUBLIC CPB_USE_SIMD=0)
    message(STATUS "SIMD support disabled (PB_USE_SIMD=OFF)")
endif()

# Thread support (must come before target_link_libraries)
find_package(Threads REQUIRED)

# Link libraries
target_link_libraries(cppcore PUBLIC
    Eigen3::Eigen
    fmt::fmt
    Threads::Threads
)

# Compiler warnings
if(MSVC)
    target_compile_options(cppcore PRIVATE /W4)
    if(PB_WERROR)
        target_compile_options(cppcore PRIVATE /WX)
    endif()
else()
    target_compile_options(cppcore PRIVATE
        -Wall -Wextra -Wpedantic
        -Wno-unused-parameter
        -Wno-missing-field-initializers
    )
    if(PB_WERROR)
        target_compile_options(cppcore PRIVATE -Werror)
    endif()
endif()

# Platform-specific optimizations
if(NOT MSVC)
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        target_compile_options(cppcore PRIVATE
            -O3
            -funroll-loops
        )

        if(PB_NATIVE_SIMD)
            target_compile_options(cppcore PRIVATE -march=native)
            message(STATUS "Native SIMD instructions enabled (-march=native)")
        endif()
    endif()
endif()

# MKL support
if(PB_MKL)
    find_package(MKL REQUIRED)
    target_link_libraries(cppcore PUBLIC MKL::MKL)
    target_compile_definitions(cppcore PUBLIC CPB_USE_MKL)

    # MKL-specific headers
    target_sources(cppcore PRIVATE
        include/compute/mkl/lanczos.hpp
        include/compute/mkl/wrapper.hpp
    )
    message(STATUS "Intel MKL support enabled")
endif()

# CUDA support
if(PB_CUDA)
    enable_language(CUDA)
    add_subdirectory(cuda)
    target_link_libraries(cppcore PUBLIC pybinding_cuda)
    message(STATUS "CUDA support enabled")
endif()

# Testing
if(PB_TESTS)
    FetchContent_Declare(
        Catch2
        URL https://github.com/catchorg/Catch2/archive/refs/tags/v3.5.0.tar.gz
        URL_HASH SHA256=f6d4f8d78a9b59ec72a81d49f58d18eb317372ac07f8d9432710a079e69fd66a
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE
    )
    FetchContent_MakeAvailable(Catch2)

    add_subdirectory(tests)
    message(STATUS "C++ tests enabled")
endif()

# Installation (for development)
install(TARGETS cppcore
    EXPORT pybinding-targets
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
    INCLUDES DESTINATION include
)

install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.hpp"
)

# Export targets
install(EXPORT pybinding-targets
    FILE pybinding-targets.cmake
    NAMESPACE pybinding::
    DESTINATION lib/cmake/pybinding
)

# Print configuration summary
message(STATUS "")
message(STATUS "=== Pybinding C++ Core Configuration ===")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "Native SIMD: ${PB_NATIVE_SIMD}")
message(STATUS "MKL: ${PB_MKL}")
message(STATUS "CUDA: ${PB_CUDA}")
message(STATUS "Tests: ${PB_TESTS}")
message(STATUS "IPO/LTO: ${CMAKE_INTERPROCEDURAL_OPTIMIZATION}")
message(STATUS "========================================")
message(STATUS "")
