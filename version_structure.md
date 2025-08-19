# 버전 관리 구조 설계

## 📁 **프로젝트 구조**

```
agrionDiaryMacro/
├── README.md
├── requirements.txt
├── .env
├── .gitignore
│
├── 📦 v1.0/                    # 기존 버전 (단일 파일 구조)
│   ├── auto_diary_writer.py    # 기존 2,255줄 파일
│   ├── ai_GPT_diary_content_generator.py
│   ├── settings.py
│   ├── start_diary_writer.py
│   ├── data/
│   │   └── rice_schedule_data.json
│   └── log/                    # 기존 로그들
│
├── 📦 v2.0/                    # 리팩토링 버전 (모듈화 구조)
│   ├── core/                   # 핵심 모듈들
│   │   ├── __init__.py
│   │   ├── browser_manager.py
│   │   ├── logger_manager.py
│   │   ├── schedule_processor.py
│   │   ├── config_manager.py
│   │   └── web_interactor.py
│   │
│   ├── services/               # 서비스 레이어
│   │   ├── __init__.py
│   │   ├── content_generator_wrapper.py
│   │   ├── error_handler.py
│   │   └── diary_processor.py
│   │
│   ├── main/                   # 메인 실행 파일들
│   │   ├── __init__.py
│   │   ├── agrion_macro_v2.py
│   │   └── start_diary_writer_v2.py
│   │
│   ├── utils/                  # 유틸리티
│   │   ├── __init__.py
│   │   └── constants.py
│   │
│   ├── tests/                  # 테스트 파일들
│   │   ├── __init__.py
│   │   ├── test_browser_manager.py
│   │   ├── test_logger_manager.py
│   │   └── test_integration.py
│   │
│   ├── data/                   # 데이터 파일들
│   │   └── rice_schedule_data.json
│   │
│   ├── config/                 # 설정 파일들
│   │   ├── settings.py
│   │   └── ai_GPT_diary_content_generator.py
│   │
│   └── log/                    # v2.0 로그들
│
├── 📦 shared/                  # 공통 리소스
│   ├── data/                   # 공통 데이터
│   │   └── rice_schedule_data.json
│   ├── config/                 # 공통 설정
│   │   └── settings.py
│   └── requirements.txt        # 공통 의존성
│
└── 📦 docs/                    # 문서
    ├── v1.0_documentation.md
    ├── v2.0_documentation.md
    ├── migration_guide.md
    └── api_reference.md
```

## 🔄 **버전별 특징**

### **v1.0 (기존 버전)**

- **구조**: 단일 파일 구조
- **파일 크기**: 2,255줄 (auto_diary_writer.py)
- **특징**:
  - 단일 책임 원칙 위반
  - 유지보수 어려움
  - 테스트 어려움
  - 모든 기능이 하나의 클래스에 집중

### **v2.0 (리팩토링 버전)**

- **구조**: 모듈화 구조
- **파일 크기**: 300-400줄 (각 모듈)
- **특징**:
  - 단일 책임 원칙 준수
  - 의존성 주입 패턴
  - 테스트 용이성
  - 유지보수성 향상

## 📋 **마이그레이션 계획**

### **1단계: 기존 코드 백업**

```bash
# v1.0 폴더 생성 및 기존 파일 이동
mkdir v1.0
mv auto_diary_writer.py v1.0/
mv ai_GPT_diary_content_generator.py v1.0/
mv settings.py v1.0/
mv start_diary_writer.py v1.0/
```

### **2단계: v2.0 구조 생성**

```bash
# v2.0 폴더 구조 생성
mkdir -p v2.0/{core,services,main,utils,tests,data,config,log}
```

### **3단계: 모듈별 파일 이동**

```bash
# 핵심 모듈들 이동
mv browser_manager.py v2.0/core/
mv logger_manager.py v2.0/core/
mv schedule_processor.py v2.0/core/
mv config_manager.py v2.0/core/
```

### **4단계: 공통 리소스 분리**

```bash
# 공통으로 사용되는 파일들
mkdir -p shared/{data,config}
cp v1.0/data/rice_schedule_data.json shared/data/
cp v1.0/settings.py shared/config/
```

## 🚀 **실행 방법**

### **v1.0 실행**

```bash
cd v1.0
python start_diary_writer.py
```

### **v2.0 실행**

```bash
cd v2.0
python main/start_diary_writer_v2.py
```

## 📊 **버전 비교표**

| 항목              | v1.0      | v2.0      | 개선도        |
| ----------------- | --------- | --------- | ------------- |
| **파일 구조**     | 단일 파일 | 모듈화    | **대폭 개선** |
| **코드 라인**     | 2,255줄   | 300-400줄 | **80% 감소**  |
| **유지보수성**    | 낮음      | 높음      | **대폭 개선** |
| **테스트 용이성** | 어려움    | 쉬움      | **대폭 개선** |
| **재사용성**      | 낮음      | 높음      | **대폭 개선** |
| **확장성**        | 제한적    | 높음      | **대폭 개선** |

## 🔧 **설정 관리**

### **환경별 설정**

- **개발 환경**: `v2.0/config/dev_settings.py`
- **테스트 환경**: `v2.0/config/test_settings.py`
- **운영 환경**: `v2.0/config/prod_settings.py`

### **버전별 의존성**

- **v1.0**: `requirements_v1.txt`
- **v2.0**: `requirements_v2.txt`
- **공통**: `shared/requirements.txt`
