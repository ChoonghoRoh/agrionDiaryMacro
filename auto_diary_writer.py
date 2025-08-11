import time
import random
import json
import re
import os
import signal
import atexit
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from settings import Config
from ai_GPT_diary_content_generator import ContentGenerator

class AgrionMacro:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.content_generator = ContentGenerator()
        self.schedule_data = None
        self.log_file = None
        self.log_filename = None
        self.setup_driver()
        self.load_schedule_data()
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """시그널 핸들러를 설정하여 프로그램 중단 시 로그를 안전하게 저장합니다."""
        def signal_handler(signum, frame):
            print(f"\n⚠️ 시그널 {signum}을 받았습니다. 로그를 안전하게 저장하고 종료합니다...")
            self.cleanup_and_exit()
        
        # SIGINT (Ctrl+C), SIGTERM 등록
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 프로그램 종료 시 자동 정리 등록
        atexit.register(self.cleanup_and_exit)
    
    def cleanup_and_exit(self):
        """로그 파일을 안전하게 닫고 리소스를 정리합니다."""
        try:
            if self.log_file:
                self.log_message("📝 프로그램 종료 - 로그 파일을 안전하게 저장합니다.")
                self.log_file.flush()
                self.log_file.close()
                self.log_file = None
                print(f"✅ 로그 파일이 안전하게 저장되었습니다: {self.log_filename}")
            
            if self.driver:
                self.driver.quit()
                print("✅ 브라우저가 안전하게 종료되었습니다.")
                
        except Exception as e:
            print(f"⚠️ 정리 중 오류 발생: {e}")
    
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
    
    def load_schedule_data(self):
        """농작업 일정 데이터를 로드합니다."""
        try:
            with open('data/rice_schedule_data.json', 'r', encoding='utf-8') as f:
                self.schedule_data = json.load(f)
            print("✅ 농작업 일정 데이터 로드 완료")
        except Exception as e:
            print(f"❌ 농작업 일정 데이터 로드 실패: {e}")
            self.schedule_data = None
        
    def setup_driver(self):
        """Firefox 드라이버를 설정합니다."""
        firefox_options = Options()
        # firefox_options.add_argument('--headless')  # 헤드리스 모드 (필요시 주석 해제)
        
        try:
            # GeckoDriverManager 사용
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
        except Exception as e:
            print(f"GeckoDriverManager 오류: {e}")
            print("시스템 Firefox 드라이버 사용 시도...")
            try:
                # 시스템에 설치된 Firefox 드라이버 사용
                self.driver = webdriver.Firefox(options=firefox_options)
            except Exception as e2:
                print(f"시스템 Firefox 드라이버 오류: {e2}")
                print("Firefox 브라우저가 설치되어 있는지 확인하세요.")
                raise
        
        self.wait = WebDriverWait(self.driver, 10)
        
    def login(self):
        """농업ON 사이트에 로그인합니다."""
        try:
            print("로그인 페이지로 이동 중...")
            self.driver.get(Config.LOGIN_URL)
            time.sleep(Config.FAST_WAIT_TIME)
            
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
            
        except Exception as e:
            print(f"로그인 중 오류 발생: {e}")
            raise
            
    def navigate_to_diary_main(self):
        """영농일지 메인 페이지로 이동합니다."""
        try:
            print("영농일지 메인 페이지로 이동 중...")
            self.driver.get(Config.DIARY_MAIN_URL)
            time.sleep(Config.FAST_WAIT_TIME)
            print("영농일지 메인 페이지 이동 완료!")
            
        except Exception as e:
            print(f"영농일지 메인 페이지 이동 중 오류 발생: {e}")
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
            
    def set_date_range(self, start_date, end_date):
        """시작일과 종료일을 설정합니다."""
        try:
            print(f"날짜 설정: {start_date} ~ {end_date}")
            
            # 시작일 설정
            start_date_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "now_date_s"))
            )
            
            # datepicker 클릭하여 달력 열기
            start_date_input.click()
            time.sleep(random.uniform(Config.SELECT_DELAY_MIN, Config.SELECT_DELAY_MAX))
            
            # 날짜 파싱
            start_year, start_month, start_day = map(int, start_date.split('-'))
            
            # 연도 선택
            year_select = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-year")
            year_options = Select(year_select)
            year_options.select_by_value(str(start_year))
            time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            # 월 선택 (0부터 시작하므로 -1)
            month_select = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-month")
            month_options = Select(month_select)
            month_options.select_by_value(str(start_month - 1))  # 0부터 시작
            time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            # 일 선택 (선택 가능한 날짜만)
            day_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ui-datepicker-calendar td[data-handler='selectDay'] a")
            for day_element in day_elements:
                if day_element.text == str(start_day):
                    day_element.click()
                    break
            
            time.sleep(random.uniform(Config.SELECT_DELAY_MIN, Config.SELECT_DELAY_MAX))
            
            # 종료일 설정
            end_date_input = self.driver.find_element(By.ID, "now_date_e")
            end_date_input.click()
            time.sleep(random.uniform(Config.SELECT_DELAY_MIN, Config.SELECT_DELAY_MAX))
            
            # 종료일 파싱
            end_year, end_month, end_day = map(int, end_date.split('-'))
            
            # 종료일 연도 선택
            year_select = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-year")
            year_options = Select(year_select)
            year_options.select_by_value(str(end_year))
            time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            # 종료일 월 선택 (0부터 시작하므로 -1)
            month_select = self.driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-month")
            month_options = Select(month_select)
            month_options.select_by_value(str(end_month - 1))  # 0부터 시작
            time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            # 종료일 일 선택 (선택 가능한 날짜만)
            day_elements = self.driver.find_elements(By.CSS_SELECTOR, ".ui-datepicker-calendar td[data-handler='selectDay'] a")
            for day_element in day_elements:
                if day_element.text == str(end_day):
                    day_element.click()
                    break
            
            time.sleep(random.uniform(Config.SELECT_DELAY_MIN, Config.SELECT_DELAY_MAX))
            print("날짜 설정 완료!")
            
        except Exception as e:
            print(f"날짜 설정 중 오류 발생: {e}")
            # datepicker 방식이 실패하면 기존 방식으로 fallback
            try:
                print("datepicker 방식 실패, 직접 입력 방식으로 시도...")
                start_date_input = self.wait.until(
                    EC.presence_of_element_located((By.ID, "now_date_s"))
                )
                self.driver.execute_script("arguments[0].value = arguments[1]", start_date_input, start_date)
                
                end_date_input = self.driver.find_element(By.ID, "now_date_e")
                self.driver.execute_script("arguments[0].value = arguments[1]", end_date_input, end_date)
                
                time.sleep(1)
                print("직접 입력 방식으로 날짜 설정 완료!")
            except Exception as fallback_error:
                print(f"날짜 설정 완전 실패: {fallback_error}")
                raise
            
    def select_crop(self):
        """품목을 선택합니다."""
        try:
            print(f"품목 선택: {Config.CROP_TYPE}")
            
            # 품목 선택 드롭다운 클릭
            crop_select = self.wait.until(
                EC.element_to_be_clickable((By.ID, "selectCrops"))
            )
            crop_select.click()
            time.sleep(random.uniform(Config.SELECT_DELAY_MIN, Config.SELECT_DELAY_MAX))
            
            # 품목 옵션들 찾기
            options = self.driver.find_elements(By.CSS_SELECTOR, "#selectCrops option")
            print(f"발견된 품목 옵션 수: {len(options)}")
            
            # 품목 옵션 찾기
            found = False
            for i, option in enumerate(options):
                print(f"옵션 {i}: {option.text}")
                if Config.CROP_TYPE in option.text:
                    option.click()
                    found = True
                    print(f"품목 선택됨: {option.text}")
                    break
            
            if not found:
                # 기본값 선택 (첫 번째 옵션)
                if len(options) > 0:
                    options[0].click()
                    print(f"'{Config.CROP_TYPE}'을 찾을 수 없어 첫 번째 옵션을 선택했습니다: {options[0].text}")
                else:
                    print("선택 가능한 품목이 없습니다.")
            
            # 서버 전송을 위한 대기
            print("서버에서 필지 목록을 로드하는 중...")
            time.sleep(random.uniform(Config.SERVER_LOAD_DELAY_MIN, Config.SERVER_LOAD_DELAY_MAX))
            print("품목 선택 완료!")
            
        except Exception as e:
            print(f"품종 선택 중 오류 발생: {e}")
            # 오류 발생 시에도 계속 진행
            print("품종 선택을 건너뛰고 계속 진행합니다.")
            
    def select_all_lands(self):
        """모든 필지를 선택합니다."""
        try:
            print("모든 필지 선택 중...")
            
            # 필지 목록 대기
            time.sleep(Config.FAST_WAIT_TIME)
            
            # 필지 체크박스들 찾기
            land_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "#checkLand input[type='checkbox']")
            print(f"발견된 필지 체크박스 수: {len(land_checkboxes)}")
            
            if land_checkboxes:
                for i, checkbox in enumerate(land_checkboxes):
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        print(f"필지 {i+1} 선택됨")
                        time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                print(f"{len(land_checkboxes)}개 필지 선택 완료!")
                
                # 서버 전송을 위한 대기
                print("서버에서 품종 목록을 로드하는 중...")
                time.sleep(random.uniform(Config.SERVER_LOAD_DELAY_MIN, Config.SERVER_LOAD_DELAY_MAX))
            else:
                print("선택 가능한 필지가 없습니다.")
                print("필지 목록이 로드되지 않았을 수 있습니다.")
                
        except Exception as e:
            print(f"필지 선택 중 오류 발생: {e}")
            
    def select_all_crops(self):
        """모든 품종을 선택합니다."""
        try:
            print("모든 품종 선택 중...")
            
            # 품목 목록 대기
            time.sleep(Config.FAST_WAIT_TIME)
            
            # 품종 체크박스들 찾기
            crop_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "#checkScrop input[type='checkbox']")
            print(f"발견된 품종 체크박스 수: {len(crop_checkboxes)}")
            
            if crop_checkboxes:
                for i, checkbox in enumerate(crop_checkboxes):
                    if not checkbox.is_selected():
                        self.driver.execute_script("arguments[0].click();", checkbox)
                        print(f"품종 {i+1} 선택됨")
                        time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                print(f"{len(crop_checkboxes)}개 품종 선택 완료!")
                
                # 서버 전송을 위한 대기 (단축)
                print("서버에서 작업단계 목록을 로드하는 중...")
                time.sleep(0.5)
            else:
                print("선택 가능한 품종이 없습니다.")
                print("품종 목록이 로드되지 않았을 수 있습니다.")
                
        except Exception as e:
            print(f"품목 선택 중 오류 발생: {e}")
            
    def get_weather_data(self):
        """영농일지 페이지에서 날씨 정보를 수집합니다."""
        try:
            # 날씨 정보 요소들 찾기
            weather_select = self.driver.find_element(By.ID, "wfKor")
            low_temp = self.driver.find_element(By.ID, "low_temp").get_attribute("value")
            high_temp = self.driver.find_element(By.ID, "high_temp").get_attribute("value")
            rainfall = self.driver.find_element(By.ID, "r12").get_attribute("value")
            humidity = self.driver.find_element(By.ID, "reh").get_attribute("value")
            
            weather_data = {
                "weather": weather_select.get_attribute("value"),
                "low_temp": low_temp,
                "high_temp": high_temp,
                "rainfall": rainfall,
                "humidity": humidity
            }
            
            print(f"🌤️ 날씨 정보 수집: {weather_data['weather']}, 기온: {low_temp}°C~{high_temp}°C")
            return weather_data
            
        except Exception as e:
            print(f"⚠️ 날씨 데이터 수집 실패: {e}")
            return None
    
    def parse_date_to_month_day(self, date_str):
        """날짜 문자열을 월-일 형식으로 변환합니다."""
        try:
            # "2025-03-15" -> "03-15"
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%m-%d")
        except Exception as e:
            print(f"날짜 파싱 오류: {e}")
            return None
    
    def is_date_in_period_with_tolerance(self, selected_date, period_range, tolerance_days=15):
        """선택된 날짜가 기간 범위에 포함되는지 확인 (+-15일 여유)"""
        try:
            # 기간 파싱 (예: "03-01 ~ 05-10")
            start_str, end_str = period_range.split(" ~ ")
            start_month, start_day = map(int, start_str.split("-"))
            end_month, end_day = map(int, end_str.split("-"))
            
            # 선택된 날짜 파싱
            selected_month, selected_day = map(int, selected_date.split("-"))
            
            # 시작일과 종료일 계산 (2025년 기준)
            start_date = datetime(2025, start_month, start_day) - timedelta(days=tolerance_days)
            end_date = datetime(2025, end_month, end_day) + timedelta(days=tolerance_days)
            selected_date_obj = datetime(2025, selected_month, selected_day)
            
            return start_date <= selected_date_obj <= end_date
            
        except Exception as e:
            print(f"기간 비교 오류: {e}")
            return False
    
    def find_matching_tasks_by_date(self, selected_date):
        """선택된 날짜에 해당하는 작업들을 찾습니다."""
        if not self.schedule_data:
            print("❌ 농작업 일정 데이터가 없습니다.")
            return []
        
        matching_tasks = []
        month_day = self.parse_date_to_month_day(selected_date)
        
        if not month_day:
            return []
        
        # JSON 데이터에서 해당 날짜의 작업들 찾기
        for month_key, month_data in self.schedule_data.items():
            for stage_key, stage_tasks in month_data.items():
                for task in stage_tasks:
                    if self.is_date_in_period_with_tolerance(month_day, task["기간"]):
                        matching_tasks.append({
                            "작업명": task["작업명"],
                            "기간": task["기간"],
                            "설명": task["설명"],
                            "단계": stage_key
                        })
        
        print(f"📅 {selected_date}에 해당하는 작업 {len(matching_tasks)}개 발견")
        for task in matching_tasks:
            print(f"  - {task['작업명']} ({task['기간']})")
        
        return matching_tasks
    
    def get_available_task_steps(self):
        """웹페이지에서 사용 가능한 작업단계 목록을 가져옵니다."""
        try:
            # 페이지 안정화를 위한 대기 (단축)
            time.sleep(1)
            
            # 작업단계 선택 드롭다운 찾기
            task_select = self.wait.until(
                EC.presence_of_element_located((By.ID, "selectTask"))
            )
            
            # 드롭다운 클릭하여 옵션 로드 (빠른 방식)
            try:
                task_select.click()
                time.sleep(0.3)  # 빠른 대기
                print("✅ 작업단계 드롭다운 클릭 성공")
            except Exception as click_error:
                print(f"⚠️ 드롭다운 클릭 실패, JavaScript로 시도: {click_error}")
                self.driver.execute_script("arguments[0].click();", task_select)
                time.sleep(0.3)  # 빠른 대기
            
            # 작업단계 옵션들 찾기 (빠른 시도)
            max_retries = 2  # 시도 횟수 줄임
            options = []
            
            for retry in range(max_retries):
                try:
                    options = self.driver.find_elements(By.CSS_SELECTOR, "#selectTask option")
                    if options:
                        print(f"✅ 작업단계 옵션 로드 성공 (시도 {retry + 1})")
                        break
                    else:
                        print(f"⚠️ 작업단계 옵션 없음 (시도 {retry + 1})")
                        time.sleep(0.5)  # 대기 시간 단축
                except Exception as find_error:
                    print(f"⚠️ 작업단계 옵션 찾기 실패 (시도 {retry + 1}): {find_error}")
                    time.sleep(0.5)  # 대기 시간 단축
            
            print(f"발견된 작업단계 옵션 수: {len(options)}")
            
            # 모든 옵션 가져오기 (제외할 작업 필터링)
            available_tasks = []
            excluded_tasks = ["출하/판매작업", "병해충 피해"]  # 제외할 작업들
            
            for i, option in enumerate(options):
                option_text = option.text.strip()
                option_value = option.get_attribute("value")
                if option_text and option_text != "작업단계 선택" and option_value:
                    # 제외할 작업인지 확인
                    if any(excluded in option_text for excluded in excluded_tasks):
                        print(f"   ⚠️  제외됨: {option_text}")
                        continue
                    
                    available_tasks.append(option_text)
                    print(f"작업단계 옵션 {i}: {option_text} (value: {option_value})")
            
            # 디버깅: 모든 옵션 출력
            if not available_tasks:
                print("⚠️ 사용 가능한 작업단계가 없습니다. 모든 옵션을 확인합니다:")
                for i, option in enumerate(options):
                    option_text = option.text.strip()
                    option_value = option.get_attribute("value")
                    print(f"  옵션 {i}: '{option_text}' (value: '{option_value}')")
            
            print(f"📋 사용 가능한 작업단계 {len(available_tasks)}개:")
            for i, task in enumerate(available_tasks, 1):
                print(f"  {i:2d}. {task}")
            
            return available_tasks
            
        except Exception as e:
            print(f"❌ 작업단계 목록 가져오기 실패: {e}")
            return []
    
    def match_task_with_gpt(self, json_task_name, available_tasks):
        """GPT를 사용하여 JSON 작업명과 웹페이지 작업단계를 매칭합니다."""
        try:
            # 간단한 매칭 로직 (GPT 없이)
            # 정확한 매칭 먼저 시도
            for task in available_tasks:
                if json_task_name in task or task in json_task_name:
                    print(f"✅ 정확한 매칭 발견: '{json_task_name}' → '{task}'")
                    return task
            
            # 부분 매칭 시도
            for task in available_tasks:
                # 키워드 기반 매칭
                keywords = {
                    "논갈이": ["논갈이", "쟁기"],
                    "비료": ["비료"],
                    "로터리": ["로터리"],
                    "볍씨소독": ["소독", "볍씨"],
                    "파종": ["파종", "씨뿌리기"],
                    "치상": ["치상"],
                    "이앙": ["이앙", "모내기"],
                    "방제": ["방제", "농약"],
                    "제초": ["제초", "잡초"],
                    "물떼기": ["물떼기"],
                    "수확": ["수확"],
                    "건조": ["건조"],
                    "출하": ["출하", "판매"]
                }
                
                for keyword, related_terms in keywords.items():
                    if keyword in json_task_name:
                        for term in related_terms:
                            if term in task:
                                print(f"✅ 키워드 매칭 발견: '{json_task_name}' → '{task}'")
                                return task
            
            print(f"⚠️ 매칭 실패: '{json_task_name}'에 해당하는 작업단계를 찾을 수 없습니다.")
            return None
            
        except Exception as e:
            print(f"❌ 작업 매칭 중 오류: {e}")
            return None
    
    def generate_weather_aware_content(self, task_name, selected_date, weather_data):
        """날씨 정보를 고려한 현실적인 작업 내용 생성"""
        try:
            if weather_data:
                prompt = f"""
                {selected_date} 날씨: {weather_data['weather']}, 
                기온: {weather_data['low_temp']}°C~{weather_data['high_temp']}°C, 
                강수량: {weather_data['rainfall']}mm, 
                습도: {weather_data['humidity']}%
                
                {task_name} 작업에 대한 영농일지를 작성해주세요. 
                날씨 상황을 고려해서 현실적인 내용으로 작성해주세요.
                """
            else:
                prompt = f"{task_name} 작업에 대한 영농일지를 작성해주세요."
            
            # GPT를 사용하여 내용 생성 (날짜 정보 포함)
            content = self.content_generator.generate_diary_content(task_name, "벼", use_gpt=True, current_date=selected_date)
            
            # 날씨 정보가 있으면 추가
            if weather_data and content:
                weather_context = f" 날씨는 {weather_data['weather']}이고 기온은 {weather_data['low_temp']}°C~{weather_data['high_temp']}°C입니다."
                content = content.replace(".", weather_context + ".", 1)
            
            return content
            
        except Exception as e:
            print(f"❌ 날씨 고려 내용 생성 실패: {e}")
            return self.content_generator.generate_diary_content(task_name, "벼", use_gpt=False)
    
    def parse_farming_schedule(self, schedule_text):
        """농작업 일정 텍스트를 파싱하여 작업 단계를 추출합니다."""
        try:
            print(f"농작업 일정 파싱: {schedule_text}")
            
            # 쉼표로 구분된 작업 단계들을 분리
            schedule_parts = [part.strip() for part in schedule_text.split(',')]
            print(f"분리된 일정 부분: {schedule_parts}")
            
            # 일반적인 농작업 키워드 (품종에 관계없이 사용되는 기본 키워드)
            general_keywords = {
                "씨뿌리기": ["씨뿌리기", "파종", "종자", "소독"],
                "모내기": ["모내기", "이앙", "모", "심기"],
                "비료주기": ["비료", "시비", "주기", "영양"],
                "농약살포": ["농약", "방제", "살포", "약제", "병해충"],
                "물관리": ["물", "관수", "물떼기", "배수", "관리"],
                "수확": ["수확", "수확기", "출하", "판매", "수집"],
                "건조": ["건조"],
                "제초": ["제초", "잡초"],
                "갈이": ["갈이", "쟁기", "로터리"],
                "기타": ["기타", "교육", "예찰"]
            }
            
            # 각 부분에서 키워드 찾기
            matched_tasks = []
            for part in schedule_parts:
                part_matched = False
                for task_name, keywords in general_keywords.items():
                    for keyword in keywords:
                        if keyword in part:
                            if task_name not in matched_tasks:  # 중복 제거
                                matched_tasks.append(task_name)
                            part_matched = True
                            break
                    if part_matched:
                        break
                
                # 키워드 매칭이 안된 경우, 입력된 텍스트 그대로 사용
                if not part_matched and part:
                    matched_tasks.append(part)
            
            print(f"파싱된 작업 단계: {matched_tasks}")
            return matched_tasks
            
        except Exception as e:
            print(f"농작업 일정 파싱 실패: {e}")
            return []
    
    def find_matching_task_step(self, schedule_task, available_tasks):
        """일정 텍스트와 사용 가능한 작업 단계를 매칭합니다."""
        try:
            print(f"작업 단계 매칭: '{schedule_task}' -> {available_tasks}")
            
            # 1. 정확한 매칭 시도
            for available_task in available_tasks:
                if schedule_task == available_task:
                    print(f"정확 매칭: {available_task}")
                    return available_task
            
            # 2. 부분 매칭 시도 (포함 관계)
            for available_task in available_tasks:
                if schedule_task in available_task or available_task in schedule_task:
                    print(f"부분 매칭: {available_task}")
                    return available_task
            
            # 3. 유사도 기반 매칭 (품종에 관계없는 일반적인 키워드)
            general_keywords = {
                "씨뿌리기": ["파종", "종자", "소독", "씨앗"],
                "모내기": ["이앙", "모", "심기", "정식"],
                "비료주기": ["비료", "시비", "영양", "주기"],
                "농약살포": ["방제", "약제", "병해충", "살포"],
                "물관리": ["물", "관수", "물떼기", "배수", "관리"],
                "수확": ["수확", "출하", "판매", "수집"],
                "건조": ["건조"],
                "제초": ["제초", "잡초"],
                "갈이": ["갈이", "쟁기", "로터리", "경운"],
                "기타": ["기타", "교육", "예찰", "활동"]
            }
            
            # 일반 키워드로 매칭 시도
            for schedule_key, keywords in general_keywords.items():
                if schedule_task == schedule_key:
                    for available_task in available_tasks:
                        for keyword in keywords:
                            if keyword in available_task:
                                print(f"일반 키워드 매칭: {schedule_task} -> {available_task}")
                                return available_task
            
            # 4. 유사도 점수 기반 매칭 (가장 유사한 옵션 선택)
            best_match = None
            best_score = 0
            
            for available_task in available_tasks:
                # 간단한 유사도 계산 (공통 문자 수)
                common_chars = sum(1 for c in schedule_task if c in available_task)
                score = common_chars / max(len(schedule_task), len(available_task))
                
                if score > best_score and score > 0.3:  # 30% 이상 유사도
                    best_score = score
                    best_match = available_task
            
            if best_match:
                print(f"유사도 매칭: {schedule_task} -> {best_match} (점수: {best_score:.2f})")
                return best_match
            
            # 5. 매칭 실패 시 첫 번째 유효한 옵션 반환
            if available_tasks:
                print(f"매칭 실패, 첫 번째 옵션 선택: {available_tasks[0]}")
                return available_tasks[0]
            
            return None
            
        except Exception as e:
            print(f"작업 단계 매칭 실패: {e}")
            return None
    
    def select_task_step(self, task_step):
        """작업 단계를 선택합니다."""
        try:
            print(f"작업 단계 선택: {task_step}")
            
            # 작업 단계 선택 드롭다운 클릭
            task_select = self.wait.until(
                EC.element_to_be_clickable((By.ID, "selectTask"))
            )
            task_select.click()
            time.sleep(0.3)  # 빠른 대기
            
            # 작업 단계 옵션들 찾기
            options = self.driver.find_elements(By.CSS_SELECTOR, "#selectTask option")
            print(f"발견된 작업 단계 옵션 수: {len(options)}")
            
            # 작업 단계 옵션 찾기 (빠른 매칭)
            found = False
            for i, option in enumerate(options):
                option_text = option.text.strip()
                option_value = option.get_attribute("value")
                
                # 정확한 매칭 시도
                if task_step == option_text:
                    option.click()
                    found = True
                    print(f"작업 단계 정확 매칭 선택됨: {option_text}")
                    break
                elif task_step in option_text or option_text in task_step:
                    option.click()
                    found = True
                    print(f"작업 단계 부분 매칭 선택됨: {option_text}")
                    break
                # value 속성으로도 매칭 시도
                elif option_value and task_step in option_value:
                    option.click()
                    found = True
                    print(f"작업 단계 value 매칭 선택됨: {option_text} (value: {option_value})")
                    break
            
            if not found:
                # 기본값 선택 (첫 번째 유효한 옵션)
                for option in options:
                    option_text = option.text.strip()
                    option_value = option.get_attribute("value")
                    if option_text and option_text != "작업단계 선택" and option_value:
                        option.click()
                        print(f"'{task_step}'을 찾을 수 없어 첫 번째 유효한 옵션을 선택했습니다: {option_text}")
                        break
                else:
                    print("선택 가능한 작업 단계가 없습니다.")
            
            # 서버 전송을 위한 대기 (단축)
            time.sleep(0.5)
            print("작업 단계 선택 완료!")
            
        except Exception as e:
            print(f"작업 단계 선택 중 오류 발생: {e}")
            # 오류 발생 시에도 계속 진행
            print("작업 단계 선택을 건너뛰고 계속 진행합니다.")
            
    def enter_memo(self, task_step):
        """작업 내용을 입력합니다."""
        try:
            print("작업 내용 입력 중...")
            
            # 메모 입력 필드
            memo_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "memo"))
            )
            
            # 현재 선택된 품목과 작업 단계 텍스트 가져오기
            selected_crop = self.get_selected_crop_text()
            selected_task = self.get_selected_task_text()
            
            # ChatGPT를 사용하여 내용 생성 (실제 선택된 텍스트 기반)
            # Config에서 GPT 사용 여부 설정 (결제 완료로 GPT 활성화)
            content = self.content_generator.generate_diary_content(selected_task, selected_crop, True, None)  # GPT 사용
            
            memo_input.clear()
            time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            # 자연스러운 타이핑 시뮬레이션 (속도 향상)
            for char in content:
                memo_input.send_keys(char)
                time.sleep(random.uniform(0.02, 0.08))  # 타이핑 속도 향상
            
            print(f"작업 내용 입력 완료: {content[:50]}...")
            
        except Exception as e:
            print(f"작업 내용 입력 중 오류 발생: {e}")
            raise
            
    def handle_additional_fields(self, task_step):
        """작업 단계별 추가 입력 필드를 처리합니다."""
        try:
            print(f"추가 입력 필드 처리 중: {task_step}")
            
            # 수확작업인 경우
            if "수확작업" in task_step:
                self.handle_harvest_fields()
            # 파종작업인 경우
            elif "파종작업" in task_step:
                self.handle_seeding_fields()
            # 이앙작업인 경우
            elif "이앙작업" in task_step:
                self.handle_transplanting_fields()
                
        except Exception as e:
            print(f"추가 입력 필드 처리 중 오류 발생: {e}")
            
    def handle_harvest_fields(self):
        """수확작업 관련 추가 필드를 처리합니다."""
        try:
            print("수확작업 추가 필드 처리 중...")
            
            # 수확량 입력 (amount3)
            try:
                amount3_input = self.driver.find_element(By.ID, "amount3")
                amount3_input.clear()
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                # 벼 수확량은 보통 1평당 0.5~0.8kg 정도, 300평 기준으로 계산
                harvest_amount = str(random.randint(150, 240))  # 150~240kg
                amount3_input.send_keys(harvest_amount)
                print(f"수확량 입력 완료: {harvest_amount}kg")
            except Exception as e:
                print(f"수확량 입력 실패: {e}")
            
            # 단위 선택 (unit)
            try:
                unit_select = self.driver.find_element(By.ID, "unit")
                from selenium.webdriver.support.ui import Select
                select = Select(unit_select)
                select.select_by_value("kg")
                print("단위 선택 완료: kg")
            except Exception as e:
                print(f"단위 선택 실패: {e}")
                
        except Exception as e:
            print(f"수확작업 필드 처리 중 오류: {e}")
            
    def handle_seeding_fields(self):
        """파종작업 관련 추가 필드를 처리합니다."""
        try:
            print("파종작업 추가 필드 처리 중...")
            
            # 파종량 입력 (amount2)
            try:
                amount2_input = self.driver.find_element(By.ID, "amount2")
                amount2_input.clear()
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                # 벼 파종량은 보통 1평당 0.2~0.3kg 정도, 300평 기준으로 계산
                seeding_amount = str(random.randint(60, 90))  # 60~90kg
                amount2_input.send_keys(seeding_amount)
                print(f"파종량 입력 완료: {seeding_amount}kg")
            except Exception as e:
                print(f"파종량 입력 실패: {e}")
            
            # 단위 선택 (unit)
            try:
                unit_select = self.driver.find_element(By.ID, "unit")
                from selenium.webdriver.support.ui import Select
                select = Select(unit_select)
                select.select_by_value("kg")
                print("단위 선택 완료: kg")
            except Exception as e:
                print(f"단위 선택 실패: {e}")
                
        except Exception as e:
            print(f"파종작업 필드 처리 중 오류: {e}")
            
    def handle_transplanting_fields(self):
        """이앙작업 관련 추가 필드를 처리합니다."""
        try:
            print("이앙작업 추가 필드 처리 중...")
            
            # 평당 주수 입력 (perPyeongAmount)
            try:
                per_pyeong_input = self.driver.find_element(By.ID, "perPyeongAmount")
                per_pyeong_input.clear()
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                # 벼 평당 주수는 보통 15~20주 정도
                per_pyeong_amount = str(random.randint(15, 20))
                per_pyeong_input.send_keys(per_pyeong_amount)
                print(f"평당 주수 입력 완료: {per_pyeong_amount}주")
            except Exception as e:
                print(f"평당 주수 입력 실패: {e}")
            
            # 모판 수량 입력 (seedbedAmount)
            try:
                seedbed_input = self.driver.find_element(By.ID, "seedbedAmount")
                seedbed_input.clear()
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                # 모판 수량은 보통 300평 기준으로 15~20개 정도
                seedbed_amount = str(random.randint(15, 20))
                seedbed_input.send_keys(seedbed_amount)
                print(f"모판 수량 입력 완료: {seedbed_amount}개")
            except Exception as e:
                print(f"모판 수량 입력 실패: {e}")
                
        except Exception as e:
            print(f"이앙작업 필드 처리 중 오류: {e}")
            
    def get_selected_crop_text(self):
        """현재 선택된 품목의 텍스트를 가져옵니다."""
        try:
            crop_select = self.driver.find_element(By.ID, "selectCrops")
            # Select 객체를 사용하여 선택된 값 가져오기
            from selenium.webdriver.support.ui import Select
            select = Select(crop_select)
            selected_option = select.first_selected_option
            crop_text = selected_option.text
            print(f"선택된 품목: {crop_text}")
            return crop_text
        except Exception as e:
            print(f"품목 텍스트 가져오기 실패: {e}")
            return Config.CROP_TYPE
            
    def get_selected_task_text(self):
        """현재 선택된 작업 단계의 텍스트를 가져옵니다."""
        try:
            task_select = self.driver.find_element(By.ID, "selectTask")
            # Select 객체를 사용하여 선택된 값 가져오기
            from selenium.webdriver.support.ui import Select
            select = Select(task_select)
            selected_option = select.first_selected_option
            task_text = selected_option.text
            print(f"선택된 작업 단계: {task_text}")
            return task_text
        except Exception as e:
            print(f"작업 단계 텍스트 가져오기 실패: {e}")
            return "작업단계 선택"
    
    def check_input_fields(self):
        """입력 항목들이 올바르게 설정되었는지 확인합니다."""
        try:
            print("입력 항목 체크 중...")
            missing_fields = []
            
            # 1. 날짜 체크
            try:
                start_date = self.driver.find_element(By.ID, "now_date_s").get_attribute("value")
                end_date = self.driver.find_element(By.ID, "now_date_e").get_attribute("value")
                if not start_date or not end_date:
                    missing_fields.append("날짜")
                    print("❌ 날짜가 설정되지 않았습니다.")
                else:
                    print(f"✅ 날짜 설정됨: {start_date} ~ {end_date}")
            except Exception as e:
                missing_fields.append("날짜")
                print(f"❌ 날짜 체크 실패: {e}")
            
            # 2. 품목 체크
            try:
                selected_crop = self.get_selected_crop_text()
                if not selected_crop or selected_crop == "품목선택":
                    missing_fields.append("품목")
                    print("❌ 품목이 선택되지 않았습니다.")
                else:
                    print(f"✅ 품목 선택됨: {selected_crop}")
            except Exception as e:
                missing_fields.append("품목")
                print(f"❌ 품목 체크 실패: {e}")
            
            # 3. 필지 체크
            try:
                land_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "#checkLand input[type='checkbox']:checked")
                if not land_checkboxes:
                    missing_fields.append("필지")
                    print("❌ 필지가 선택되지 않았습니다.")
                else:
                    print(f"✅ 필지 선택됨: {len(land_checkboxes)}개")
            except Exception as e:
                missing_fields.append("필지")
                print(f"❌ 필지 체크 실패: {e}")
            
            # 4. 품종 체크
            try:
                crop_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "#checkScrop input[type='checkbox']:checked")
                if not crop_checkboxes:
                    missing_fields.append("품종")
                    print("❌ 품종이 선택되지 않았습니다.")
                else:
                    print(f"✅ 품종 선택됨: {len(crop_checkboxes)}개")
            except Exception as e:
                missing_fields.append("품종")
                print(f"❌ 품종 체크 실패: {e}")
            
            # 5. 작업 단계 체크
            try:
                selected_task = self.get_selected_task_text()
                if not selected_task or selected_task == "작업단계 선택":
                    missing_fields.append("작업 단계")
                    print("❌ 작업 단계가 선택되지 않았습니다.")
                else:
                    print(f"✅ 작업 단계 선택됨: {selected_task}")
            except Exception as e:
                missing_fields.append("작업 단계")
                print(f"❌ 작업 단계 체크 실패: {e}")
            
            # 6. 작업 내용 체크
            try:
                memo_input = self.driver.find_element(By.ID, "memo")
                memo_content = memo_input.get_attribute("value")
                if not memo_content or len(memo_content.strip()) < 10:
                    missing_fields.append("작업 내용")
                    print("❌ 작업 내용이 입력되지 않았거나 너무 짧습니다.")
                else:
                    print(f"✅ 작업 내용 입력됨: {len(memo_content)}자")
            except Exception as e:
                missing_fields.append("작업 내용")
                print(f"❌ 작업 내용 체크 실패: {e}")
            
            if missing_fields:
                print(f"\n⚠️  누락된 항목: {', '.join(missing_fields)}")
                return False, missing_fields
            else:
                print("\n✅ 모든 입력 항목이 올바르게 설정되었습니다!")
                return True, []
                
        except Exception as e:
            print(f"입력 항목 체크 중 오류 발생: {e}")
            return False, []
    
    def get_missing_fields(self):
        """누락된 입력 항목들을 확인하고 목록을 반환합니다."""
        try:
            missing_fields = []
            
            # 1. 날짜 체크
            try:
                start_date = self.driver.find_element(By.ID, "now_date_s").get_attribute("value")
                end_date = self.driver.find_element(By.ID, "now_date_e").get_attribute("value")
                if not start_date or not end_date:
                    missing_fields.append("날짜")
            except:
                missing_fields.append("날짜")
            
            # 2. 품목 체크
            try:
                selected_crop = self.get_selected_crop_text()
                if not selected_crop or selected_crop == "품목선택":
                    missing_fields.append("품목")
            except:
                missing_fields.append("품목")
            
            # 3. 필지 체크
            try:
                land_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "#checkLand input[type='checkbox']:checked")
                if not land_checkboxes:
                    missing_fields.append("필지")
            except:
                missing_fields.append("필지")
            
            # 4. 품종 체크
            try:
                crop_checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "#checkScrop input[type='checkbox']:checked")
                if not crop_checkboxes:
                    missing_fields.append("품종")
            except:
                missing_fields.append("품종")
            
            # 5. 작업 단계 체크
            try:
                selected_task = self.get_selected_task_text()
                if not selected_task or selected_task == "작업단계 선택":
                    missing_fields.append("작업 단계")
            except:
                missing_fields.append("작업 단계")
            
            # 6. 작업 내용 체크
            try:
                memo_input = self.driver.find_element(By.ID, "memo")
                memo_content = memo_input.get_attribute("value")
                if not memo_content or len(memo_content.strip()) < 10:
                    missing_fields.append("작업 내용")
            except:
                missing_fields.append("작업 내용")
            
            return missing_fields
                
        except Exception as e:
            print(f"누락된 항목 확인 중 오류 발생: {e}")
            return []
    
    def retry_input_fields(self, missing_fields):
        """누락된 입력 항목들을 다시 설정합니다."""
        try:
            print(f"\n누락된 항목 재설정 시작: {', '.join(missing_fields)}")
            
            for field in missing_fields:
                print(f"\n--- {field} 재설정 ---")
                
                if field == "날짜":
                    # 날짜 재설정 (현재 설정된 날짜 사용)
                    start_date = self.driver.find_element(By.ID, "now_date_s").get_attribute("value")
                    end_date = self.driver.find_element(By.ID, "now_date_e").get_attribute("value")
                    if not start_date or not end_date:
                        # 기본 날짜 설정
                        from datetime import datetime
                        today = datetime.now().strftime('%Y-%m-%d')
                        self.set_date_range(today, today)
                
                elif field == "품목":
                    self.select_crop()
                
                elif field == "필지":
                    self.select_all_lands()
                
                elif field == "품종":
                    self.select_all_crops()
                
                elif field == "작업 단계":
                    # 현재 선택된 작업 단계 다시 선택
                    selected_task = self.get_selected_task_text()
                    if selected_task and selected_task != "작업단계 선택":
                        self.select_task_step(selected_task)
                
                elif field == "작업 내용":
                    # 작업 내용 재입력
                    selected_task = self.get_selected_task_text()
                    if selected_task and selected_task != "작업단계 선택":
                        self.enter_memo(selected_task)
                
                time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            print("누락된 항목 재설정 완료!")
            
        except Exception as e:
            print(f"누락된 항목 재설정 중 오류 발생: {e}")
            
    def save_diary(self):
        """영농일지를 저장합니다."""
        try:
            print("영농일지 저장 중...")
            
            # 저장 버튼 클릭
            save_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "upsert_diary"))
            )
            save_button.click()
            
            # 저장 후 대기 시간 단축
            time.sleep(random.uniform(2, 4))
            
            # 첫 번째 알럿 확인
            time.sleep(1)
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                print("첫 번째 알럿 확인 완료")
            except:
                print("첫 번째 알럿이 없습니다.")
                
            # 두 번째 알럿 확인
            time.sleep(random.uniform(1, 2))
            try:
                alert = self.driver.switch_to.alert
                alert.accept()
                print("두 번째 알럿 확인 완료")
            except:
                print("두 번째 알럿이 없습니다.")
                
            print("영농일지 저장 완료!")
            
        except Exception as e:
            print(f"영농일지 저장 중 오류 발생: {e}")
            raise
            
    def process_single_diary(self, date, task_step, is_first=False):
        """단일 영농일지를 처리합니다."""
        try:
            print(f"\n=== {date} {task_step} 영농일지 등록 시작 ===")
            
            # 첫 번째가 아닌 경우에만 페이지 이동
            if not is_first:
                # 영농일지 상세 페이지로 이동 (링크 클릭 방식)
                self.navigate_to_diary_detail_from_main()
            
            # 날짜 설정
            self.set_date_range(date, date)
            
            # 첫 번째가 아닌 경우에만 품목, 필지, 품종 선택 (이미 선택되어 있음)
            if not is_first:
                # 1. 품목 선택 (셀렉트 박스)
                self.select_crop()
                
                # 2. 필지 선택 (체크박스) - 품목 선택 후 로드됨
                self.select_all_lands()
                
                # 3. 품종 선택 (체크박스) - 필지 선택 후 로드됨
                self.select_all_crops()
            
            # 4. 작업 단계 선택 (셀렉트 박스) - 품종 선택 후 로드됨
            self.select_task_step(task_step)
            
            # 5. 작업 단계별 추가 필드 처리
            self.handle_additional_fields(task_step)
            
            # 6. 작업 내용 입력
            self.enter_memo(task_step)
            
            # 저장 전 대기 (자연스러운 타이핑 시뮬레이션)
            time.sleep(random.uniform(2, 5))
            
            # 저장 전 입력 항목 체크
            print("\n=== 저장 전 입력 항목 체크 ===")
            max_retry_count = 3
            retry_count = 0
            
            while retry_count < max_retry_count:
                is_valid, missing_fields = self.check_input_fields()
                if is_valid:
                    print("✅ 모든 항목이 올바르게 설정되었습니다. 저장을 진행합니다.")
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retry_count:
                        print(f"\n⚠️  누락된 항목이 있습니다. 재시도 {retry_count}/{max_retry_count}")
                        # 누락된 항목 재설정
                        if missing_fields:
                            self.retry_input_fields(missing_fields)
                        time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                    else:
                        print("❌ 최대 재시도 횟수를 초과했습니다. 저장을 진행합니다.")
            
            # 저장
            self.save_diary()
            
            print(f"=== {date} {task_step} 영농일지 등록 완료 ===\n")
            
            # 다음 작업을 위한 대기 (서버 감지 방지를 위해 적절한 시간)
            time.sleep(random.uniform(5, 10))
            
        except Exception as e:
            print(f"영농일지 등록 중 오류 발생: {e}")
            print("🔄 에러 복구 시도: 메인 페이지로 돌아가서 영농일지 등록 재시작...")
            return self.recover_from_error(date, task_step)
            
    def process_single_diary_with_schedule(self, start_date, end_date):
        """JSON 스케줄 데이터를 기반으로 주간 영농일지를 처리합니다."""
        try:
            print(f"\n=== {start_date} ~ {end_date} 영농일지 등록 시작 (스케줄 기반) ===")
            
            # 1. JSON에서 해당 주의 작업들 찾기 (시작일 기준)
            matching_tasks = self.find_matching_tasks_by_date(start_date)
            
            if not matching_tasks:
                print(f"⚠️ {start_date} ~ {end_date}에 해당하는 작업이 없습니다. 기본 관리 작업으로 등록합니다.")
                # 기본 관리 작업으로 등록
                return self.process_basic_diary(start_date, end_date)
            
            # 2. 현재 페이지가 영농일지 작성 페이지인지 확인
            current_url = self.driver.current_url
            if not current_url.endswith('diaryDetail.do'):
                print("현재 페이지가 영농일지 작성 페이지가 아닙니다. 페이지 이동 중...")
                self.navigate_to_diary_detail_from_main()
            else:
                print("이미 영농일지 작성 페이지에 있습니다.")
            
            # 3. 날짜 범위 설정
            self.set_date_range(start_date, end_date)
            
            # 4. 품목, 필지, 품종 선택 (항상 처음부터 시작)
            try:
                self.select_crop()
                self.select_all_lands()
                self.select_all_crops()
            except Exception as e:
                print(f"❌ 품목/필지/품종 선택 실패: {e}")
                return False
            
            # 5. 사용 가능한 작업단계 목록 가져오기 (빠른 방식)
            try:
                # 페이지 안정화를 위한 대기 (단축)
                time.sleep(1)
                
                # 작업단계 드롭다운이 로드될 때까지 대기
                self.wait.until(
                    EC.presence_of_element_located((By.ID, "selectTask"))
                )
                
                available_tasks = self.get_available_task_steps()
                
                if not available_tasks:
                    print("❌ 사용 가능한 작업단계를 가져올 수 없습니다.")
                    return False
            except Exception as e:
                print(f"❌ 작업단계 목록 가져오기 실패: {e}")
                return False
            
            # 6. 랜덤으로 작업 선택하여 매칭 시도
            import random
            selected_task = random.choice(matching_tasks)
            print(f"🎲 랜덤 선택된 작업: {selected_task['작업명']} ({selected_task['기간']})")
            matched_task = self.match_task_with_gpt(selected_task["작업명"], available_tasks)
            
            if not matched_task:
                print(f"❌ '{selected_task['작업명']}'에 해당하는 작업단계를 찾을 수 없습니다.")
                return False
            
            # 7. 작업단계 선택
            self.select_task_step(matched_task)
            
            # 8. 작업 단계별 추가 필드 처리
            self.handle_additional_fields(matched_task)
            
            # 9. 날씨 정보 수집
            weather_data = self.get_weather_data()
            
            # 10. 날씨를 고려한 작업 내용 생성
            content = self.generate_weather_aware_content(
                selected_task["작업명"], 
                start_date, 
                weather_data
            )
            
            # 날짜 정보를 포함한 내용 생성
            if not content:
                content = self.content_generator.generate_diary_content(
                    selected_task["작업명"], 
                    "벼", 
                    True, 
                    start_date
                )
            
            # 11. 작업 내용 입력
            self.enter_memo_with_content(content)
            
            # 11. 저장 전 입력 항목 체크
            print("\n=== 저장 전 입력 항목 체크 ===")
            max_retry_count = 3
            retry_count = 0
            
            while retry_count < max_retry_count:
                is_valid, missing_fields = self.check_input_fields()
                if is_valid:
                    print("✅ 모든 항목이 올바르게 설정되었습니다. 저장을 진행합니다.")
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retry_count:
                        print(f"\n⚠️  누락된 항목이 있습니다. 재시도 {retry_count}/{max_retry_count}")
                        if missing_fields:
                            self.retry_input_fields(missing_fields)
                        time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                    else:
                        print("❌ 최대 재시도 횟수를 초과했습니다. 저장을 진행합니다.")
            
            # 12. 영농일지 저장
            self.save_diary()
            
            self.log_message(f"✅ {start_date} {selected_task['작업명']} 영농일지 등록 완료!")
            return True
            
        except Exception as e:
            self.log_message(f"❌ {start_date} 영농일지 등록 중 오류 발생: {e}")
            self.log_message("🔄 에러 복구 시도: 메인 페이지로 돌아가서 영농일지 등록 재시작...")
            return self.recover_from_error_with_schedule(start_date, end_date)
            
    def process_basic_diary(self, start_date, end_date):
        """작업이 없는 주의 기본 관리 영농일지를 등록합니다."""
        try:
            print(f"\n=== {start_date} ~ {end_date} 기본 관리 영농일지 등록 시작 ===")
            
            # 1. 현재 페이지가 영농일지 작성 페이지인지 확인
            current_url = self.driver.current_url
            if not current_url.endswith('diaryDetail.do'):
                print("현재 페이지가 영농일지 작성 페이지가 아닙니다. 페이지 이동 중...")
                self.navigate_to_diary_detail_from_main()
            else:
                print("이미 영농일지 작성 페이지에 있습니다.")
            
            # 2. 날짜 범위 설정
            self.set_date_range(start_date, end_date)
            
            # 3. 품목, 필지, 품종 선택 (항상 처음부터 시작)
            try:
                self.select_crop()
                self.select_all_lands()
                self.select_all_crops()
            except Exception as e:
                print(f"❌ 품목/필지/품종 선택 실패: {e}")
                return False
            
            # 4. 사용 가능한 작업단계 목록 가져오기 (빠른 방식)
            try:
                # 페이지 안정화를 위한 대기 (단축)
                time.sleep(1)
                
                # 작업단계 드롭다운이 로드될 때까지 대기
                self.wait.until(
                    EC.presence_of_element_located((By.ID, "selectTask"))
                )
                
                available_tasks = self.get_available_task_steps()
                
                if not available_tasks:
                    print("❌ 사용 가능한 작업단계를 가져올 수 없습니다.")
                    return False
            except Exception as e:
                print(f"❌ 작업단계 목록 가져오기 실패: {e}")
                return False
            
            # 5. 기본 관리 작업 선택 (기타작업 또는 비료작업)
            basic_task = None
            for task in available_tasks:
                if "기타작업" in task or "비료작업" in task or "관찰" in task:
                    basic_task = task
                    break
            
            if not basic_task:
                # 첫 번째 사용 가능한 작업 사용
                basic_task = available_tasks[0]
            
            print(f"선택된 기본 작업: {basic_task}")
            
            # 6. 작업단계 선택
            self.select_task_step(basic_task)
            
            # 7. 작업 단계별 추가 필드 처리
            self.handle_additional_fields(basic_task)
            
            # 8. 날씨 정보 수집
            weather_data = self.get_weather_data()
            
            # 9. 기본 관리 내용 생성
            content = self.generate_basic_diary_content(start_date, weather_data)
            
            # 10. 작업 내용 입력
            self.enter_memo_with_content(content)
            
            # 11. 저장 전 입력 항목 체크
            print("\n=== 저장 전 입력 항목 체크 ===")
            max_retry_count = 3
            retry_count = 0
            
            while retry_count < max_retry_count:
                is_valid, missing_fields = self.check_input_fields()
                if is_valid:
                    print("✅ 모든 항목이 올바르게 설정되었습니다. 저장을 진행합니다.")
                    break
                else:
                    retry_count += 1
                    if retry_count < max_retry_count:
                        print(f"\n⚠️  누락된 항목이 있습니다. 재시도 {retry_count}/{max_retry_count}")
                        if missing_fields:
                            self.retry_input_fields(missing_fields)
                        time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
                    else:
                        print("❌ 최대 재시도 횟수를 초과했습니다. 저장을 진행합니다.")
            
            # 12. 영농일지 저장
            self.save_diary()
            
            print(f"✅ {start_date} 기본 관리 영농일지 등록 완료!")
            return True
            
        except Exception as e:
            print(f"❌ {start_date} 기본 관리 영농일지 등록 중 오류 발생: {e}")
            return False
            
    def generate_basic_diary_content(self, date, weather_data):
        """기본 관리 영농일지 내용을 생성합니다. (GPT 활용)"""
        try:
            # 날씨 정보가 있으면 포함
            if weather_data:
                weather_info = f" 날씨는 {weather_data['weather']}이고 기온은 {weather_data['low_temp']}°C~{weather_data['high_temp']}°C입니다."
            else:
                weather_info = ""
            
            # 계절에 따른 기본 관리 내용 (GPT 활용)
            month = int(date.split('-')[1])
            
            # GPT를 사용하여 다양한 내용 생성
            if Config.OPENAI_API_KEY:
                try:
                    season_prompts = {
                        "winter": f"{date} 겨울철 논 관리. 토양 상태 점검 및 겨울철 준비 작업.{weather_info} 다양한 겨울철 논 관리 활동을 100자 이내로 작성해주세요.",
                        "spring": f"{date} 봄철 논 관리. 파종 준비 및 토양 상태 점검.{weather_info} 다양한 봄철 논 관리 활동을 100자 이내로 작성해주세요.",
                        "early_summer": f"{date} 초여름 논 관리. 모내기 후 생육 상태 점검.{weather_info} 다양한 초여름 논 관리 활동을 100자 이내로 작성해주세요.",
                        "summer": f"{date} 여름철 논 관리. 생육 관리 및 병해충 점검.{weather_info} 다양한 여름철 논 관리 활동을 100자 이내로 작성해주세요.",
                        "autumn": f"{date} 가을철 논 관리. 수확 준비 및 완숙도 점검.{weather_info} 다양한 가을철 논 관리 활동을 100자 이내로 작성해주세요.",
                        "late_autumn": f"{date} 늦가을 논 관리. 수확 후 정리 작업.{weather_info} 다양한 늦가을 논 관리 활동을 100자 이내로 작성해주세요."
                    }
                    
                    if month in [12, 1, 2]:
                        prompt = season_prompts["winter"]
                    elif month in [3, 4]:
                        prompt = season_prompts["spring"]
                    elif month in [5, 6]:
                        prompt = season_prompts["early_summer"]
                    elif month in [7, 8]:
                        prompt = season_prompts["summer"]
                    elif month in [9, 10]:
                        prompt = season_prompts["autumn"]
                    else:  # 11월
                        prompt = season_prompts["late_autumn"]
                    
                    # GPT 호출
                    content = self.content_generator.generate_diary_content(
                        "기본관리", "벼", True, date
                    )
                    
                    if content and len(content) > 20:  # 의미있는 내용이 생성된 경우
                        return content
                        
                except Exception as e:
                    print(f"GPT 기본 관리 내용 생성 실패: {e}")
            
            # GPT 실패 시 기본 템플릿 사용
            if month in [12, 1, 2]:  # 겨울
                templates = [
                    f"{date} 겨울철 논 관리. 토양 상태 점검 및 겨울철 준비 작업.{weather_info} 논갈이 준비 중이며 내년 작기 준비를 위해 정리 작업을 진행했습니다.",
                    f"{date} 겨울철 논 관리. 토양 동결 상태 확인 및 겨울철 보호 작업.{weather_info} 논의 동결 상태를 점검하고 겨울철 보호 작업을 진행했습니다.",
                    f"{date} 겨울철 논 관리. 농기구 정비 및 내년 계획 수립.{weather_info} 농기구 정비를 완료하고 내년 작기 계획을 수립했습니다."
                ]
            elif month in [3, 4]:  # 봄
                templates = [
                    f"{date} 봄철 논 관리. 파종 준비 및 토양 상태 점검.{weather_info} 논갈이 작업 완료 후 파종 준비를 위해 토양 상태를 확인했습니다.",
                    f"{date} 봄철 논 관리. 논갈이 작업 및 비료 준비.{weather_info} 봄철 논갈이 작업을 진행하고 파종을 위한 비료를 준비했습니다.",
                    f"{date} 봄철 논 관리. 논 정리 및 파종 준비.{weather_info} 논을 정리하고 파종을 위한 최종 준비를 완료했습니다."
                ]
            elif month in [5, 6]:  # 초여름
                templates = [
                    f"{date} 초여름 논 관리. 모내기 후 생육 상태 점검.{weather_info} 이앙 작업 완료 후 모의 생육 상태를 확인하고 물관리를 진행했습니다.",
                    f"{date} 초여름 논 관리. 모 생육 관리 및 물관리.{weather_info} 모의 생육 상태가 양호하며 적절한 물관리를 진행했습니다.",
                    f"{date} 초여름 논 관리. 모 적응 상태 점검 및 관리.{weather_info} 모의 적응 상태를 점검하고 생육에 필요한 관리 작업을 진행했습니다."
                ]
            elif month in [7, 8]:  # 여름
                templates = [
                    f"{date} 여름철 논 관리. 생육 관리 및 병해충 점검.{weather_info} 벼 생육이 양호하며 병해충 발생 여부를 정기적으로 점검하고 있습니다.",
                    f"{date} 여름철 논 관리. 생육 촉진 및 병해충 방제.{weather_info} 벼 생육을 촉진하고 병해충 방제 작업을 진행했습니다.",
                    f"{date} 여름철 논 관리. 생육 상태 점검 및 물관리.{weather_info} 벼 생육 상태를 점검하고 적절한 물관리를 진행했습니다."
                ]
            elif month in [9, 10]:  # 가을
                templates = [
                    f"{date} 가을철 논 관리. 수확 준비 및 완숙도 점검.{weather_info} 벼가 완숙기에 접어들어 수확 준비를 위해 상태를 점검했습니다.",
                    f"{date} 가을철 논 관리. 완숙도 확인 및 수확 준비.{weather_info} 벼의 완숙도를 확인하고 수확 준비 작업을 진행했습니다.",
                    f"{date} 가을철 논 관리. 수확 시기 결정 및 준비.{weather_info} 최적의 수확 시기를 결정하고 수확 준비를 완료했습니다."
                ]
            else:  # 11월
                templates = [
                    f"{date} 늦가을 논 관리. 수확 후 정리 작업.{weather_info} 수확 작업 완료 후 논 정리 및 내년 준비를 위한 작업을 진행했습니다.",
                    f"{date} 늦가을 논 관리. 논 정리 및 내년 준비.{weather_info} 수확 후 논을 정리하고 내년 작기를 위한 준비 작업을 진행했습니다.",
                    f"{date} 늦가을 논 관리. 농기구 정리 및 보관.{weather_info} 사용한 농기구를 정리하고 보관 작업을 완료했습니다."
                ]
            
            # 랜덤하게 템플릿 선택
            content = random.choice(templates)
            
            # 100자로 제한
            if len(content) > 100:
                content = content[:97] + "..."
            
            return content
            
        except Exception as e:
            print(f"기본 관리 내용 생성 중 오류: {e}")
            return f"{date} 논 관리 작업을 진행했습니다."
            


            
    def recover_from_error(self, date, task_step):
        """에러 발생 시 메인 페이지로 돌아가서 영농일지 등록을 재시작합니다."""
        try:
            print("🔄 에러 복구 프로세스 시작...")
            
            # 1. 메인 페이지로 이동
            print("📄 메인 페이지로 이동 중...")
            self.navigate_to_diary_main()
            time.sleep(Config.FAST_WAIT_TIME)
            
            # 2. 영농일지 등록 링크 찾기 및 클릭
            print("🔗 영농일지 등록 링크 찾는 중...")
            try:
                # 여러 방법으로 링크 찾기 시도
                diary_link = None
                
                # 방법 1: 정확한 JavaScript 링크 찾기
                try:
                    diary_link = self.driver.find_element(By.XPATH, "//a[@href=\"javascript:goView('I', 'diaryMain')\"]")
                    print("✅ 방법 1로 영농일지 등록 링크 발견")
                except:
                    pass
                
                # 방법 2: 텍스트로 찾기
                if not diary_link:
                    try:
                        diary_link = self.driver.find_element(By.XPATH, "//a[contains(text(), '영농일지 등록')]")
                        print("✅ 방법 2로 영농일지 등록 링크 발견")
                    except:
                        pass
                
                # 방법 3: 부분 href로 찾기
                if not diary_link:
                    try:
                        diary_link = self.driver.find_element(By.XPATH, "//a[contains(@href, 'goView') and contains(@href, 'diaryMain')]")
                        print("✅ 방법 3으로 영농일지 등록 링크 발견")
                    except:
                        pass
                
                if diary_link:
                    diary_link.click()
                    print("✅ 영농일지 등록 링크 클릭 성공")
                else:
                    raise Exception("영농일지 등록 링크를 찾을 수 없습니다")
                    
            except Exception as e:
                print(f"❌ 영농일지 등록 링크 클릭 실패: {e}")
                # 직접 URL 이동으로 대체
                print("🔄 직접 URL 이동으로 대체...")
                self.navigate_to_diary_detail()
            
            time.sleep(Config.FAST_WAIT_TIME)
            
            # 3. 영농일지 등록 재시작
            print(f"🔄 {date} {task_step} 영농일지 등록 재시작...")
            return self.process_single_diary(date, task_step, is_first=True)
            
        except Exception as e:
            print(f"❌ 에러 복구 실패: {e}")
            return False
            
    def recover_from_error_with_schedule(self, start_date, end_date=None):
        """스케줄 기반 에러 발생 시 메인 페이지로 돌아가서 영농일지 등록을 재시작합니다."""
        try:
            print("🔄 스케줄 기반 에러 복구 프로세스 시작...")
            
            # 1. 메인 페이지로 이동 (강제로 URL 이동)
            print("📄 메인 페이지로 이동 중...")
            self.driver.get(Config.DIARY_MAIN_URL)
            time.sleep(Config.FAST_WAIT_TIME)
            print("✅ 메인 페이지 이동 완료")
            
            # 2. 영농일지 등록 링크 찾기 및 클릭
            print("🔗 영농일지 등록 링크 찾는 중...")
            try:
                # 여러 방법으로 링크 찾기 시도
                diary_link = None
                
                # 방법 1: 정확한 JavaScript 링크 찾기
                try:
                    diary_link = self.driver.find_element(By.XPATH, "//a[@href=\"javascript:goView('I', 'diaryMain')\"]")
                    print("✅ 방법 1로 영농일지 등록 링크 발견")
                except:
                    pass
                
                # 방법 2: 텍스트로 찾기
                if not diary_link:
                    try:
                        diary_link = self.driver.find_element(By.XPATH, "//a[contains(text(), '영농일지 등록')]")
                        print("✅ 방법 2로 영농일지 등록 링크 발견")
                    except:
                        pass
                
                # 방법 3: 부분 href로 찾기
                if not diary_link:
                    try:
                        diary_link = self.driver.find_element(By.XPATH, "//a[contains(@href, 'goView') and contains(@href, 'diaryMain')]")
                        print("✅ 방법 3으로 영농일지 등록 링크 발견")
                    except:
                        pass
                
                if diary_link:
                    diary_link.click()
                    print("✅ 영농일지 등록 링크 클릭 성공")
                else:
                    raise Exception("영농일지 등록 링크를 찾을 수 없습니다")
                    
            except Exception as e:
                print(f"❌ 영농일지 등록 링크 클릭 실패: {e}")
                # 직접 URL 이동으로 대체
                print("🔄 직접 URL 이동으로 대체...")
                self.driver.get(Config.DIARY_DETAIL_URL)
            
            time.sleep(Config.FAST_WAIT_TIME)
            
            # 3. 영농일지 등록 재시작
            if end_date:
                print(f"🔄 {start_date} ~ {end_date} 영농일지 등록 재시작 (스케줄 기반)...")
                return self.process_single_diary_with_schedule(start_date, end_date)
            else:
                print(f"🔄 {start_date} 영농일지 등록 재시작 (스케줄 기반)...")
                return self.process_single_diary_with_schedule(start_date, start_date)
            
        except Exception as e:
            print(f"❌ 스케줄 기반 에러 복구 실패: {e}")
            return False
    
    def enter_memo_with_content(self, content):
        """생성된 내용으로 메모를 입력합니다."""
        try:
            print(f"📝 작업 내용 입력: {content}")
            
            # 메모 입력 필드 찾기
            memo_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "memo"))
            )
            
            # 기존 내용 삭제
            memo_input.clear()
            time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            # 새로운 내용 입력
            memo_input.send_keys(content)
            time.sleep(random.uniform(Config.INPUT_DELAY_MIN, Config.INPUT_DELAY_MAX))
            
            print("✅ 작업 내용 입력 완료")
            
        except Exception as e:
            print(f"❌ 작업 내용 입력 중 오류 발생: {e}")
            raise
    
    def run_macro(self):
        """메인 매크로를 실행합니다."""
        try:
            # 로그 파일 생성 (log 폴더에 저장)
            self.log_filename = f"log/diary_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # log 폴더가 없으면 생성
            os.makedirs('log', exist_ok=True)
            
            self.log_file = open(self.log_filename, 'w', encoding='utf-8')
            self.log_message("농업ON 영농일지 자동 등록 매크로 시작!")
            self.log_message(f"📝 로그 파일: {self.log_filename}")
            
            # 시작일 자동 업데이트 시도
            updated_start_date = self.auto_update_start_date()
            
            # 설정된 날짜부터 시작
            start_date = datetime.strptime(updated_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(Config.END_DATE, '%Y-%m-%d')
            current_week_start = start_date
            self.log_message(f"🚀 시작 날짜: {current_week_start.strftime('%Y-%m-%d')}")
            
            # 로그인
            self.login()
            
            # 영농일지 메인 페이지로 이동
            self.navigate_to_diary_main()
            
            # 메인 페이지에서 영농일지 작성 페이지로 이동
            self.navigate_to_diary_detail_from_main()
            
            # 전체 주차 계산
            total_weeks = ((end_date - start_date).days + Config.DIARY_INTERVAL_DAYS - 1) // Config.DIARY_INTERVAL_DAYS
            current_week = 0
            
            while current_week_start <= end_date:
                current_week += 1
                
                # 현재 주의 시작일과 종료일 계산
                week_end = min(current_week_start + timedelta(days=Config.DIARY_INTERVAL_DAYS - 1), end_date)
                week_start_str = current_week_start.strftime('%Y-%m-%d')
                week_end_str = week_end.strftime('%Y-%m-%d')
                
                self.log_message(f"\n📅 진행률: {current_week}/{total_weeks} ({week_start_str} ~ {week_end_str})")
                
                try:
                    success = self.process_single_diary_with_schedule(week_start_str, week_end_str)
                    if success:
                        self.log_message(f"✅ {week_start_str} ~ {week_end_str} 영농일지 등록 완료")
                    else:
                        self.log_message(f"⚠️ {week_start_str} ~ {week_end_str} 해당 작업 없음 (건너뜀)")
                except Exception as e:
                    self.log_message(f"⚠️ {week_start_str} ~ {week_end_str} 등록 중 오류 발생: {e}")
                    self.log_message("🔄 에러 복구 시도 중...")
                    
                    # 에러 복구 시도
                    recovery_success = self.recover_from_error_with_schedule(week_start_str, week_end_str)
                    if not recovery_success:
                        self.log_message(f"❌ {week_start_str} ~ {week_end_str} 복구 실패, 다음 주로 진행...")
                
                # 다음 주로 이동
                current_week_start += timedelta(days=Config.DIARY_INTERVAL_DAYS)
                
                # 진행률 표시 (4주마다)
                if current_week % 4 == 0:
                    progress_percent = (current_week / total_weeks) * 100
                    self.log_message(f"📊 진행률: {progress_percent:.1f}% ({current_week}/{total_weeks})")
                
                # 서버 부하 방지를 위한 대기
                time.sleep(random.uniform(3, 8))
                
            self.log_message("모든 영농일지 등록 완료!")
            
        except Exception as e:
            self.log_message(f"매크로 실행 중 오류 발생: {e}")
        finally:
            # 로그 파일 닫기
            if self.log_file:
                self.log_message("📝 로그 파일 저장 완료")
                self.log_file.flush()
                self.log_file.close()
                self.log_file = None
                print(f"✅ 로그 파일이 안전하게 저장되었습니다: {self.log_filename}")
            
            if self.driver:
                self.driver.quit()
                print("✅ 브라우저가 안전하게 종료되었습니다.")
    
    def get_farming_schedule(self):
        """사용자로부터 농작업 일정을 입력받습니다."""
        try:
            print("\n=== 농작업 일정 입력 ===")
            print("농작업 일정을 입력해주세요.")
            print("예시:")
            print("- 일반적인 표현: 씨뿌리기, 모내기, 비료주기, 농약살포, 수확")
            print("- 또는 실제 작업명: 파종작업, 이앙작업, 비료작업, 방제작업, 수확작업")
            print("- 또는 원하는 작업을 자유롭게 입력")
            print("여러 작업을 쉼표로 구분하여 입력할 수 있습니다.")
            print("입력하지 않으면 웹페이지의 기본 작업 단계를 사용합니다.")
            
            # 사용자 입력 받기
            schedule_input = input("농작업 일정: ").strip()
            
            if not schedule_input:
                print("일정을 입력하지 않아 웹페이지의 기본 작업 단계를 사용합니다.")
                return ""  # 빈 문자열로 반환하여 웹페이지 옵션 사용
            
            return schedule_input
            
        except Exception as e:
            print(f"일정 입력 중 오류 발생: {e}")
            return ""  # 오류 시에도 웹페이지 옵션 사용
                
    def run_test_mode(self):
        """테스트 모드 - 스케줄 기반 영농일지 1개 등록"""
        try:
            # 로그 파일 생성 (테스트 모드용)
            self.log_filename = f"log/test_diary_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            # log 폴더가 없으면 생성
            os.makedirs('log', exist_ok=True)
            
            self.log_file = open(self.log_filename, 'w', encoding='utf-8')
            self.log_message("🌾 농업ON 영농일지 테스트 등록 시작 (스케줄 기반)!")
            
            # 로그인
            self.login()
            
            # 영농일지 메인 페이지로 이동
            self.navigate_to_diary_main()
            
            # 메인 페이지에서 영농일지 작성 페이지로 이동
            self.navigate_to_diary_detail_from_main()
            
            # 테스트용 날짜 (3월 15일 - 로터리작업 기간)
            test_date = "2025-03-15"
            print(f"📅 테스트 날짜: {test_date}")
            
            # 1. 품목 선택 (셀렉트 박스)
            self.select_crop()
            
            # 2. 필지 선택 (체크박스) - 품목 선택 후 로드됨
            self.select_all_lands()
            
            # 3. 품종 선택 (체크박스) - 필지 선택 후 로드됨
            self.select_all_crops()
            
            # 스케줄 기반 영농일지 등록 (에러 발생 시 메인 페이지로 재진입)
            try:
                success = self.process_single_diary_with_schedule(test_date, is_first=True)
                
                if success:
                    print("✅ 테스트 영농일지 등록 완료!")
                else:
                    print("❌ 테스트 영농일지 등록 실패!")
                    
            except Exception as e:
                print(f"⚠️ 테스트 영농일지 등록 중 오류 발생: {e}")
                print("🔄 에러 복구 시도 중...")
                
                # 에러 복구 시도
                recovery_success = self.recover_from_error_with_schedule(test_date)
                if recovery_success:
                    print("✅ 테스트 영농일지 복구 성공!")
                else:
                    print("❌ 테스트 영농일지 복구 실패!")
            
        except Exception as e:
            print(f"❌ 테스트 모드 실행 중 오류 발생: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                print("✅ 브라우저가 안전하게 종료되었습니다.")
                
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
    
    def auto_update_start_date(self):
        """로그를 분석해서 시작일을 자동으로 업데이트합니다."""
        try:
            print("🔄 시작일 자동 업데이트 중...")
            
            # 로그에서 마지막 처리된 날짜 찾기
            last_date = self.find_last_processed_date_from_logs()
            
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
    
if __name__ == "__main__":
    macro = AgrionMacro()
    macro.run_macro()
