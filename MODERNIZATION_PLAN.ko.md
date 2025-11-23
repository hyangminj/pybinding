# Pybinding 현대화 계획

## 현재 상태 (2020년 마지막 업데이트)

### 문제점
- **C++ 표준**: C++11 (2011년) - 최신 C++20/23 기능 사용 불가
- **Python 지원**: 3.6-3.8 (Python 3.6은 2021년 EOL)
- **의존성 버전**:
  - Eigen3: 3.3.3 (2017년) → 최신 3.4.x 사용 가능
  - pybind11: 매우 오래된 버전 → 최신 2.13.x 사용 가능
  - libsimdpp: 2.0-rc2 (릴리스 후보) → 안정 버전 사용 필요
  - CMake: 3.1 요구 → 최신 3.20+ 기능 활용 가능
- **컴파일러**: GCC 5.0/Clang 3.5 (2014년)
- **빌드 시스템**: 수동 다운로드 방식, conda 의존성

### 성능 개선 기회
1. C++17/20의 최적화 기능 활용 (constexpr if, structured bindings 등)
2. 최신 컴파일러의 벡터화 및 최적화
3. 최신 Eigen3의 성능 개선 활용
4. 최신 pybind11의 오버헤드 감소

## 현대화 목표

### 단기 목표 (호환성 유지)
- C++17 표준으로 업그레이드
- Python 3.9-3.14 지원
- 최신 안정 버전 의존성 사용
- pyproject.toml 기반 빌드 시스템

### 중기 목표 (성능 개선)
- C++20 표준으로 업그레이드
- 최신 컴파일러 최적화 활용
- SIMD 개선 (AVX-512 지원)
- 멀티스레딩 개선

### 장기 목표 (생태계 통합)
- vcpkg/Conan 등 C++ 패키지 매니저 통합
- uv/pip 최신 빌드 백엔드 사용
- CI/CD 현대화 (GitHub Actions)

## 구체적인 변경 사항

### 1. C++ 표준 업그레이드 (C++11 → C++17)

**변경 이유**:
- C++17은 광범위하게 지원됨 (GCC 7+, Clang 5+, MSVC 2017+)
- 성능 및 코드 품질 개선 기능 많음
- C++20은 아직 일부 플랫폼에서 불안정

**주요 개선점**:
- `if constexpr` - 컴파일 타임 분기
- Structured bindings - 코드 간결성
- `std::optional`, `std::variant` - 외부 variant 라이브러리 불필요
- Parallel algorithms - 표준 병렬 처리
- `[[nodiscard]]`, `[[maybe_unused]]` - 더 나은 경고

### 2. Python 지원 업그레이드 (3.6-3.8 → 3.9-3.14)

**변경 이유**:
- Python 3.6-3.8은 모두 EOL (End of Life)
- Python 3.9+는 성능 개선 및 타입 힌팅 개선
- Python 3.11+는 상당한 성능 향상 (10-60%)

**변경 사항**:
- 최소 Python 버전: 3.9
- setup.py → pyproject.toml + CMake
- Type hints 추가 (PEP 484, 604)

### 3. 의존성 업그레이드

| 라이브러리 | 현재 | 목표 | 변경 이유 |
|-----------|------|------|-----------|
| Eigen3 | 3.3.3 (2017) | 3.4.0+ | 성능 개선, 버그 수정 |
| pybind11 | 오래된 버전 | 2.13.x | Python 3.13+ 지원, 성능 개선 |
| libsimdpp | 2.0-rc2 | 제거 후 Eigen/std 사용 | RC 버전 의존성 제거 |
| fmt | 다운로드 | 최신 11.x | C++20 std::format 대체 가능 |
| CMake | 3.1+ | 3.20+ | 현대적 CMake 기능 |

### 4. 빌드 시스템 현대화

**현재 문제**:
- setup.py 기반 (deprecated)
- 수동 의존성 다운로드
- conda 강제 의존

**개선 방안**:
```
pybinding/
├── pyproject.toml          # PEP 517/518 빌드 정의
├── CMakeLists.txt          # 현대적 CMake
├── cmake/
│   └── dependencies.cmake  # FetchContent 사용
└── setup.py               # 하위 호환성 유지 (선택)
```

### 5. 패키지 매니저 통합

**옵션 1: CMake FetchContent** (권장)
```cmake
include(FetchContent)
FetchContent_Declare(eigen URL https://gitlab.com/libeigen/eigen/-/archive/3.4.0/eigen-3.4.0.tar.gz)
FetchContent_MakeAvailable(eigen)
```

**옵션 2: vcpkg** (Windows 친화적)
```bash
vcpkg install eigen3 pybind11
```

**옵션 3: Conan** (크로스 플랫폼)
```python
# conanfile.txt
[requires]
eigen/3.4.0
pybind11/2.13.0
```

### 6. 컴파일러 요구사항 업데이트

| 플랫폼 | 현재 | 목표 |
|--------|------|------|
| Linux | GCC 5.0+ | GCC 9.0+ / Clang 10+ |
| macOS | Clang 3.5+ | Clang 12+ (Xcode 12+) |
| Windows | VS 2015+ | VS 2019+ |

### 7. 성능 최적화 기회

**컴파일러 플래그**:
```cmake
# C++17 모드
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 최적화 플래그
if(NOT MSVC)
    target_compile_options(cppcore PUBLIC
        -march=native        # 네이티브 아키텍처 최적화
        -O3                  # 최대 최적화
        -funroll-loops       # 루프 언롤링
        -ffast-math          # 빠른 수학 연산 (주의 필요)
    )
endif()

# LTO (Link Time Optimization)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
```

**SIMD 개선**:
- libsimdpp 제거
- Eigen의 벡터화 활용 (더 안정적)
- AVX-512 지원 추가

**멀티스레딩**:
- OpenMP 추가 (선택적)
- C++17 parallel algorithms 활용

### 8. 개발 환경 현대화

**CI/CD**:
- Travis CI + AppVeyor → GitHub Actions
- 자동 빌드 및 테스트
- 자동 릴리스 (wheels 빌드)

**개발 도구**:
- pre-commit hooks (clang-format, black)
- Type checking (mypy)
- 정적 분석 (clang-tidy, cppcheck)

## 단계별 실행 계획

### Phase 1: 기반 작업 (안전한 업그레이드)
1. ✅ 현대화 계획 수립
2. pyproject.toml 생성
3. CMake 3.20+ 기능 활용
4. pybind11을 최신 버전으로 업그레이드
5. Eigen3 3.4.0으로 업그레이드
6. Python 3.9+ 지원

### Phase 2: C++ 현대화
1. C++17 표준 적용
2. 코드 리팩토링 (C++17 기능 활용)
3. libsimdpp 제거 (Eigen으로 대체)
4. 컴파일러 경고 수준 향상

### Phase 3: 성능 최적화
1. 최신 컴파일러 최적화 플래그
2. LTO (Link Time Optimization) 활성화
3. 프로파일링 및 병목 제거
4. 벤치마크 비교

### Phase 4: 생태계 통합
1. GitHub Actions CI/CD
2. PyPI wheels 자동 빌드
3. Documentation 업데이트
4. 개발자 도구 (pre-commit, formatting)

## 예상 성능 향상

- **컴파일 시간**: 10-30% 감소 (ccache + 최신 컴파일러)
- **런타임 성능**: 15-40% 향상 (C++17 + 최신 Eigen + 최적화)
- **메모리 사용**: 5-15% 감소 (move semantics 활용)
- **Python 오버헤드**: 10-25% 감소 (최신 pybind11)

## 위험 및 완화 방안

### 위험 요소
1. **하위 호환성 파괴**: 오래된 시스템 지원 불가
2. **빌드 실패**: 새로운 의존성 문제
3. **성능 회귀**: 예상치 못한 성능 저하
4. **사용자 불편**: 빌드 환경 재설정 필요

### 완화 방안
1. 점진적 업그레이드 (major version bump)
2. 충분한 테스트 및 CI
3. 벤치마크 자동화
4. 명확한 마이그레이션 가이드
5. 이전 버전 유지보수 브랜치

## 다음 단계

실행하려면:
1. 이 계획 검토 및 승인
2. Phase 1 시작 (pyproject.toml 생성)
3. 테스트 환경 구축
4. 단계별 구현 및 테스트
