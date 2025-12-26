import pdfplumber
import re
import os

def extract_project_info(pdf_path):
    """
    plan.pdf에서 텍스트를 추출하여 프로젝트 핵심 정보(현장명_번지)를 반환합니다.
    파일명 생성용: '한남동_383-1'
    """
    if not os.path.exists(pdf_path):
        print(f"🔥 [Error] 파일이 없습니다: {pdf_path}")
        return "현장미상"

    full_text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # 보통 1페이지에 개요(Overview)가 있음. 
            # 혹시 모르니 1~3페이지까지 뒤짐.
            for i in range(min(3, len(pdf.pages))):
                text = pdf.pages[i].extract_text()
                if text:
                    full_text += text + "\n"
        
        # 디버깅: 읽어온 텍스트 확인 (로그에 찍힘)
        # print(f"📄 [PDF Raw Text]:\n{full_text[:300]}...") 

        # ---------------------------------------------------------
        # 🎯 [Deep Think] 정규식(Regex)으로 주소 사냥
        # ---------------------------------------------------------
        
        # 1. '동' 찾기 (예: 한남동, 서초동, 역삼동)
        # 패턴: 한글 2~4글자 + '동' + 공백/특수문자
        dong_match = re.search(r'([가-힣]{2,4}동)', full_text)
        dong = dong_match.group(1) if dong_match else "현장"

        # 2. '번지' 찾기 (예: 383-1, 12-5, 100번지)
        # 패턴: 숫자 + '-' + 숫자 (또는 그냥 숫자)
        # 주소 뒤에 보통 번지가 옴.
        bunji_match = re.search(r'(\d+-\d+)', full_text)
        if not bunji_match:
            # 하이픈 없는 번지 (예: 383) 시도
            bunji_match = re.search(r'(\d+)번지', full_text)
            
        bunji = bunji_match.group(1) if bunji_match else ""

        # 3. 최종 조합
        if bunji:
            result = f"{dong}_{bunji}"
        else:
            result = dong

        print(f"📍 [PDF 분석 완료] 추출된 현장명: {result}")
        return result

    except Exception as e:
        print(f"⚠️ [PDF 파싱 실패] {e}")
        return "현장미상"