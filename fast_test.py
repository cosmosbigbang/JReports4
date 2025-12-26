import openpyxl

files = {
    'T': '5. 건물경사계 (한남동).xlsx',
    'C': '4. 균열측정계(한남동).xlsx',
    'SE': '6. 지표침하계(한남동).xlsx',
    'S': '3. 변형률계(1~7 3단샘플).xlsx',
    'W': '2. 지하수위계(한남동).xlsx',
    'I': '1. 지중경사계(한남동).xlsx'
}

counts = {}
for k, v in files.items():
    wb = openpyxl.load_workbook(f'excel/{v}', read_only=True, data_only=True)
    counts[k] = len(wb.sheetnames)
    print(f"{k}: {counts[k]}")
    wb.close()

print(counts)
