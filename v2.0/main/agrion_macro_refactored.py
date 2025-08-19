import time
import random
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.browser_manager import BrowserManager
from core.logger_manager import LoggerManager
from core.schedule_processor import ScheduleProcessor
from core.config_manager import ConfigManager
from config.ai_GPT_diary_content_generator import ContentGenerator
from config.settings import Config
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


class AgrionMacroRefactored:
    """리팩토링된 농업ON 영농일지 자동 등록 매크로"""
    
    def __init__(self, test_mode=False):
        # 의존성 주입 패턴 적용
        self.logger_manager = LoggerManager()
        self.browser_manager = BrowserManager(self.logger_manager)
        self.schedule_processor = ScheduleProcessor()
        self.config_manager = ConfigManager(self.logger_manager)
        self.content_generator = ContentGenerator()
        
        # 테스트 모드 설정
        self.test_mode = test_mode
        
        # 로그 시작
        if test_mode:
            self.logger_manager.log_message("🌾 농업ON 영농일지 테스트 등록 시작 (리팩토링 버전)!")
        else:
            self.logger_manager.log_message("농업ON 영농일지 자동 등록 매크로 시작 (리팩토링 버전)!")
    
    def run_macro(self):
        """메인 매크로를 실행합니다."""
        try:
            # 시작일 자동 업데이트 시도
            updated_start_date = self.config_manager.auto_update_start_date()
            
            # 설정된 날짜부터 시작
            start_date = datetime.strptime(updated_start_date, '%Y-%m-%d')
            end_date = datetime.strptime(Config.END_DATE, '%Y-%m-%d')
            current_week_start = start_date
            self.logger_manager.log_message(f"🚀 시작 날짜: {current_week_start.strftime('%Y-%m-%d')}")
            
            # 로그인
            self.browser_manager.login()
            
            # 영농일지 메인 페이지로 이동
            self.browser_manager.navigate_to_diary_main()
            
            # 메인 페이지에서 영농일지 작성 페이지로 이동
            self.browser_manager.navigate_to_diary_detail_from_main()
            
            # 전체 주차 계산
            total_weeks = ((end_date - start_date).days + Config.DIARY_INTERVAL_DAYS - 1) // Config.DIARY_INTERVAL_DAYS
            current_week = 0
            
            while current_week_start <= end_date:
                current_week += 1
                
                # 현재 주의 시작일과 종료일 계산
                week_end = min(current_week_start + timedelta(days=Config.DIARY_INTERVAL_DAYS - 1), end_date)
                week_start_str = current_week_start.strftime('%Y-%m-%d')
                week_end_str = week_end.strftime('%Y-%m-%d')
                
                self.logger_manager.log_message(f"\n📅 진행률: {current_week}/{total_weeks} ({week_start_str} ~ {week_end_str})")
                
                try:
                    success = self.process_single_diary_with_schedule(week_start_str, week_end_str)
                    if success:
                        self.logger_manager.log_message(f"✅ {week_start_str} ~ {week_end_str} 영농일지 등록 완료")
                    else:
                        self.logger_manager.log_message(f"⚠️ {week_start_str} ~ {week_end_str} 해당 작업 없음 (건너뜀)")
                except Exception as e:
                    self.logger_manager.log_message(f"⚠️ {week_start_str} ~ {week_end_str} 등록 중 오류 발생: {e}")
                    self.logger_manager.log_message("🔄 에러 복구 시도 중...")
                    
                    # 에러 복구 시도
                    recovery_success = self.recover_from_error_with_schedule(week_start_str, week_end_str)
                    if not recovery_success:
                        self.logger_manager.log_message(f"❌ {week_start_str} ~ {week_end_str} 복구 실패, 다음 주로 진행...")
                
                # 다음 주로 이동
                current_week_start += timedelta(days=Config.DIARY_INTERVAL_DAYS)
                
                # 진행률 표시 (4주마다)
                if current_week % 4 == 0:
                    progress_percent = (current_week / total_weeks) * 100
                    self.logger_manager.log_message(f"📊 진행률: {progress_percent:.1f}% ({current_week}/{total_weeks})")
                
                # 서버 부하 방지를 위한 대기
                time.sleep(random.uniform(3, 8))
                
            self.logger_manager.log_message("모든 영농일지 등록 완료!")
            
        except Exception as e:
            self.logger_manager.log_message(f"매크로 실행 중 오류 발생: {e}")
        finally:
            # cleanup_and_exit에서 통합 처리
            self.browser_manager.cleanup_and_exit()
    
    def run_test_mode(self):
        """테스트 모드 - 스케줄 기반 영농일지 1개 등록"""
        try:
            # 로그인
            self.browser_manager.login()
            
            # 영농일지 메인 페이지로 이동
            self.browser_manager.navigate_to_diary_main()
            
            # 메인 페이지에서 영농일지 작성 페이지로 이동
            self.browser_manager.navigate_to_diary_detail_from_main()
            
            # 테스트용 날짜 (3월 15일 - 로터리작업 기간)
            test_date = "2025-03-15"
            print(f"📅 테스트 날짜: {test_date}")
            
            # 스케줄 기반 영농일지 등록 (에러 발생 시 메인 페이지로 재진입)
            try:
                success = self.process_single_diary_with_schedule(test_date, test_date)
                
                if success:
                    print("✅ 테스트 영농일지 등록 완료!")
                else:
                    print("❌ 테스트 영농일지 등록 실패!")
                    
            except Exception as e:
                print(f"⚠️ 테스트 영농일지 등록 중 오류 발생: {e}")
                print("🔄 에러 복구 시도 중...")
                
                # 에러 복구 시도
                recovery_success = self.recover_from_error_with_schedule(test_date, test_date)
                if recovery_success:
                    print("✅ 테스트 영농일지 복구 성공!")
                else:
                    print("❌ 테스트 영농일지 복구 실패!")
            
        except Exception as e:
            print(f"❌ 테스트 모드 실행 중 오류 발생: {e}")
        finally:
            # cleanup_and_exit에서 통합 처리
            self.browser_manager.cleanup_and_exit()
    
    def process_single_diary_with_schedule(self, start_date, end_date):
        """JSON 스케줄 데이터를 기반으로 주간 영농일지를 처리합니다."""
        try:
            print(f"\n=== {start_date} ~ {end_date} 영농일지 등록 시작 (스케줄 기반) ===")
            
            # 1. JSON에서 해당 주의 작업들 찾기 (시작일 기준)
            matching_tasks = self.schedule_processor.find_matching_tasks_by_date(start_date)
            
            if not matching_tasks:
                print(f"⚠️ {start_date} ~ {end_date}에 해당하는 작업이 없습니다. 기본 관리 작업으로 등록합니다.")
                # 기본 관리 작업으로 등록
                return self.process_basic_diary(start_date, end_date)
            
            # 2. 현재 페이지가 영농일지 작성 페이지인지 확인
            current_url = self.browser_manager.get_driver().current_url
            if not current_url.endswith('diaryDetail.do'):
                print("현재 페이지가 영농일지 작성 페이지가 아닙니다. 페이지 이동 중...")
                self.browser_manager.navigate_to_diary_detail_from_main()
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
                self.browser_manager.get_wait().until(
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
            matched_task = self.schedule_processor.match_task_with_gpt(selected_task["작업명"], available_tasks)
            
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
            
            # 12. 저장 전 입력 항목 체크
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
            
            # 13. 영농일지 저장
            self.save_diary()
            
            self.logger_manager.log_message(f"✅ {start_date} {selected_task['작업명']} 영농일지 등록 완료!")
            return True
            
        except Exception as e:
            self.logger_manager.log_message(f"❌ {start_date} 영농일지 등록 중 오류 발생: {e}")
            self.logger_manager.log_message("🔄 에러 복구 시도: 메인 페이지로 돌아가서 영농일지 등록 재시작...")
            return self.recover_from_error_with_schedule(start_date, end_date)
    
    def process_basic_diary(self, start_date, end_date):
        """작업이 없는 주의 기본 관리 영농일지를 등록합니다."""
        try:
            print(f"\n=== {start_date} ~ {end_date} 기본 관리 영농일지 등록 시작 ===")
            
            # 1. 현재 페이지가 영농일지 작성 페이지인지 확인
            current_url = self.browser_manager.get_driver().current_url
            if not current_url.endswith('diaryDetail.do'):
                print("현재 페이지가 영농일지 작성 페이지가 아닙니다. 페이지 이동 중...")
                self.browser_manager.navigate_to_diary_detail_from_main()
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
                self.browser_manager.get_wait().until(
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
    
    def recover_from_error_with_schedule(self, start_date, end_date=None):
        """스케줄 기반 에러 발생 시 메인 페이지로 돌아가서 영농일지 등록을 재시작합니다."""
        try:
            print("🔄 스케줄 기반 에러 복구 프로세스 시작...")
            
            # 1. 메인 페이지로 이동 (강제로 URL 이동)
            print("📄 메인 페이지로 이동 중...")
            self.browser_manager.get_driver().get(Config.DIARY_MAIN_URL)
            time.sleep(Config.FAST_WAIT_TIME)
            print("✅ 메인 페이지 이동 완료")
            
            # 2. 영농일지 등록 링크 찾기 및 클릭
            print("🔗 영농일지 등록 링크 찾는 중...")
            try:
                # 여러 방법으로 링크 찾기 시도
                diary_link = None
                
                # 방법 1: 정확한 JavaScript 링크 찾기
                try:
                    diary_link = self.browser_manager.get_driver().find_element(By.XPATH, "//a[@href=\"javascript:goView('I', 'diaryMain')\"]")
                    print("✅ 방법 1로 영농일지 등록 링크 발견")
                except:
                    pass
                
                # 방법 2: 텍스트로 찾기
                if not diary_link:
                    try:
                        diary_link = self.browser_manager.get_driver().find_element(By.XPATH, "//a[contains(text(), '영농일지 등록')]")
                        print("✅ 방법 2로 영농일지 등록 링크 발견")
                    except:
                        pass
                
                # 방법 3: 부분 href로 찾기
                if not diary_link:
                    try:
                        diary_link = self.browser_manager.get_driver().find_element(By.XPATH, "//a[contains(@href, 'goView') and contains(@href, 'diaryMain')]")
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
                self.browser_manager.get_driver().get(Config.DIARY_DETAIL_URL)
            
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
    
    # 웹 요소 조작 메서드들 (기존 코드에서 가져와서 수정)
    def set_date_range(self, start_date, end_date):
        """시작일과 종료일을 설정합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def select_crop(self):
        """품목을 선택합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def select_all_lands(self):
        """모든 필지를 선택합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def select_all_crops(self):
        """모든 품종을 선택합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def get_available_task_steps(self):
        """웹페이지에서 사용 가능한 작업단계 목록을 가져옵니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def select_task_step(self, task_step):
        """작업 단계를 선택합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def handle_additional_fields(self, task_step):
        """작업 단계별 추가 입력 필드를 처리합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def get_weather_data(self):
        """영농일지 페이지에서 날씨 정보를 수집합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def generate_weather_aware_content(self, task_name, selected_date, weather_data):
        """날씨 정보를 고려한 현실적인 작업 내용 생성"""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def generate_basic_diary_content(self, date, weather_data):
        """기본 관리 영농일지 내용을 생성합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def enter_memo_with_content(self, content):
        """생성된 내용으로 메모를 입력합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def check_input_fields(self):
        """입력 항목들이 올바르게 설정되었는지 확인합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def retry_input_fields(self, missing_fields):
        """누락된 입력 항목들을 다시 설정합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass
    
    def save_diary(self):
        """영농일지를 저장합니다."""
        # 기존 코드에서 가져와서 수정 필요
        pass


if __name__ == "__main__":
    # 테스트 모드로 실행
    macro = AgrionMacroRefactored(test_mode=True)
    macro.run_test_mode()
