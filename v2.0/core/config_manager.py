import os
import re
from datetime import datetime, timedelta
import sys
import shutil

# v2.0의 config 디렉토리에서 settings 임포트
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

from settings import Config


class ConfigManager:
    """설정 파일 관리를 담당하는 클래스"""
    
    def __init__(self, logger_manager=None):
        self.logger_manager = logger_manager
        # .env 파일 검증
        self.validate_env_file()
    
    def validate_env_file(self):
        """환경 변수 파일이 올바르게 설정되었는지 검증합니다."""
        try:
            # 필수 환경 변수 확인
            required_vars = ['AGRION_USERNAME', 'AGRION_PASSWORD']
            missing_vars = []
            
            for var in required_vars:
                value = getattr(Config, var, None)
                if not value or value == '':
                    missing_vars.append(var)
            
            if missing_vars:
                print("❌ 필수 환경 변수가 설정되지 않았습니다:")
                for var in missing_vars:
                    print(f"   - {var}")
                print("\n📝 .env 파일을 생성하고 다음 내용을 입력하세요:")
                print("=" * 50)
                print("# 로그인 정보 (필수)")
                print("AGRION_USERNAME=your_username_here")
                print("AGRION_PASSWORD=your_password_here")
                print("=" * 50)
                print("\n💡 .env 파일 위치:")
                print("   - v2.0/.env")
                print("   - 프로젝트 루트/.env")
                print("   - shared/.env")
                return False
            
            print("✅ 환경 변수 설정 확인 완료")
            return True
            
        except Exception as e:
            print(f"⚠️ 환경 변수 검증 중 오류: {e}")
            return False
    
    def auto_update_start_date(self):
        """로그를 분석해서 시작일을 자동으로 업데이트합니다."""
        try:
            print("🔄 시작일 자동 업데이트 중...")
            
            if not self.logger_manager:
                print("⚠️ 로거가 없어 자동 업데이트를 건너뜁니다.")
                return Config.START_DATE
            
            # 로그에서 마지막 처리된 날짜 찾기
            last_date = self.logger_manager.find_last_processed_date_from_logs()
            
            if last_date:
                # 다음 시작일 계산
                next_start_date = self.calculate_next_start_date(last_date)
                
                if next_start_date:
                    # settings.py 파일 업데이트
                    self.update_settings_file(next_start_date)
                    
                    # .env 파일도 업데이트
                    env_updated = self.update_env_file(next_start_date)
                    if env_updated:
                        print(f"✅ 시작일이 {next_start_date}로 자동 업데이트되었습니다. (settings.py + .env)")
                    else:
                        print(f"✅ 시작일이 {next_start_date}로 자동 업데이트되었습니다. (settings.py만)")
                    
                    return next_start_date
                else:
                    print("⚠️ 다음 시작일 계산 실패")
            else:
                print("⚠️ 로그에서 마지막 처리 날짜를 찾을 수 없음")
            
            print("⚠️ 자동 업데이트를 건너뛰고 설정된 시작일을 사용합니다.")
            return Config.START_DATE
            
        except Exception as e:
            print(f"⚠️ 자동 업데이트 실패: {e}")
            import traceback
            traceback.print_exc()
            return Config.START_DATE
    
    def calculate_next_start_date(self, last_date_str):
        """마지막 처리된 날짜를 기반으로 다음 시작일을 계산합니다."""
        try:
            if not last_date_str:
                return None
                
            # 마지막 처리된 날짜 파싱
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
            
            # 다음 주차의 시작일 계산 (7일 후)
            next_start_date = last_date + timedelta(days=Config.DIARY_INTERVAL_DAYS)
            
            print(f"📅 마지막 처리 날짜: {last_date_str}")
            print(f"📅 다음 시작 날짜: {next_start_date.strftime('%Y-%m-%d')}")
            
            return next_start_date.strftime('%Y-%m-%d')
            
        except Exception as e:
            print(f"⚠️ 다음 시작일 계산 실패: {e}")
            return None
    
    def update_settings_file(self, new_start_date):
        """settings.py 파일의 START_DATE를 업데이트합니다."""
        try:
            settings_file = 'settings.py'
            
            # 파일 읽기
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # START_DATE 라인 찾기 및 교체
            pattern = r"START_DATE = '([^']*)'"
            replacement = f"START_DATE = '{new_start_date}'"
            updated_content = re.sub(pattern, replacement, content)
            
            # 파일 쓰기
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            print(f"✅ settings.py 파일이 업데이트되었습니다: {new_start_date}")
            
            # Python 모듈 캐시 무효화 및 다시 로드
            import importlib
            import settings
            importlib.reload(settings)
            print(f"✅ settings 모듈이 다시 로드되었습니다.")
            
        except Exception as e:
            print(f"❌ settings.py 파일 업데이트 실패: {e}")
            raise
    
    def update_env_file(self, new_start_date):
        """환경 변수 파일(.env)의 START_DATE를 업데이트합니다."""
        try:
            env_file = '.env'
            
            # .env 파일이 없으면 생성
            if not os.path.exists(env_file):
                print("⚠️ .env 파일이 없습니다. .env.example을 복사하여 생성합니다.")
                if os.path.exists('.env.example'):
                    import shutil
                    shutil.copy('.env.example', env_file)
                else:
                    print("❌ .env.example 파일도 없습니다.")
                    return False
            
            # 파일 읽기
            with open(env_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # START_DATE 라인 찾기 및 교체
            if 'START_DATE=' in content:
                # 기존 START_DATE 라인 교체
                pattern = r'START_DATE=([^\n]*)'
                replacement = f'START_DATE={new_start_date}'
                updated_content = re.sub(pattern, replacement, content)
            else:
                # START_DATE 라인이 없으면 추가
                updated_content = content + f'\nSTART_DATE={new_start_date}'
            
            # 파일 쓰기
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            print(f"✅ .env 파일이 업데이트되었습니다: {new_start_date}")
            return True
            
        except Exception as e:
            print(f"❌ .env 파일 업데이트 실패: {e}")
            return False
