#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v2.0 실행 스크립트

리팩토링된 모듈화 구조의 v2.0 버전을 실행합니다.
"""

import os
import sys
import subprocess

def main():
    """v2.0 실행"""
    print("🌾 농업ON 영농일지 자동 등록 매크로 v2.0")
    print("=" * 50)
    
    # v2.0 디렉토리로 이동
    v2_dir = os.path.join(os.path.dirname(__file__), 'v2.0')
    
    if not os.path.exists(v2_dir):
        print("❌ v2.0 디렉토리를 찾을 수 없습니다.")
        return
    
    # v2.0의 start_diary_writer_v2.py 실행
    script_path = os.path.join(v2_dir, 'main', 'start_diary_writer_v2.py')
    
    if not os.path.exists(script_path):
        print("❌ v2.0의 start_diary_writer_v2.py를 찾을 수 없습니다.")
        return
    
    print(f"📁 v2.0 디렉토리로 이동: {v2_dir}")
    print(f"🚀 스크립트 실행: {script_path}")
    print("-" * 50)
    
    try:
        # 현재 작업 디렉토리를 v2.0으로 변경하고 스크립트 실행
        subprocess.run([sys.executable, script_path], cwd=v2_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ v2.0 실행 중 오류 발생: {e}")
    except KeyboardInterrupt:
        print("\n⚠️ 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")

if __name__ == "__main__":
    main()
