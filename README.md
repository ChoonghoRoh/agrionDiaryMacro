# 🌾 농업ON 영농일지 자동 등록 매크로

농업ON 사이트에서 영농일지를 자동으로 등록하는 Python 매크로입니다.

## 📁 프로젝트 구조

```
agrionDiaryMacro/
├── 📦 v1.0/                    # 기존 버전 (단일 파일 구조)
├── 📦 v2.0/                    # 리팩토링 버전 (모듈화 구조)
├── 📦 shared/                  # 공통 리소스
└── 📦 docs/                    # 문서
```

## 🚀 빠른 시작

### v1.0 (기존 버전) 실행

```bash
cd v1.0
python start_diary_writer.py
```

### v2.0 (리팩토링 버전) 실행

```bash
cd v2.0
python main/start_diary_writer_v2.py
```

## 📊 버전 비교

| 항목              | v1.0      | v2.0      | 개선도        |
| ----------------- | --------- | --------- | ------------- |
| **파일 구조**     | 단일 파일 | 모듈화    | **대폭 개선** |
| **코드 라인**     | 2,255줄   | 300-400줄 | **80% 감소**  |
| **유지보수성**    | 낮음      | 높음      | **대폭 개선** |
| **테스트 용이성** | 어려움    | 쉬움      | **대폭 개선** |
| **재사용성**      | 낮음      | 높음      | **대폭 개선** |

## 🔧 설치 및 설정

### 1. 의존성 설치

```bash
pip install -r shared/requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 입력하세요:

```env
AGRION_USERNAME=your_username
AGRION_PASSWORD=your_password
START_DATE=2025-01-01
END_DATE=2025-12-31
CROP_TYPE=벼
OPENAI_API_KEY=your_openai_api_key
```

## 📖 자세한 문서

- [v1.0 문서](docs/v1.0_documentation.md)
- [v2.0 문서](docs/v2.0_documentation.md)
- [마이그레이션 가이드](docs/migration_guide.md)

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요.
