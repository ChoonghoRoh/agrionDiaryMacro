import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드 (v2.0 디렉토리에서 실행할 때 상위 디렉토리의 .env 파일도 찾기)
current_dir = os.path.dirname(os.path.abspath(__file__))
v2_dir = os.path.dirname(current_dir)  # v2.0 디렉토리
root_dir = os.path.dirname(v2_dir)     # 프로젝트 루트 디렉토리

# 여러 위치에서 .env 파일 찾기
env_paths = [
    os.path.join(current_dir, '.env'),           # v2.0/config/.env
    os.path.join(v2_dir, '.env'),                # v2.0/.env
    os.path.join(root_dir, '.env'),              # 루트/.env
    os.path.join(root_dir, 'shared', '.env'),    # shared/.env
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ .env 파일 로드됨: {env_path}")
        break
else:
    print("⚠️ .env 파일을 찾을 수 없습니다. 기본값을 사용합니다.")
    # .env 파일이 없으면 기본값만 사용

class Config:
    # 로그인 정보
    USERNAME = os.getenv('AGRION_USERNAME', '')
    PASSWORD = os.getenv('AGRION_PASSWORD', '')
    
    # 날짜 설정 (.env 파일에서 읽기, 기본값 설정)
    START_DATE = os.getenv('START_DATE', '2021-06-27')  # 시작일 지정
    END_DATE = os.getenv('END_DATE', '2023-12-31')      # 종료일 지정
    

    # 영농일지 등록 간격 설정
    DIARY_INTERVAL_DAYS = 7    # 영농일지 등록 간격 (일) - 7일 = 1주일 간격
    
    # 품목 설정
    CROP_TYPE = os.getenv('CROP_TYPE', '벼')  # 품목 (예: 벼, 감자, 고구마 등)
    
    # OpenAI API 설정 (작업 내용 생성용)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    USE_GPT = os.getenv('USE_GPT', 'true').lower() == 'true'  # GPT 사용 여부 (기본값: true)
    
    # GPT 모델 설정 (가격 변동 시 쉽게 변경 가능)
    GPT_MODEL = os.getenv('GPT_MODEL', 'gpt-4o-mini')  # 사용할 GPT 모델
    GPT_MAX_TOKENS = int(os.getenv('GPT_MAX_TOKENS', '50'))  # 최대 토큰 수
    GPT_TEMPERATURE = float(os.getenv('GPT_TEMPERATURE', '0.7'))  # 창의성 수준 (0.0-1.0)
    
    # 웹사이트 URL
    LOGIN_URL = 'https://www.agrion.kr/portal/gc/ml/mberLoginForm.do'
    DIARY_MAIN_URL = 'https://www.agrion.kr/portal/farm/diaryMain.do'
    DIARY_DETAIL_URL = 'https://www.agrion.kr/portal/farm/diaryDetail.do'
    
    # 대기 시간 설정 (서버 안정성을 위해 증가)
    WAIT_TIME = 8  # 기본 대기 시간 (초) - 서버 안정성 향상
    LONG_WAIT_TIME = 12  # 긴 대기 시간 (초) - 서버 안정성 향상
    
    # 빠른 입력을 위한 딜레이 설정
    FAST_WAIT_TIME = 4  # 빠른 기본 대기 시간 (초)
    FAST_LONG_WAIT_TIME = 6  # 빠른 긴 대기 시간 (초)
    
    # 입력 간 딜레이 설정 (초)
    INPUT_DELAY_MIN = 0.3  # 최소 입력 딜레이
    INPUT_DELAY_MAX = 0.8  # 최대 입력 딜레이
    
    # 선택 간 딜레이 설정 (초)
    SELECT_DELAY_MIN = 0.5  # 최소 선택 딜레이
    SELECT_DELAY_MAX = 1.2  # 최대 선택 딜레이
    
    # 서버 로딩 대기 시간 (초)
    SERVER_LOAD_DELAY_MIN = 0.8  # 최소 서버 로딩 대기
    SERVER_LOAD_DELAY_MAX = 1.5  # 최대 서버 로딩 대기
