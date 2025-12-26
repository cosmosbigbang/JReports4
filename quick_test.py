import openpyxl
import os

# 1. 원본 시트 개수 확인
files = {
    'T': '5. 건물경사계 (한남동).xlsx',
    'C': '4. 균열측정계(한남동).xlsx',
    'SE': '6. 지표침하계(한남동).xlsx',
    'S': '3. 변형률계(1~7 3단샘플).xlsx',
    'W': '2. 지하수위계(한남동).xlsx',
    'I': '1. 지중경사계(한남동).xlsx'
}

print("=== 원본 템플릿 시트 개수 ===")
counts = {}
for k, v in files.items():
    wb = openpyxl.load_workbook(f'excel/{v}', data_only=False)
    counts[k] = len(wb.sheetnames)
    print(f"{k}: {counts[k]}개")
    wb.close()

print(f"\n생성할 파일: {counts}")

# 2. 동일 개수로 파일 생성
from excel_template_cloner import create_all_sensor_files
create_all_sensor_files(counts, "원본동일테스트")

# 3. 파일 크기 비교
print("\n=== 파일 크기 비교 ===")
sensor_names = {
    'T': '건물경사계',
    'C': '균열측정계',
    'SE': '지표침하계',
    'S': '변형률계',
    'W': '지하수위계',
    'I': '지중경사계'
}

for k, v in files.items():
    orig_size = os.path.getsize(f'excel/{v}')
    gen_file = f'generated_excels/원본동일테스트/{sensor_names[k]}(원본동일테스트).xlsx'
    gen_size = os.path.getsize(gen_file)
    diff = ((gen_size - orig_size) / orig_size) * 100
    print(f"{k}: 원본={orig_size:,} bytes, 생성={gen_size:,} bytes, 차이={diff:+.1f}%")
