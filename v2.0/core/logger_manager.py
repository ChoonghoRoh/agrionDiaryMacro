import os
import re
from datetime import datetime


class LoggerManager:
    """로깅 시스템을 관리하는 클래스"""
    
    def __init__(self, log_filename=None):
        self.log_file = None
        self.log_filename = log_filename
        self.setup_log_file()
    
    def setup_log_file(self):
        """로그 파일을 설정합니다."""
        try:
            if not self.log_filename:
                # log 폴더가 없으면 생성
                os.makedirs('log', exist_ok=True)
                self.log_filename = f"log/diary_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            self.log_file = open(self.log_filename, 'w', encoding='utf-8')
            print(f"📝 로그 파일 생성: {self.log_filename}")
            
        except Exception as e:
            print(f"❌ 로그 파일 생성 실패: {e}")
            self.log_file = None
    
    def log_message(self, message):
        """메시지를 콘솔과 로그 파일에 출력합니다."""
        print(message)
        if self.log_file:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_entry = f"[{timestamp}] {message}\n"
                self.log_file.write(log_entry)
                self.log_file.flush()  # 즉시 파일에 쓰기
                
                # 로그 파일 크기 확인 (100MB 이상이면 새 파일 생성)
                if self.log_file.tell() > 100 * 1024 * 1024:  # 100MB
                    self.rotate_log_file()
                    
            except Exception as e:
                print(f"⚠️ 로그 파일 쓰기 실패: {e}")
                # 로그 파일이 손상된 경우 새로 생성
                self.recreate_log_file()
    
    def recreate_log_file(self):
        """로그 파일을 다시 생성합니다."""
        try:
            if self.log_file:
                self.log_file.close()
            
            if self.log_filename:
                self.log_file = open(self.log_filename, 'a', encoding='utf-8')
                self.log_message("📝 로그 파일이 재생성되었습니다.")
        except Exception as e:
            print(f"❌ 로그 파일 재생성 실패: {e}")
            self.log_file = None
    
    def rotate_log_file(self):
        """로그 파일이 너무 커지면 새 파일로 로테이션합니다."""
        try:
            if self.log_file and self.log_filename:
                self.log_file.close()
                
                # 기존 파일명에 타임스탬프 추가
                base_name = self.log_filename.replace('.txt', '')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                new_filename = f"{base_name}_{timestamp}.txt"
                
                # 기존 파일을 새 이름으로 이동
                if os.path.exists(self.log_filename):
                    os.rename(self.log_filename, new_filename)
                    print(f"📝 로그 파일이 로테이션되었습니다: {new_filename}")
                
                # 새 로그 파일 생성
                self.log_filename = f"log/diary_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                self.log_file = open(self.log_filename, 'w', encoding='utf-8')
                self.log_message("📝 새 로그 파일이 생성되었습니다.")
                
        except Exception as e:
            print(f"❌ 로그 파일 로테이션 실패: {e}")
            # 로테이션 실패 시 기존 파일에 계속 쓰기
            if self.log_filename:
                self.log_file = open(self.log_filename, 'a', encoding='utf-8')
    
    def close_log_file(self):
        """로그 파일을 안전하게 닫습니다."""
        try:
            if self.log_file:
                self.log_file.flush()
                self.log_file.close()
                self.log_file = None
                print(f"✅ 로그 파일이 안전하게 저장되었습니다: {self.log_filename}")
        except Exception as e:
            print(f"⚠️ 로그 파일 닫기 중 오류: {e}")
    
    def find_last_processed_date_from_logs(self):
        """로그 파일에서 마지막으로 처리된 날짜를 찾습니다."""
        try:
            print("🔍 로그에서 마지막 처리 날짜를 찾는 중...")
            
            # 로그 파일들 찾기 (log 폴더에서)
            log_files = []
            log_dir = 'log'
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.startswith('diary_log_') and file.endswith('.txt'):
                        log_files.append(os.path.join(log_dir, file))
            else:
                # log 폴더가 없으면 현재 디렉토리에서 찾기 (기존 호환성)
                for file in os.listdir('.'):
                    if file.startswith('diary_log_') and file.endswith('.txt'):
                        log_files.append(file)
            
            if not log_files:
                print("📝 로그 파일이 없습니다. 새로 생성합니다.")
                return None
            
            # 가장 최근 로그 파일 찾기
            latest_log = max(log_files, key=os.path.getctime)
            print(f"📄 최근 로그 파일: {latest_log}")
            
            # 로그 파일 읽기
            with open(latest_log, 'r', encoding='utf-8') as f:
                log_content = f.read()
            
            # 마지막으로 처리된 날짜 패턴 찾기
            # "✅ 2024-02-17 논갈이(쟁기)작업 영농일지 등록 완료!" 패턴
            # "✅ 2021-02-01 ~ 2021-02-07 영농일지 등록 완료" 패턴
            date_pattern = r'✅ (\d{4}-\d{2}-\d{2}) .* 영농일지 등록 완료'
            matches = re.findall(date_pattern, log_content)
            
            if matches:
                last_date = matches[-1]  # 마지막 매치
                print(f"📅 마지막 처리 날짜 발견: {last_date}")
                return last_date
            else:
                print("📝 로그에서 완료된 영농일지 날짜를 찾을 수 없습니다.")
                return None
            
        except Exception as e:
            print(f"⚠️ 로그 분석 실패: {e}")
            return None
    
    def get_log_filename(self):
        """로그 파일명을 반환합니다."""
        return self.log_filename
