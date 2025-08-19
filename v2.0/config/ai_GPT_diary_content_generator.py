import openai
from settings import Config

class ContentGenerator:
    def __init__(self):
        # openai.api_key 설정 제거 (OpenAI 클라이언트에서 직접 설정)
        pass
        
    def generate_diary_content(self, task_step, crop_type, use_gpt=True, current_date=None):
        """작업 단계에 따른 영농일지 내용을 생성합니다.
        
        Args:
            task_step (str): 작업 단계 (예: "파종작업", "이앙작업")
            crop_type (str): 작물 종류 (예: "벼", "감자")
            use_gpt (bool): GPT 사용 여부 (기본값: True)
            current_date (str): 현재 날짜 (예: "2024-01-01")
        """
        
        # 작업 단계별 기본 템플릿 (GPT 사용하지 않을 때, 100자 제한)
        task_prompts = {
            # 기본 작업
            "씨뿌리기": f"{crop_type} 씨뿌리기 작업을 진행했습니다. 토양 상태를 확인하고 적절한 깊이로 씨를 뿌렸습니다.",
            "모내기": f"{crop_type} 모내기 작업을 완료했습니다. 모의 상태가 양호하여 정식 작업을 진행했습니다.",
            "비료주기": f"{crop_type} 비료주기 작업을 실시했습니다. 작물 생육에 필요한 영양분을 공급했습니다.",
            "농약살포": f"{crop_type} 농약살포 작업을 진행했습니다. 병해충 방제를 위해 적절한 농약을 살포했습니다.",
            "물관리": f"{crop_type} 물관리 작업을 실시했습니다. 작물 생육에 적합한 수분을 유지하도록 관리했습니다.",
            "수확": f"{crop_type} 수확 작업을 완료했습니다. 적절한 시기에 수확하여 품질을 확보했습니다.",
            
            # 실제 웹 옵션 기반 (100자 이내로 간결하게)
            "파종작업": f"{crop_type} 파종작업을 진행했습니다. 토양 상태를 확인하고 적절한 깊이로 종자를 파종했습니다.",
            "볍씨소독작업": f"{crop_type} 볍씨소독작업을 실시했습니다. 종자 소독을 통해 병해충을 예방했습니다.",
            "이앙작업": f"{crop_type} 이앙작업을 완료했습니다. 모의 상태가 양호하여 정식 작업을 진행했습니다.",
            "비료작업": f"{crop_type} 비료작업을 실시했습니다. 작물 생육에 필요한 영양분을 공급했습니다.",
            "방제작업": f"{crop_type} 방제작업을 진행했습니다. 병해충 방제를 위해 적절한 농약을 살포했습니다.",
            "중간물떼기": f"{crop_type} 중간물떼기 작업을 실시했습니다. 작물 생육에 적합한 수분을 유지하도록 관리했습니다.",
            "완전물떼기": f"{crop_type} 완전물떼기 작업을 완료했습니다. 수확 전 적절한 시기에 물을 완전히 뗐습니다.",
            "수확작업": f"{crop_type} 수확작업을 완료했습니다. 적절한 시기에 수확하여 품질을 확보했습니다.",
            "출하/판매작업": f"{crop_type} 출하/판매작업을 진행했습니다. 수확한 작물을 정리하여 출하 준비를 완료했습니다.",
            "건조작업": f"{crop_type} 건조작업을 실시했습니다. 수확한 작물을 적절한 수분으로 건조했습니다.",
            "병해충 피해": f"{crop_type} 병해충 피해 상황을 확인했습니다. 피해 정도를 파악하고 대응 방안을 마련했습니다.",
            "제초작업": f"{crop_type} 제초작업을 진행했습니다. 잡초를 제거하여 작물 생육 환경을 개선했습니다.",
            "논갈이(쟁기)작업": f"{crop_type} 논갈이(쟁기)작업을 실시했습니다. 토양을 갈아엎어 작물 재배 환경을 준비했습니다.",
            "치상작업": f"{crop_type} 치상작업을 진행했습니다. 모를 키우기 위한 치상 작업을 완료했습니다.",
            "로터리작업": f"{crop_type} 로터리작업을 실시했습니다. 토양을 부숴서 작물 재배에 적합한 환경을 만들었습니다.",
            "작기종료": f"{crop_type} 작기종료 작업을 완료했습니다. 이번 작기의 모든 작업을 마무리했습니다.",
            "기타작업": f"{crop_type} 기타작업을 진행했습니다. 농장 관리에 필요한 추가 작업을 실시했습니다.",
            "교육일정": f"{crop_type} 교육일정에 참여했습니다. 농업 기술 향상을 위한 교육을 받았습니다.",
            "예찰활동": f"{crop_type} 예찰활동을 진행했습니다. 병해충 발생 상황을 모니터링했습니다."
        }
        
        # GPT 사용하지 않거나 API 키가 없는 경우 기본 템플릿 사용
        if not use_gpt or not Config.OPENAI_API_KEY:
            print(f"기본 템플릿을 사용합니다. (GPT 사용: {use_gpt}, API 키: {'있음' if Config.OPENAI_API_KEY else '없음'})")
            content = task_prompts.get(task_step, f"{crop_type} {task_step} 작업을 진행했습니다.")
            
            # 100자로 제한
            if len(content) > 200:
                content = content[:197] + "..."
            
            print(f"기본 템플릿 내용 ({len(content)}자): {content}")
            return content
        
        # GPT를 사용하여 더 상세한 내용 생성 (토큰 비용 최소화)
        try:
            print(f"ChatGPT API를 사용하여 '{task_step}' 작업 내용을 생성합니다...")
            
            # 날짜 정보가 있으면 프롬프트에 포함
            if current_date:
                prompt = f"{current_date} {crop_type} {task_step} 영농인에 대입하여 작성. 작업 영농일지 200자 이내로 작성. 날짜를 정확히 사용하세요."
            else:
                prompt = f"{crop_type} {task_step} 영농인에 대입하여 작성. 작업 영농일지 200자 이내로 작성"
            
            # OpenAI API 호출 (Config 설정 사용)
            openai.api_key = Config.OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model=Config.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "농업인 영농일지 작성. 200자 이내."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=Config.GPT_MAX_TOKENS,
                temperature=Config.GPT_TEMPERATURE
            )
            
            # GPT가 생성한 내용 반환 (200자 제한)
            generated_content = response.choices[0].message.content.strip()
            
            # 100자로 제한
            if len(generated_content) > 200:
                generated_content = generated_content[:197] + "..."
            
            print(f"GPT가 생성한 내용 ({len(generated_content)}자): {generated_content}")
            return generated_content
            
        except Exception as e:
            print(f"ChatGPT API 호출 중 오류 발생: {e}")
            print("기본 템플릿을 사용합니다.")
            # API 오류 시 기본 내용 반환
            return task_prompts.get(task_step, f"{crop_type} {task_step} 작업을 진행했습니다.")
