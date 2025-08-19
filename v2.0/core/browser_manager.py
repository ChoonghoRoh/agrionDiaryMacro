import time
import random
import os
import signal
import atexit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.chrome import ChromeDriverManager
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'config'))

from settings import Config


class BrowserManager:
    """브라우저 드라이버 관리 및 기본 웹 네비게이션을 담당하는 클래스"""
    
    def __init__(self, logger_manager=None):
        self.driver = None
        self.wait = None
        self.logger_manager = logger_manager
        self.is_cleanup_done = False
        self.setup_driver()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """시그널 핸들러를 설정하여 프로그램 중단 시 로그를 안전하게 저장합니다."""
        def signal_handler(signum, frame):
            print(f"\n⚠️ 시그널 {signum}을 받았습니다. 로그를 안전하게 저장하고 종료합니다...")
            self.cleanup_and_exit()
            # 강제 종료
            os._exit(0)
        
        # SIGINT (Ctrl+C) 등록 (Windows에서 가장 안정적)
        signal.signal(signal.SIGINT, signal_handler)
        
        # SIGTERM은 Windows에서 제한적이므로 조건부 등록
        try:
            signal.signal(signal.SIGTERM, signal_handler)
        except (AttributeError, OSError):
            # Windows에서는 SIGTERM이 지원되지 않을 수 있음
            pass
        
        # 프로그램 종료 시 자동 정리 등록
        atexit.register(self.cleanup_and_exit)
    
    def cleanup_and_exit(self):
        """로그 파일을 안전하게 닫고 리소스를 정리합니다."""
        if self.is_cleanup_done:
            return  # 이미 cleanup이 완료됨
        
        self.is_cleanup_done = True
        print("\n🔄 리소스 정리 중...")
        
        try:
            # 로그 파일 정리
            if self.logger_manager:
                try:
                    self.logger_manager.log_message("📝 프로그램 종료 - 로그 파일을 안전하게 저장합니다.")
                    self.logger_manager.close_log_file()
                    print("✅ 로그 파일이 안전하게 저장되었습니다.")
                except Exception as log_error:
                    print(f"⚠️ 로그 파일 정리 중 오류: {log_error}")
            
            # 브라우저 드라이버 정리
            if self.driver:
                try:
                    print("🔄 브라우저 종료 중...")
                    self.driver.quit()
                    self.driver = None
                    print("✅ 브라우저가 안전하게 종료되었습니다.")
                except Exception as driver_error:
                    print(f"⚠️ 브라우저 종료 중 오류: {driver_error}")
                    # 브라우저가 응답하지 않을 경우 강제 종료
                    try:
                        import psutil
                        for proc in psutil.process_iter(['pid', 'name']):
                            if 'firefox' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower():
                                proc.terminate()
                    except:
                        pass
                        
        except Exception as e:
            print(f"⚠️ 정리 중 전체 오류 발생: {e}")
        
        print("✅ 리소스 정리 완료")
    
    def setup_driver(self):
        """브라우저 드라이버를 설정합니다. Firefox를 우선 사용합니다."""
        self.driver = None
        self.wait = None
        
        # Firefox 먼저 시도 (더 안정적)
        if self._try_firefox():
            return
        
        # Firefox 실패 시 Chrome 시도
        if self._try_chrome():
            return
        
        # 모든 브라우저 실패 시 오류 발생
        raise Exception("Firefox와 Chrome 모두 설치되지 않았습니다. 브라우저를 설치해주세요.")
    
    def _try_chrome(self):
        """Chrome 드라이버 설정을 시도합니다."""
        try:
            print("Chrome 드라이버 설정 시도 중...")
            chrome_options = ChromeOptions()
            # chrome_options.add_argument('--headless')  # 헤드리스 모드 (필요시 주석 해제)
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-extensions')
            chrome_options.add_argument('--disable-plugins')
            chrome_options.add_argument('--disable-images')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            try:
                # ChromeDriverManager 사용
                service = ChromeService(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
            except Exception as e1:
                print(f"ChromeDriverManager 실패: {e1}")
                # 시스템 Chrome 드라이버 사용 시도
                try:
                    self.driver = webdriver.Chrome(options=chrome_options)
                except Exception as e2:
                    print(f"시스템 Chrome 드라이버 실패: {e2}")
                    raise Exception(f"Chrome 드라이버 설정 실패: {e1}, {e2}")
            
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Chrome 드라이버 설정 완료!")
            return True
            
        except Exception as e:
            print(f"Chrome 드라이버 설정 실패: {e}")
            return False
    
    def _try_firefox(self):
        """Firefox 드라이버 설정을 시도합니다."""
        try:
            print("Firefox 드라이버 설정 시도 중...")
            firefox_options = FirefoxOptions()
            # firefox_options.add_argument('--headless')  # 헤드리스 모드 (필요시 주석 해제)
            
            # GeckoDriverManager 사용
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Firefox 드라이버 설정 완료!")
            return True
            
        except Exception as e:
            print(f"GeckoDriverManager 오류: {e}")
            print("시스템 Firefox 드라이버 사용 시도...")
            try:
                # 시스템에 설치된 Firefox 드라이버 사용
                self.driver = webdriver.Firefox(options=firefox_options)
                self.wait = WebDriverWait(self.driver, 10)
                print("✅ 시스템 Firefox 드라이버 설정 완료!")
                return True
            except Exception as e2:
                print(f"시스템 Firefox 드라이버 오류: {e2}")
                return False
    
    def login(self):
        """농업ON 사이트에 로그인합니다."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"로그인 시도 중... (시도 {attempt + 1}/{max_retries})")
                print("로그인 페이지로 이동 중...")
                self.driver.get(Config.LOGIN_URL)
                time.sleep(Config.FAST_WAIT_TIME)
                
                # 페이지 로딩 확인
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # 아이디 입력
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.ID, "memberId"))
                )
                username_input.clear()
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                username_input.send_keys(Config.USERNAME)
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                
                # 비밀번호 입력
                password_input = self.driver.find_element(By.ID, "pwd")
                password_input.clear()
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                password_input.send_keys(Config.PASSWORD)
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                
                # 로그인 버튼 클릭
                login_button = self.driver.find_element(By.CSS_SELECTOR, "div.btnCon > button.login")
                login_button.click()
                
                time.sleep(Config.FAST_LONG_WAIT_TIME)
                print("로그인 완료!")
                return
                
            except Exception as e:
                print(f"로그인 중 오류 발생 (시도 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"5초 후 재시도합니다...")
                    time.sleep(5)
                else:
                    print("최대 재시도 횟수 초과.")
                    raise
    
    def navigate_to_diary_main(self):
        """영농일지 메인 페이지로 이동합니다."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"영농일지 메인 페이지로 이동 중... (시도 {attempt + 1}/{max_retries})")
                self.driver.get(Config.DIARY_MAIN_URL)
                time.sleep(Config.FAST_WAIT_TIME)
                
                # 페이지 로딩 확인
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                print("영농일지 메인 페이지 이동 완료!")
                return
                
            except Exception as e:
                print(f"영농일지 메인 페이지 이동 중 오류 발생 (시도 {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    print(f"5초 후 재시도합니다...")
                    time.sleep(5)
                else:
                    print("최대 재시도 횟수 초과. 페이지 이동을 건너뜁니다.")
                    raise
    
    def navigate_to_diary_detail_from_main(self):
        """메인 페이지에서 영농일지 작성 페이지로 이동합니다."""
        try:
            print("메인 페이지에서 영농일지 작성 페이지로 이동 중...")
            
            # 영농일지 작성 링크 찾기 및 클릭
            diary_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.action_box > a[href*='goView'][href*='diaryMain']"))
            )
            diary_link.click()
            
            time.sleep(Config.FAST_WAIT_TIME)
            print("영농일지 작성 페이지 이동 완료!")
            
        except Exception as e:
            print(f"영농일지 작성 페이지 이동 중 오류 발생: {e}")
            # 링크 클릭이 실패하면 메인 페이지로 이동
            try:
                print("링크 클릭 실패, 메인 페이지로 이동...")
                self.driver.get(Config.DIARY_MAIN_URL)
                time.sleep(Config.FAST_WAIT_TIME)
                print("메인 페이지로 이동 완료!")
            except Exception as fallback_error:
                print(f"메인 페이지 이동도 실패: {fallback_error}")
                raise
    
    def navigate_to_diary_detail(self):
        """영농일지 상세 등록 페이지로 이동합니다."""
        try:
            print("영농일지 상세 등록 페이지로 이동 중...")
            self.driver.get(Config.DIARY_DETAIL_URL)
            time.sleep(Config.FAST_WAIT_TIME)
            print("영농일지 상세 등록 페이지 이동 완료!")
            
        except Exception as e:
            print(f"영농일지 상세 등록 페이지 이동 중 오류 발생: {e}")
            raise
    
    def get_driver(self):
        """드라이버 인스턴스를 반환합니다."""
        return self.driver
    
    def get_wait(self):
        """WebDriverWait 인스턴스를 반환합니다."""
        return self.wait
