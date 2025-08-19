#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v2.0 농업ON 영농일지 자동 등록 매크로 실행 스크립트

리팩토링된 모듈화 구조를 사용하는 v2.0 버전입니다.
"""

import sys
import os

# v2.0 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from main.agrion_macro_refactored import AgrionMacroRefactored


def main():
    """메인 실행 함수"""
    print("🌾 농업ON 영농일지 자동 등록 매크로 v2.0")
    print("=" * 50)
    
    # 모드 선택
    print("\n실행 모드를 선택하세요:")
    print("1. 테스트 모드 (1개 일지 등록)")
    print("2. 전체 모드 (전체 기간 일지 등록)")
    
    while True:
        mode = input("\n모드를 선택하세요 (1 또는 2): ").strip()
        if mode in ['1', '2']:
            break
        print("⚠️ 1 또는 2를 입력해주세요.")
    
    # 매크로 인스턴스 생성
    macro = None
    try:
        # 테스트 모드 설정
        test_mode = (mode == '1')
        macro = AgrionMacroRefactored(test_mode=test_mode)
        
        if test_mode:
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
            macro.browser_manager.cleanup_and_exit()
        print("📝 로그 파일이 안전하게 저장되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 매크로 실행 중 오류가 발생했습니다: {e}")
        if macro:
            macro.browser_manager.cleanup_and_exit()
        print("📝 로그 파일을 확인하여 오류 내용을 확인하세요.")
    finally:
        print("\n✅ 매크로가 종료되었습니다.")


if __name__ == "__main__":
    main()
