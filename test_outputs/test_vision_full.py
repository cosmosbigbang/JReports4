"""
전체 이미지 vs 하단 50% 비교 테스트
"""
import base64
import requests
import json
from PIL import Image
import io
from api_config import OPENAI_API_KEY

def analyze_image(image, desc):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """이 건설 계측계획평면도를 분석해주세요:

1. **범례표(계측범례)에서 계측기 정보 추출**:
   - T (건물경사계)
   - C/CK (균열측정계)
   - I (지중경사계)
   - S (변형률계) - 단수 주의
   - SE (지표침하계) - Points 개수
   - W (지하수위계)
   
2. **기본 정보**:
   - 현장명/공사명
   - 주소 (동, 번지)
   - 시공사
   
자세히 분석해서 JSON으로 답변해주세요."""
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
        "max_tokens": 1500,
        "temperature": 0.0
    }
    
    print(f"\n{'='*60}")
    print(f"🔍 {desc}")
    print('='*60)
    
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60
    )
    
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        print(content)
        return content
    else:
        print(f"❌ 오류: {response.status_code}")
        return None

# 원본 이미지
image = Image.open('c-018.jpg')
image = image.convert("RGB")
width, height = image.size

# 테스트 1: 전체 이미지
result1 = analyze_image(image, "전체 이미지 분석")

# 테스트 2: 하단 50%
image_bottom = image.crop((0, height // 2, width, height))
result2 = analyze_image(image_bottom, "하단 50% (범례 영역)")

# 테스트 3: 하단 30%
image_bottom30 = image.crop((0, int(height * 0.7), width, height))
result3 = analyze_image(image_bottom30, "하단 30% (범례 영역)")
