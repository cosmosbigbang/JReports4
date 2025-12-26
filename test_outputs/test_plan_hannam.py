"""
plan.pdf (한남동) 기본 정보 추출
"""
import base64
import requests
import json
from api_config import OPENAI_API_KEY

print("="*60)
print("📄 plan.pdf 분석 (한남동)")
print("="*60)

with open('plan_hannam.jpg', 'rb') as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

prompt = """이 건설 공사개요 문서에서 정보를 추출해주세요.

**필수 정보**:
1. 공사명/현장명
2. 위치/주소 - 특히 "동"과 "번지" 정확히
3. 시공사
4. 발주처/건축주
5. 공사기간
6. 건물규모
7. 굴착깊이

**중요**: 
- 주소에서 "○○동"과 "123-4" 같은 번지를 정확히 찾아주세요
- 표의 내용을 정확히 읽어주세요

JSON 형식:
{
  "project_name": "공사명",
  "location": "전체주소",
  "location_dong": "한남동",
  "location_bunji": "383-1",
  "contractor": "시공사",
  "client": "발주처",
  "period": "기간",
  "building_scale": "규모",
  "excavation_depth": "굴착깊이"
}"""

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
    print("\n원본 응답:")
    print(content)
    
    try:
        content_clean = content.replace("```json", "").replace("```", "").strip()
        result = json.loads(content_clean)
        
        print("\n" + "="*60)
        print("✅ 추출된 정보")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        folder_name = f"{result.get('location_dong', '')}_{result.get('location_bunji', '')}"
        print(f"\n📁 폴더명: {folder_name}")
        
    except Exception as e:
        print(f"\n❌ JSON 파싱 실패: {e}")
else:
    print(f"❌ API 오류: {response.status_code}")
    print(response.text)
