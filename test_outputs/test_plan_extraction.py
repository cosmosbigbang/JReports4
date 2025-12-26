"""
plan.pdf (C-003 공사개요) 기본 정보 추출
"""
import base64
import requests
import json
import pdfplumber
from PIL import Image
import io
from api_config import OPENAI_API_KEY

# PDF를 이미지로 변환
print("="*60)
print("📄 C-003 공사개요 및 주요시방.pdf → 이미지 변환")
print("="*60)

with pdfplumber.open('uploads/C-003 공사개요 및 주요시방.pdf') as pdf:
    page = pdf.pages[0]
    
    # 고해상도 이미지로 변환
    img = page.to_image(resolution=200)
    pil_img = img.original
    
    # 저장
    pil_img.save('plan_page1.jpg')
    print(f"✅ 저장: plan_page1.jpg ({pil_img.size[0]} x {pil_img.size[1]})")

# Vision API로 분석
print("\n🤖 GPT-4o Vision 분석 중...\n")

with open('plan_page1.jpg', 'rb') as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

prompt = """이 건설 공사개요 문서에서 다음 정보를 정확히 추출해주세요:

**필수 정보**:
1. 공사명 (또는 현장명)
2. 위치/주소 (동, 번지 포함)
3. 시공사 (건설사)
4. 발주처 (건축주, 건설사)
5. 공사기간
6. 건물규모 (층수, 면적 등)
7. 굴착깊이

**출력 형식 (JSON)**:
```json
{
  "project_name": "공사명",
  "location": "주소",
  "location_dong": "○○동",
  "location_bunji": "123-4",
  "contractor": "시공사명",
  "client": "발주처명",
  "period": "공사기간",
  "building_scale": "건물규모",
  "excavation_depth": "굴착깊이"
}
```

표에서 정확한 값을 찾아서 입력해주세요."""

payload = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ],
    "max_tokens": 1000,
    "temperature": 0.0
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json=payload,
    timeout=60
)

if response.status_code == 200:
    content = response.json()['choices'][0]['message']['content']
    print("원본 응답:")
    print(content)
    
    # JSON 추출
    try:
        content_clean = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content_clean)
        
        print("\n" + "="*60)
        print("✅ 추출된 기본 정보")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # 폴더명 생성 (동_번지)
        folder_name = f"{result.get('location_dong', '현장')}_{result.get('location_bunji', '')}"
        print(f"\n📁 생성될 폴더명: {folder_name}")
        
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
else:
    print(f"❌ API 오류: {response.status_code}")
    print(response.text)
