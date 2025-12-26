import json
import os
import time
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render
from django.core.files.storage import default_storage
from .models import Project, Sensor
from .pdf_parser import extract_project_info
from .excel_builder import create_excel_files
from .utils import parse_and_save_data
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from excel_template_cloner import create_all_sensor_files

@csrf_exempt
def analyze_plan(request):
    """
    [POST] plan.pdf 업로드 -> 프로젝트 정보 추출 -> 수동 입력 대기
    """
    if request.method == 'POST' and request.FILES.get('plan_file'):
        plan_file = request.FILES['plan_file']
        
        # 1. PDF 파일 임시 저장
        file_path = default_storage.save(f'temp/{plan_file.name}', plan_file)
        full_path = default_storage.path(file_path)
        
        # 2. PDF에서 프로젝트 정보 추출 (예: 한남동_383-1)
        project_info = extract_project_info(full_path)
        
        # 3. 프로젝트 생성 또는 조회
        project, created = Project.objects.get_or_create(
            name=project_info,
            defaults={'location': project_info}
        )
        
        # 4. plan 파일 저장
        if created or not project.plan_file:
            project.plan_file.save(plan_file.name, plan_file, save=True)
        
        return JsonResponse({
            'status': 'success',
            'project_id': project.id,
            'project_name': project_info,
            'message': '프로젝트 정보 추출 완료. 센서 수량을 입력해주세요.'
        })
    
    return JsonResponse({'status': 'error', 'message': 'plan.pdf 파일이 필요합니다.'}, status=400)

@csrf_exempt
def create_project_sensors(request):
    """
    [POST] 센서 수량 입력 -> DB 생성 + 엑셀 파일 생성
    Body: { "project_id": 1, "counts": {"T": 6, "C": 18, "I": 3, "S": 12, "SE": 9, "W": 2} }
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        project_id = data.get('project_id')
        counts = data.get('counts', {})
        
        project = get_object_or_404(Project, pk=project_id)
        
        created_sensors = []
        
        # 1. 센서 DB 생성 (T-1, T-2...)
        for sensor_type, count in counts.items():
            if int(count) == 0:
                continue
            for i in range(1, int(count) + 1):
                code = f"{sensor_type}-{i}"
                sensor, _ = Sensor.objects.get_or_create(
                    project=project,
                    sensor_type=sensor_type,
                    code=code
                )
                created_sensors.append(code)
        
        # 2. 폴더명 생성 (한남동383-1 형식 - 언더바 제거)
        folder_name = project.name.replace('_', '')
        output_dir = os.path.join('media', 'excels', folder_name)
        
        # 3. 엑셀 파일 생성
        created_files = create_excel_files(counts, folder_name, output_dir)
        
        return JsonResponse({
            'status': 'success',
            'created_sensors': created_sensors,
            'excel_files': created_files,
            'output_folder': folder_name
        })

    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def upload_measurement(request):
    """
    [POST] 계측 CSV 데이터 업로드 -> 파싱 및 저장
    Form-Data: file=csv파일, sensor_code='T-1', project_id=1
    """
    if request.method == 'POST':
        file = request.FILES.get('file')
        sensor_code = request.POST.get('sensor_code')
        project_id = request.POST.get('project_id')
        
        sensor = Sensor.objects.filter(project_id=project_id, code=sensor_code).first()
        if not sensor:
            return JsonResponse({'status': 'error', 'message': '센서를 찾을 수 없음'}, status=404)
            
        # CSV 파서 가동
        success = parse_and_save_data(file, sensor)
        
        if success:
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': '파싱 실패'}, status=500)
            
    return JsonResponse({'status': 'error'}, status=400)


# reports/views.py 맨 아래에 추가

def index(request):
    return JsonResponse({
        "status": "running", 
        "system": "J Reports Backend Engine", 
        "version": "1.0 (Vision + Overlay)"
    })

def sensor_form(request):
    """계측기 입력 폼 페이지"""
    return render(request, 'create_sensors.html')

@csrf_exempt
def generate_excel(request):
    """엑셀 파일 생성 API"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            site_name = data.get('site_name')
            site_address = data.get('site_address')
            company = data.get('company')
            counts = data.get('counts', {})
            
            if not site_address:
                return JsonResponse({'status': 'error', 'message': '현장 주소가 필요합니다.'}, status=400)
            
            # 0인 항목 제거
            counts = {k: v for k, v in counts.items() if v > 0}
            
            if not counts:
                return JsonResponse({'status': 'error', 'message': '최소 1개 이상의 계측기가 필요합니다.'}, status=400)
            
            # 시간 측정 시작
            start_time = time.time()
            
            # 엑셀 파일 생성 (폴더명은 site_address 사용)
            result = create_all_sensor_files(counts, site_address, site_name, company)
            
            elapsed_time = round(time.time() - start_time, 2)
            
            if result:
                # 파일들을 base64로 인코딩
                files_data = []
                for sensor_type, file_path in result.items():
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                            encoded = base64.b64encode(file_content).decode('utf-8')
                            files_data.append({
                                'type': sensor_type,
                                'filename': os.path.basename(file_path),
                                'data': encoded
                            })
                
                return JsonResponse({
                    'status': 'success',
                    'site_name': site_name or site_address,
                    'folder': f'generated_excels/{site_address}',
                    'files': files_data,
                    'counts': counts,
                    'elapsed_time': elapsed_time
                })
            else:
                return JsonResponse({'status': 'error', 'message': '파일 생성 실패'}, status=500)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'POST 요청만 가능합니다.'}, status=400)