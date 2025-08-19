# 빠른 참조 가이드

## 🚀 v2.0 실행 방법
```bash
# 방법 1: 버전 선택 메뉴
python run.py

# 방법 2: v2.0 직접 실행
cd v2.0
python main/start_diary_writer_v2.py
```

## 🔧 주요 수정사항

### .env 파일 설정
```bash
# v2.0/.env 파일 생성
AGRION_USERNAME=your_username
AGRION_PASSWORD=your_password
START_DATE=2021-06-27
END_DATE=2023-12-31
```

### 문제 해결
1. **SyntaxError**: `v2.0/core/schedule_processor.py` 들여쓰기 수정 완료
2. **.env 로드**: 여러 경로에서 .env 파일 검색
3. **환경 변수 검증**: 필수 변수 자동 확인

## 📁 핵심 파일들
- `v2.0/config/settings.py` - 환경 변수 로드
- `v2.0/core/config_manager.py` - 설정 관리
- `v2.0/core/schedule_processor.py` - 일정 처리
- `run.py` - 버전 선택

## ⚠️ 주의사항
- .env 파일은 git에 커밋되지 않음
- 필수 환경 변수: AGRION_USERNAME, AGRION_PASSWORD
