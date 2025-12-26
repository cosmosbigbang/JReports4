import requests
import json

# 서버 URL
BASE_URL = 'http://127.0.0.1:8000'

# 1단계: plan.pdf 업로드 → 프로젝트 정보 추출
print("📋 [1단계] plan.pdf 업로드 중...")
with open('C-003plan.pdf', 'rb') as f:
    response = requests.post(f'{BASE_URL}/api/analyze/plan/', files={'plan_file': f})
    result = response.json()
    print(f"✅ 결과: {result}")
    
    if result['status'] != 'success':
        print("❌ 프로젝트 생성 실패")
        exit()
    
    project_id = result['project_id']
    project_name = result['project_name']
    print(f"📁 프로젝트명: {project_name} (ID: {project_id})")

# 2단계: 센서 수량 입력 (6종)
print("\n📊 [2단계] 센서 수량 입력 중...")
sensor_counts = {
    "T": 6,   # 건물경사계
    "C": 18,  # 균열측정계
    "I": 3,   # 지중경사계
    "S": 12,  # 변형률계
    "SE": 9,  # 지표침하계
    "W": 2    # 지하수위계
}

payload = {
    "project_id": project_id,
    "counts": sensor_counts
}

response = requests.post(
    f'{BASE_URL}/api/create/sensors/',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(payload)
)

result = response.json()
print(f"✅ 결과: {result}")

if result['status'] == 'success':
    print(f"\n🎉 완료!")
    print(f"- 생성된 센서: {len(result['created_sensors'])}개")
    print(f"- 엑셀 파일: {result['excel_files']}")
    print(f"- 저장 폴더: {result['output_folder']}")
else:
    print("❌ 센서 생성 실패")
