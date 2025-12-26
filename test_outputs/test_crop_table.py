"""
계측범례 테이블만 정확히 crop해서 분석
"""
import base64
import requests
import json
from PIL import Image
import io
from api_config import OPENAI_API_KEY

# 이미지 로드
image = Image.open('c-018.jpg')
width, height = image.size
print(f"원본 크기: {width} x {height}")

# 여러 영역으로 테스트
crops = {
    "우측_하단_40%": (int(width * 0.5), int(height * 0.6), width, height),
    "우측_하단_50%": (int(width * 0.5), int(height * 0.5), width, height),
    "우측_중하단": (int(width * 0.5), int(height * 0.4), width, int(height * 0.8)),
}

def analyze_crop(img_crop, name):
    # 저장해서 확인
    img_crop.save(f'crop_{name}.jpg')
    print(f"\n✅ 저장: crop_{name}.jpg ({img_crop.size[0]} x {img_crop.size[1]})")
    
    # Base64 인코딩
    buffered = io.BytesIO()
    img_crop.save(buffered, format="JPEG")
    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    prompt = """이미지에서 "계측범례" 또는 "전체수량" 표를 찾아주세요.

표의 각 행에서:
- 계측기 코드 (T, C, I, S, SE, W 등)
- 수량

을 정확히 읽어주세요.

**중요**: 
- T (건물경사계)와 S (변형률계)를 혼동하지 마세요
- SE (지표침하계)는 Points 개수를 세세요
- 표의 모든 행을 빠짐없이 읽어주세요

JSON 형식으로 답변:
{"T": 숫자, "C": 숫자, "I": 숫자, "S": 숫자, "SE": 숫자, "W": 숫자}"""
    
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
        "max_tokens": 800,
        "temperature": 0.0
    }
    
    print(f"\n{'='*60}")
    print(f"🔍 분석 중: {name}")
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
        
        # JSON 추출
        try:
            content_clean = content.replace("```json", "").replace("```", "").strip()
            result = json.loads(content_clean)
            print(f"\n추출 결과: {result}")
            
            # 정답과 비교
            correct = {"T": 27, "C": 27, "I": 4, "S": 13, "SE": 9, "W": 4}
            print("\n비교:")
            for key in correct:
                if key in result:
                    status = "✅" if result[key] == correct[key] else "❌"
                    print(f"  {key}: {result[key]} (정답: {correct[key]}) {status}")
        except:
            pass
    else:
        print(f"❌ 오류: {response.status_code}")

# 각 영역 테스트
for name, coords in crops.items():
    img_crop = image.crop(coords)
    analyze_crop(img_crop, name)
