#!/usr/bin/env python3
"""
농업ON 영농일지 자동 등록 매크로 실행 파일
"""

import os
import sys
from auto_diary_writer import AgrionMacro

def main():
    """메인 실행 함수"""
    print("=" * 50)
    print("농업ON 영농일지 자동 등록 매크로")
    print("=" * 50)
    
    # 환경 변수 확인
    if not os.path.exists('.env'):
        print("❌ .env 파일이 없습니다.")
        print(".env.example를 복사하여 .env 파일을 생성하고 설정을 입력하세요.")
        print("cp .env.example .env")
        return
    
    # 설정 확인
    from settings import Config
    
    if not Config.USERNAME or not Config.PASSWORD:
        print("❌ 로그인 정보가 설정되지 않았습니다.")
        print(".env 파일에서 AGRION_USERNAME과 AGRION_PASSWORD를 설정하세요.")
        return
    
    print(f"✅ 로그인 정보: {Config.USERNAME}")
    print(f"✅ 시작 날짜: {Config.START_DATE}")
    print(f"✅ 종료 날짜: {Config.END_DATE}")
    print(f"✅ 품목: {Config.CROP_TYPE}")
    
    if Config.OPENAI_API_KEY:
        print("✅ ChatGPT API 키가 설정되어 있습니다.")
    else:
        print("⚠️  ChatGPT API 키가 설정되지 않았습니다. 기본 템플릿을 사용합니다.")
    
    # 실행 모드 선택
    print("\n실행 모드를 선택하세요:")
    print("1. 테스트 모드 (글 등록 1개만)")
    print("2. 전체 모드 (모든 작업 단계 등록)")
    print("3. 취소")
    
    while True:
        mode = input("선택 (1/2/3): ").strip()
        if mode in ['1', '2', '3']:
            break
        print("1, 2, 3 중에서 선택해주세요.")
    
    if mode == '3':
        print("매크로 실행을 취소했습니다.")
        return
    
    macro = None
    try:
        # 매크로 실행
        macro = AgrionMacro()
        
        if mode == '1':
            # 테스트 모드 - 글 등록 1개만
            print("\n=== 테스트 모드 시작 ===")
            macro.run_test_mode()
        else:
            # 전체 모드
            print("\n=== 전체 모드 시작 ===")
            macro.run_macro()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 사용자에 의해 매크로가 중단되었습니다.")
        if macro:
            macro.cleanup_and_exit()
        print("📝 로그 파일이 안전하게 저장되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 매크로 실행 중 오류가 발생했습니다: {e}")
        if macro:
            macro.cleanup_and_exit()
        print("📝 로그 파일을 확인하여 오류 내용을 확인하세요.")
    finally:
        print("\n✅ 매크로가 종료되었습니다.")

if __name__ == "__main__":
    main()
