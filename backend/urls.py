from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from reports import views  # reports 앱의 views 가져오기

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    
    # --- 웹 페이지 ---
    path('web/', views.web_form, name='web_form'),  # 웹 폼
    path('create/', views.sensor_form, name='sensor_form'),  # 계측기 입력 폼
    
    # --- J Reports API ---
    path('api/generate-excel/', views.generate_excel, name='generate_excel'),  # 엑셀 생성
    path('api/analyze/plan/', views.analyze_plan, name='analyze_plan'),       # 도면 분석
    path('api/create/sensors/', views.create_project_sensors, name='create_sensors'), # 센서 생성
    path('api/upload/data/', views.upload_measurement, name='upload_data'),   # CSV 업로드
]

# 미디어 파일(도면, PDF) 접근용 설정
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)