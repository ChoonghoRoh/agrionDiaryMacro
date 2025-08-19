# 파일 분기 리팩토링 계획

## 현재 문제점

- `auto_diary_writer.py`가 2,255줄로 너무 큼
- 단일 책임 원칙 위반
- 유지보수 어려움
- 테스트 어려움

## 제안하는 파일 구조

### 1. `browser_manager.py` - 브라우저 관리

```python
class BrowserManager:
    - setup_driver()
    - _try_chrome()
    - _try_firefox()
    - login()
    - navigate_to_diary_main()
    - navigate_to_diary_detail()
```

### 2. `web_interactor.py` - 웹 요소 조작

```python
class WebInteractor:
    - set_date_range()
    - select_crop()
    - select_all_lands()
    - select_all_crops()
    - select_task_step()
    - enter_memo()
    - save_diary()
```

### 3. `schedule_processor.py` - 스케줄 처리

```python
class ScheduleProcessor:
    - load_schedule_data()
    - find_matching_tasks_by_date()
    - parse_farming_schedule()
    - match_task_with_gpt()
```

### 4. `content_generator_wrapper.py` - AI 내용 생성

```python
class ContentGeneratorWrapper:
    - generate_weather_aware_content()
    - generate_basic_diary_content()
    - get_weather_data()
```

### 5. `logger_manager.py` - 로깅 시스템

```python
class LoggerManager:
    - log_message()
    - recreate_log_file()
    - rotate_log_file()
    - find_last_processed_date_from_logs()
```

### 6. `error_handler.py` - 에러 처리

```python
class ErrorHandler:
    - recover_from_error()
    - recover_from_error_with_schedule()
    - setup_signal_handlers()
    - cleanup_and_exit()
```

### 7. `config_manager.py` - 설정 관리

```python
class ConfigManager:
    - auto_update_start_date()
    - update_settings_file()
    - update_env_file()
    - calculate_next_start_date()
```

### 8. `diary_processor.py` - 메인 처리 로직

```python
class DiaryProcessor:
    - process_single_diary()
    - process_single_diary_with_schedule()
    - process_basic_diary()
    - check_input_fields()
    - retry_input_fields()
```

### 9. `auto_diary_writer.py` - 메인 클래스 (간소화)

```python
class AgrionMacro:
    - __init__()  # 의존성 주입
    - run_macro()
    - run_test_mode()
```

## 장점

1. **단일 책임 원칙** 준수
2. **테스트 용이성** 향상
3. **코드 재사용성** 증가
4. **유지보수성** 향상
5. **가독성** 개선

## 구현 순서

1. 각 모듈별로 클래스 분리
2. 의존성 주입 패턴 적용
3. 인터페이스 정의
4. 단위 테스트 작성
5. 통합 테스트 수행
