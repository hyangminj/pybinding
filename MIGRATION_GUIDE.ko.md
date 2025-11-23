# Pybinding 0.10.0 마이그레이션 가이드

## 개요

Pybinding 0.10.0은 주요 현대화 릴리스입니다. 이 버전은 다음을 포함합니다:
- C++17 표준 사용
- Python 3.9+ 지원
- 최신 빌드 도구 및 의존성
- 성능 개선
- 현대적 CI/CD

## 주요 변경사항

### 1. Python 버전 요구사항

**이전**: Python 3.6-3.8
**현재**: Python 3.9-3.14

**마이그레이션**:
```bash
# Python 버전 확인
python --version

# Python 3.9+ 설치 (macOS)
brew install python@3.11

# Python 3.9+ 설치 (Ubuntu)
sudo apt-get install python3.11

# 가상환경 생성
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# 또는
venv\Scripts\activate  # Windows
```

### 2. 빌드 시스템 변경

**이전**: setup.py만 사용
**현재**: pyproject.toml (권장) + setup.py (호환성)

**설치 방법**:

#### 방법 1: pip (권장)
```bash
# 일반 설치
pip install pybinding

# 개발 모드
pip install -e .[dev]

# MKL 지원
pip install -e .[mkl]
```

#### 방법 2: 소스에서 빌드
```bash
# 의존성 확인
python --version  # 3.9+
cmake --version   # 3.20+
gcc --version     # 9.0+ (Linux)
clang --version   # 12.0+ (macOS)

# 빌드
pip install -e .

# 또는 특정 옵션으로 빌드
PB_BUILD_TYPE=Release PB_NATIVE_SIMD=ON pip install -e .
```

### 3. 의존성 버전 업그레이드

| 패키지 | 이전 | 현재 | 영향 |
|--------|------|------|------|
| numpy | >=1.12 | >=1.20 | API 변경 거의 없음 |
| scipy | >=0.19 | >=1.7 | 성능 개선 |
| matplotlib | >=2.0 | >=3.3 | 플롯 API 일부 변경 |
| pytest | >=5.0 | >=6.0 | 테스트 실행 방법 동일 |

**마이그레이션**:
```bash
# 의존성 업데이트
pip install --upgrade numpy scipy matplotlib pytest
```

### 4. C++ 컴파일러 요구사항

**이전**:
- Linux: GCC 5.0+ / Clang 3.5+
- macOS: Xcode 7+
- Windows: Visual Studio 2015+

**현재**:
- Linux: GCC 9.0+ / Clang 10+
- macOS: Xcode 12+ (Clang 12+)
- Windows: Visual Studio 2019+

**마이그레이션**:

Linux (Ubuntu/Debian):
```bash
# 컴파일러 버전 확인
gcc --version

# GCC 9+ 설치
sudo apt-get update
sudo apt-get install gcc-11 g++-11
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100
```

macOS:
```bash
# Xcode Command Line Tools 업데이트
xcode-select --install

# 또는 Homebrew로 최신 LLVM 설치
brew install llvm
```

Windows:
```powershell
# Visual Studio 2019 또는 2022 설치
# https://visualstudio.microsoft.com/downloads/

# 또는 Build Tools만 설치
# https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
```

### 5. CMake 버전 업그레이드

**이전**: CMake 3.1+
**현재**: CMake 3.20+

**마이그레이션**:
```bash
# 현재 버전 확인
cmake --version

# pip으로 설치 (모든 플랫폼)
pip install --upgrade cmake

# 또는 시스템 패키지 매니저
brew install cmake      # macOS
sudo apt-get install cmake  # Ubuntu
choco install cmake     # Windows
```

### 6. 환경 변수 변경

빌드 설정 환경 변수는 동일하게 유지됩니다:

```bash
# 빌드 타입 (Debug/Release)
export PB_BUILD_TYPE=Release

# 경고를 에러로 처리
export PB_WERROR=ON

# C++ 테스트 활성화
export PB_TESTS=ON

# 네이티브 SIMD 명령어 사용
export PB_NATIVE_SIMD=ON

# Intel MKL 사용
export PB_MKL=ON

# CUDA 지원 (CUDA 설치 필요)
export PB_CUDA=ON

# 빌드
pip install -e .
```

### 7. API 변경사항

**주요 API는 하위 호환성 유지**. 대부분의 코드는 수정 없이 작동합니다.

#### 변경된 부분:

1. **Numpy 배열 경고**:
```python
# 이전 (경고 발생 가능)
model = pb.Model(lattice, shape, pb.rectangle(10, 10))

# 현재 (권장)
model = pb.Model(lattice, pb.rectangle(10, 10))
```

2. **Matplotlib 플롯팅**:
```python
# 일부 플롯 함수에서 반환값 변경됨
# 대부분 자동으로 처리되지만, 커스텀 플롯 코드는 확인 필요
```

3. **타입 힌팅 추가** (선택사항):
```python
from pybinding import Lattice, Model
from typing import List

def create_model(lattice: Lattice) -> Model:
    return Model(lattice)
```

### 8. 개발 환경 설정

#### 새로운 개발 도구 사용 가능:

```bash
# 개발 의존성 설치
pip install -e .[dev]

# 코드 포맷팅 (Black)
black pybinding tests

# 린팅 (Ruff)
ruff check pybinding tests

# 타입 체크 (mypy)
mypy pybinding

# 테스트 실행
pytest tests/ -v
```

#### pre-commit hooks (선택사항):
```bash
# pre-commit 설치
pip install pre-commit

# hooks 설치
pre-commit install

# 수동 실행
pre-commit run --all-files
```

### 9. conda에서 pip으로 마이그레이션

**이전 방식** (conda 필수):
```bash
conda create -n pb-env python=3.8
conda activate pb-env
conda install -c conda-forge numpy scipy matplotlib kwant pytest cmake
pip install pybinding
```

**현재 방식** (pip만으로 가능):
```bash
# Python 3.9+ 가상환경
python3.11 -m venv venv
source venv/bin/activate

# 모든 의존성 pip으로 설치
pip install pybinding

# 또는 소스에서 빌드
git clone https://github.com/dean0x7d/pybinding.git
cd pybinding
pip install -e .[dev]
```

**여전히 conda 사용 가능**:
```bash
conda create -n pb-env python=3.11
conda activate pb-env
conda install -c conda-forge cmake
pip install pybinding
```

### 10. 성능 최적화 팁

#### 최대 성능으로 빌드:
```bash
# Release 모드 + 네이티브 최적화
PB_BUILD_TYPE=Release PB_NATIVE_SIMD=ON pip install --no-build-isolation -e .

# Intel CPU에서 MKL 사용
pip install mkl mkl-include
PB_MKL=ON pip install --no-build-isolation -e .
```

#### 벤치마크:
```python
import pybinding as pb
import time

# 기존 코드로 벤치마크
start = time.time()
# ... 계산 ...
print(f"Time: {time.time() - start:.2f}s")
```

**예상 성능 향상**:
- 모델 빌드: 15-30% 빠름
- KPM 계산: 20-40% 빠름
- 메모리 사용: 10-20% 감소

## 문제 해결

### 빌드 실패

#### 문제: "CMake 3.20 or newer is required"
```bash
pip install --upgrade cmake
```

#### 문제: "C++17 not supported"
```bash
# 컴파일러 업데이트 (위의 "4. C++ 컴파일러 요구사항" 참조)
```

#### 문제: "Eigen3 not found"
```bash
# CMake가 자동으로 다운로드하므로, 빌드 캐시 삭제 후 재시도
rm -rf build/
pip install -e . --no-build-isolation
```

### 런타임 오류

#### 문제: "ImportError: libstdc++.so.6: version 'GLIBCXX_3.4.XX' not found"
```bash
# 시스템 libstdc++ 업데이트 또는
# conda 환경에서 제거
conda uninstall libgcc
conda update --all
```

#### 문제: Numpy 경고
```bash
# Numpy 업데이트
pip install --upgrade numpy
```

### 성능 문제

#### 성능이 이전보다 느림
```bash
# Release 모드로 재빌드
pip uninstall pybinding
PB_BUILD_TYPE=Release pip install -e .

# 네이티브 최적화 활성화
PB_NATIVE_SIMD=ON pip install -e . --force-reinstall
```

## 롤백 (이전 버전 사용)

새 버전에 문제가 있다면 이전 버전으로 되돌릴 수 있습니다:

```bash
# 0.9.5로 롤백
pip uninstall pybinding
pip install pybinding==0.9.5

# Python 3.6-3.8 환경 필요
```

## 지원 및 피드백

- **이슈 리포트**: https://github.com/dean0x7d/pybinding/issues
- **문서**: http://docs.pybinding.site/
- **Q&A**: https://gitter.im/dean0x7d/pybinding

## 체크리스트

마이그레이션 완료를 위한 체크리스트:

- [ ] Python 3.9+ 설치 확인
- [ ] CMake 3.20+ 설치 확인
- [ ] 최신 C++ 컴파일러 설치 확인
- [ ] pybinding 0.10.0 설치
- [ ] 기존 테스트 실행 및 통과 확인
- [ ] 성능 벤치마크 확인 (선택)
- [ ] 프로덕션 코드 테스트 (선택)

## 추가 리소스

- [MODERNIZATION_PLAN.md](MODERNIZATION_PLAN.md) - 상세 현대화 계획
- [CLAUDE.md](CLAUDE.md) - 개발자 가이드
- [changelog.md](changelog.md) - 전체 변경 로그
