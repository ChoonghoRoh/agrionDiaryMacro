#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
농업ON 영농일지 자동 등록 매크로 - 버전 선택

사용자가 원하는 버전을 선택하여 실행할 수 있습니다.
"""

import os
import sys
import subprocess

def show_version_info():
    """버전 정보를 표시합니다."""
    print("🌾 농업ON 영농일지 자동 등록 매크로")
    print("=" * 60)
    print()
    print("📋 사용 가능한 버전:")
    print()
    print("1️⃣  v1.0 (기존 버전)")
    print("   - 단일 파일 구조")
    print("   - 2,255줄의 통합된 코드")
    print("   - 안정적이지만 유지보수 어려움")
    print()
    print("2️⃣  v2.0 (리팩토링 버전)")
    print("   - 모듈화 구조")
    print("   - 300-400줄의 분리된 모듈")
    print("   - 유지보수 용이, 테스트 가능")
    print()
    print("3️⃣  버전 정보 상세 보기")
    print("4️⃣  종료")
    print()

def show_detailed_info():
    """상세한 버전 정보를 표시합니다."""
    print("\n📊 버전 비교표")
    print("-" * 60)
    print(f"{'항목':<15} {'v1.0':<20} {'v2.0':<20} {'개선도'}")
    print("-" * 60)
    print(f"{'파일 구조':<15} {'단일 파일':<20} {'모듈화':<20} {'대폭 개선'}")
    print(f"{'코드 라인':<15} {'2,255줄':<20} {'300-400줄':<20} {'80% 감소'}")
    print(f"{'유지보수성':<15} {'낮음':<20} {'높음':<20} {'대폭 개선'}")
    print(f"{'테스트 용이성':<15} {'어려움':<20} {'쉬움':<20} {'대폭 개선'}")
    print(f"{'재사용성':<15} {'낮음':<20} {'높음':<20} {'대폭 개선'}")
    print(f"{'확장성':<15} {'제한적':<20} {'높음':<20} {'대폭 개선'}")
    print("-" * 60)
    print()

def run_version(version):
    """선택된 버전을 실행합니다."""
    if version == "1":
        print("🚀 v1.0 실행 중...")
        script_path = os.path.join(os.path.dirname(__file__), 'run_v1.py')
        subprocess.run([sys.executable, script_path])
    elif version == "2":
        print("🚀 v2.0 실행 중...")
        script_path = os.path.join(os.path.dirname(__file__), 'run_v2.py')
        subprocess.run([sys.executable, script_path])
    else:
        print("❌ 잘못된 선택입니다.")

def main():
    """메인 함수"""
    while True:
        show_version_info()
        
        try:
            choice = input("실행할 버전을 선택하세요 (1-4): ").strip()
            
            if choice == "1":
                run_version("1")
                break
            elif choice == "2":
                run_version("2")
                break
            elif choice == "3":
                show_detailed_info()
                input("계속하려면 Enter를 누르세요...")
            elif choice == "4":
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("⚠️ 1-4 사이의 숫자를 입력해주세요.")
                input("계속하려면 Enter를 누르세요...")
                
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 오류가 발생했습니다: {e}")
            input("계속하려면 Enter를 누르세요...")

if __name__ == "__main__":
    main()
