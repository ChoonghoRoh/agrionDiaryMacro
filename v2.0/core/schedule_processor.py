import json
import re
import os
from datetime import datetime, timedelta


class ScheduleProcessor:
    """농작업 스케줄 데이터를 처리하는 클래스"""
    
    def __init__(self):
        self.schedule_data = None
        self.load_schedule_data()
    
    def load_schedule_data(self):
        """농작업 일정 데이터를 로드합니다."""
        try:
            data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'shared', 'data', 'rice_schedule_data.json')
            with open(data_path, 'r', encoding='utf-8') as f:
                self.schedule_data = json.load(f)
            print("✅ 농작업 일정 데이터 로드 완료")
        except Exception as e:
            print(f"❌ 농작업 일정 데이터 로드 실패: {e}")
            self.schedule_data = None
    
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
    
    def get_schedule_data(self):
        """스케줄 데이터를 반환합니다."""
        return self.schedule_data
