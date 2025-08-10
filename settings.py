import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # 로그인 정보
    USERNAME = os.getenv('AGRION_USERNAME', '')
    PASSWORD = os.getenv('AGRION_PASSWORD', '')
    
    # 날짜 설정 (2021년부터 2023년까지 벼 재배 전체 기간)
    START_DATE = '2021-02-01'  # 2021년 2월 1일부터 시작
    END_DATE = '2023-12-31'    # 2023년 12월 31일까지
    
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
