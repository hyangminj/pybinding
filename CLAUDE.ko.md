# CLAUDE.md

이 파일은 Claude Code (claude.ai/code)가 이 저장소의 코드를 작업할 때 참고할 가이드를 제공합니다.

## 프로젝트 개요

Pybinding은 고체물리학에서 수치적 타이트바인딩 계산을 위한 Python 패키지입니다. 주요 기능:
- 타이트바인딩 시스템을 위한 선언적 모델 구성
- Kernel Polynomial Method (KPM)를 사용한 빠른 계산
- 성능이 중요한 코드는 C++11로 구현된 Python 인터페이스
- 임의의 기하학을 가진 1D, 2D, 3D 격자 지원

## 빌드 시스템

### 소스에서 빌드하기
```bash
# 빌드 디렉토리 생성
mkdir build && cd build

# CMake로 설정
cmake -DPYTHON_EXECUTABLE=$(which python) ..

# 빌드 (병렬 빌드는 -j 사용)
make -j2

# 테스트 실행
make tests
```

### 개발 모드로 설치
```bash
# pip으로 설치 (C++ 확장 자동 빌드)
pip install -e .

# 환경 변수로 특정 옵션 지정하여 빌드
PB_WERROR=ON PB_BUILD_TYPE=Debug pip install -v .
```

### 빌드 설정 옵션
`setup.py`에서 환경 변수로 빌드 제어:
- `PB_WERROR`: 경고를 에러로 처리 (기본값: OFF)
- `PB_TESTS`: C++ 테스트 활성화 (기본값: OFF)
- `PB_NATIVE_SIMD`: 네이티브 SIMD 명령어 활성화 (기본값: ON)
- `PB_MKL`: Intel Math Kernel Library 사용 (기본값: OFF)
- `PB_CUDA`: CUDA 지원 활성화 (기본값: OFF)
- `PB_BUILD_TYPE`: Release 또는 Debug (기본값: Release)

## 테스트

### Python 테스트 실행
```bash
# pytest로 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_model.py

# Python 내에서 테스트 실행
python -c "import pybinding as pb; pb.tests()"

# 커스텀 pytest 옵션으로 실행
python -c "import pybinding as pb; pb.tests('-v -k test_name')"
```

### C++ 테스트 실행
```bash
# 빌드 디렉토리에서 (PB_TESTS=ON인 경우)
cd build
make tests
```

### 테스트 설정
`setup.cfg`의 Pytest 설정:
- doctest가 활성화된 상태로 테스트 실행
- 테스트 경로: `pybinding`, `tests`, `docs`
- `tests/conftest.py`에 베이스라인 비교 및 플롯팅을 위한 커스텀 fixture

## 코드 아키텍처

### 상위 레벨 구조
코드베이스는 세 가지 주요 부분으로 나뉩니다:

1. **Python 레이어** (`pybinding/`): 사용자 대면 API
   - `lattice.py`: 격자 명세 (기본 벡터, 부격자, 호핑)
   - `model.py`: 격자 + 수정자로부터 시스템을 조립하는 메인 모델 빌더
   - `shape.py`: 유한 시스템을 위한 기하학적 형상
   - `modifier.py`: 온사이트/호핑 에너지를 수정하는 함수
   - `solver.py`: 정확한 대각화를 위한 고유값 솔버
   - `chebyshev.py`: KPM 기반 계산 (DOS, LDOS, 전도도)
   - `results.py`: 플롯팅 기능을 가진 결과 객체

2. **C++ 코어** (`cppcore/`): 성능이 중요한 계산
   - `include/`: 헤더 전용 인터페이스
     - `Lattice.hpp`, `Model.hpp`, `KPM.hpp`: 핵심 데이터 구조
     - `system/`: 시스템 구축 (Foundation, Shape, Symmetry, Registry)
     - `hamiltonian/`: 해밀토니안 구성 및 수정자
     - `kpm/`: Kernel Polynomial Method 구현
     - `solver/`: 고유값 솔버 (MKL용 FEAST 포함)
     - `leads/`: 반무한 리드 구조
   - `src/`: 구현 파일

3. **Python-C++ 바인딩** (`cppmodule/`): pybind11 래퍼
   - `src/main.cpp`: 모듈 초기화, wrap_* 함수 호출
   - pybind11을 사용하여 C++ 클래스를 Python에 노출

### 모델 구축 워크플로우
타이트바인딩 모델 구축의 일반적인 흐름:

1. **Lattice** → 단위 셀 정의 (기본 벡터, 부격자, 호핑 항)
2. **Model** → Lattice + Shape + Modifiers 사용
   - Shape는 유한 시스템 기하학 결정
   - Modifiers는 온사이트 에너지 또는 호핑 변경 (예: 장, 무질서)
3. **System** → 구조적 데이터 (사이트 위치, 이웃 목록)
4. **Hamiltonian** → 희소 행렬 표현
5. **Solver/KPM** → 물리적 성질 계산

C++ Model 클래스 (cppcore/include/Model.hpp)는 다음을 조율합니다:
- System 클래스를 통한 시스템 구성
- Hamiltonian 클래스를 통한 해밀토니안 구축
- 수정자 적용 (구조 및 해밀토니안 수정자)
- 전송 계산을 위한 리드 부착

### KPM (Kernel Polynomial Method)
빠른 스펙트럼 계산을 위한 핵심 알고리즘:
- `cppcore/include/kpm/` 및 `pybinding/chebyshev.py`에 위치
- 체비셰프 전개의 모멘트 계산
- PB_CUDA=ON으로 컴파일 시 CUDA 가속 지원
- 사용처: DOS, LDOS, 그린 함수, 전도도

### 재료 저장소
`pybinding/repository/`의 사전 구축된 격자:
- `graphene/`: 일반적인 수정자가 있는 그래핀 격자
- `group6_tmd.py`: 전이 금속 이칼코게나이드
- `phosphorene.py`: 흑린

## 개발 참고사항

### C++ 컴파일 요구사항
- C++11 이상 (CMake의 `PB_CPP_STANDARD`로 제어)
- CMake >= 3.1
- Linux: GCC >= 5.0 또는 Clang >= 3.5
- Windows: Visual Studio 2015 이상

### CMake가 자동으로 다운로드하는 의존성
빌드 중 CMake가 자동으로 다운로드:
- Eigen3 (3.3.3): 선형대수
- pybind11: Python-C++ 바인딩 (cppmodule/deps/에 위치)
- fmt: 문자열 포맷팅
- variant (mapbox): C++11용 variant 타입
- libsimdpp: SIMD 추상화
- Catch: C++ 테스팅 프레임워크 (PB_TESTS=ON인 경우)

### Python 의존성
`setup.py`에 명시:
- numpy >= 1.12
- scipy >= 0.19
- matplotlib >= 2.0
- pytest >= 5.0

### 특별 참고사항
- **MKL dlopen 플래그**: Linux에서 MKL 사용 시 특별한 dlopen 플래그 (RTLD_GLOBAL)가 필요합니다. 이는 `pybinding/__init__.py`에서 segfault를 방지하기 위해 scipy 모듈을 미리 import하여 처리됩니다.
- **ccache**: 빌드 시스템은 ccache가 사용 가능한 경우 자동으로 사용하여 재빌드 속도 향상
- **버전 주입**: C++ 코드는 setup.py에서 `-DCPB_VERSION`을 통해 버전 문자열을 받습니다

### 수정자 시스템
수정자는 모델을 변경하는 사용자 정의 함수입니다:
- **구조 수정자**: 위치를 수정하거나 사이트를 비활성화 (해밀토니안 전에 적용)
  - SiteStateModifier, PositionModifier
- **해밀토니안 수정자**: 에너지를 수정 (해밀토니안 행렬에 적용)
  - OnsiteModifier, HoppingModifier
- 수정자는 위치, 부격자, 사이트 인덱스 등에 따라 달라질 수 있습니다
- C++ 측에서는 이를 functor로 저장하고 구성 중에 적용합니다
