# test_engine.py

import sys
import os
import django

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from reports.pdf_parser import extract_project_info
from reports.excel_builder import create_excel_files

# 1. 현장명 설정
project_name = "한남동_383-1" 
print(f"--- [1] 현장명: {project_name} ---")

# 2. 엑셀 파일 생성 (CSV 파일 분석 기반 실제 수량)
print("\n--- [2] 엑셀 파일 생성 시작 ---")

real_site_counts = {
    'SE': 9,   # P.1 ~ P.9
    'S': 21,   # S1 ~ S7 (x3단) = 21개 가정
    'I': 5,    # I-1 ~ I-5 (중요! 누락되었던 것)
    'W': 5,    # W-1 ~ W-5 (중요! 누락되었던 것)
    'C': 18,   # C-1 ~ C-18 (중요! 누락되었던 것)
    'T': 18,   # T-1 ~ T-18
    'FM': 0    # 유량계 삭제 (사용 안 함)
}

logs = create_excel_files(real_site_counts, project_name)

print("\n[최종 생성 결과]")
for log in logs:
    print(log)