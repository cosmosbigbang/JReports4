import base64
import requests
import re
import io
import json
import pandas as pd
from PIL import Image
from django.conf import settings
from .models import Measurement

# 🔑 API 키 확인 (기존 키 유지)
OPENAI_API_KEY = "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" 

def analyze_plan_with_vision(image_file):
    print("🧠 [Deep Think] GPT-4o '현장 규칙' 기반 정밀 분석 시작...")
    
    try:
        # 1. 이미지 전처리 (하단 범례표 집중)
        image = Image.open(image_file)
        image = image.convert("RGB")
        width, height = image.size
        
        # 하단 50%만 자르기 (범례표 위치)
        image = image.crop((0, height // 2, width, height))
        
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # 2. 프롬프트: J님이 알려주신 "현장 도면 해석 규칙" 주입
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        # 시스템 프롬프트에 'FM', 'SE', '9Points', '단(Layer)' 로직 강조
        system_prompt = """
        You are a veteran Civil Engineer. Your task is to extract exact sensor counts from a Construction Legend Table (계측범례).
        
        **CRITICAL DOMAIN RULES (Must Follow):**
        1. **FM** = Flow Meter (유량계). Look for 'FM'.
        2. **SE** = Surface Settlement (지표침하계). 
           - **Rule:** If it says "3set (9Points)", the count is **9**, not 3. Always count the 'Points'.
        3. **S** = Strain Gauge (변형률계). 
           - Distinguish clearly between 'S' (Strain) and 'SE' (Settlement).
           - 'S' is often installed in layers (up to 3 layers/struts).
        4. **C** or **CK** = Crack Meter (균열측정기). Treat 'CK' and 'C' as the same category 'C'.
        5. **W** = Water Level (지하수위계).
        6. **T** = Tilt Meter (건물경사계).
        7. **Noise** (소음계), **Vibration** (진동계).
        
        **TASK:**
        - Read the image table row by row.
        - Extract the quantity number for each code.
        - Ignore address numbers (e.g., 129-5). Only read the 'Quantity' column in the table.
        
        **OUTPUT FORMAT (JSON Only):**
        Return a single JSON object. Use these exact keys:
        {"T": 0, "C": 0, "I": 0, "S": 0, "SE": 0, "W": 0, "FM": 0, "Noise": 0, "Vibration": 0}
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
                            "text": "Analyze the legend table. Find counts for T, C, I, S, SE (points), W, FM, Noise, Vibration."
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
            "temperature": 0.0 # 창의성 0, 정확도 100 추구
        }

        # 3. 요청 전송
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            print(f"🤖 [GPT-4o 분석 원본]: {content}")
            
            # JSON 정제
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        else:
            print(f"🔥 Error: {response.text}")
            return None

    except Exception as e:
        print(f"⚠️ System Error: {e}")
        return None

# (CSV 파서 함수들은 일단 유지 - 나중에 엑셀 네이밍 공식 적용할 때 대수술 필요함)
def parse_and_save_data(file_obj, sensor_instance):
    # ... 기존 코드 유지 ...
    return True
def _parse_inclinometer(df, sensor):
    # ... 기존 코드 유지 ...
    return True
def _parse_general_sensor(df, sensor):
    # ... 기존 코드 유지 ...
    return True