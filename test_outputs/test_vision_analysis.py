"""
PDF 이미지 분석 테스트 - GPT-4o Vision (독립 실행)
"""
import base64
import requests
import json
from PIL import Image
import io
from api_config import OPENAI_API_KEY

print("="*60)
print("🔍 c-018.jpg 분석 테스트")
print("="*60)

# 이미지 로드 (전체 이미지 사용)
image = Image.open('c-018.jpg')
image = image.convert("RGB")
width, height = image.size
print(f"원본 크기: {width} x {height}")

# 전체 이미지 사용 (범례표 위치를 GPT가 찾도록)
image_cropped = image
print(f"분석 영역: 전체")

# Base64 인코딩
buffered = io.BytesIO()
image_cropped.save(buffered, format="JPEG")
base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

# GPT-4o Vision API 호출
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

system_prompt = """
You are analyzing a Construction Measurement Plan (계측계획평면도).

**CRITICAL INSTRUCTIONS:**
1. Find the LEGEND TABLE (범례표 or 계측범례) - usually at bottom of the drawing
2. The table has columns: [Symbol/Code | Name | Quantity]
3. Extract EXACT numbers from the Quantity column

**SENSOR CODES:**
- **T** = 건물경사계 (Building Tiltmeter)
- **C** or **CK** = 균열측정계 (Crack Meter) - treat as same
- **I** = 지중경사계 (Inclinometer)
- **S** = 변형률계 (Strain Gauge) - NOT to be confused with SE
- **SE** = 지표침하계 (Surface Settlement) - count POINTS not sets (if "3set 9points" → 9)
- **W** = 지하수위계 (Water Level Meter)

**IMPORTANT:**
- DO NOT confuse T (Tiltmeter) with S (Strain)
- DO NOT confuse S (Strain) with SE (Settlement)
- Read the table carefully row by row
- Return EXACT numbers from the table

**OUTPUT (JSON only):**
{"T": 0, "C": 0, "I": 0, "S": 0, "SE": 0, "W": 0, "FM": 0}
"""

payload = {
    "model": "gpt-4o",
    "messages": [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": """Find the LEGEND TABLE (범례표) in this construction plan.
                    
Read each row carefully and extract the quantity for:
- T (건물경사계)
- C/CK (균열측정계)  
- I (지중경사계)
- S (변형률계)
- SE (지표침하계) - count Points
- W (지하수위계)

Be very careful not to mix up T with S, or S with SE.
Return exact numbers from the table."""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ],
    "max_tokens": 500,
    "temperature": 0.0
}

print("\n🤖 GPT-4o Vision 호출 중...\n")
response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers=headers,
    json=payload,
    timeout=60
)

if response.status_code == 200:
    content = response.json()['choices'][0]['message']['content']
    print(f"원본 응답:\n{content}\n")
    
    # JSON 정제
    content = content.replace("```json", "").replace("```", "").strip()
    result = json.loads(content)
    
    print("\n✅ 추출된 계측기 정보:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    print("\n📊 요약:")
    total = 0
    for sensor_type, count in result.items():
        if count > 0:
            print(f"  {sensor_type}: {count}개")
            total += count
    print(f"\n  총 계측기: {total}개")
else:
    print(f"❌ API 오류: {response.status_code}")
    print(response.text)
