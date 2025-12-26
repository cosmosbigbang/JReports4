from django.db import models
import os

# 1. 프로젝트 (현장) - C-003 정보 + 배경 양식
class Project(models.Model):
    name = models.CharField(max_length=200, help_text="공사명")  # 예: 용산구 한남동 383...
    location = models.CharField(max_length=300, blank=True, help_text="현장위치")
    contractor = models.CharField(max_length=100, blank=True, help_text="시공사")
    
    # [핵심] 현장마다 다른 '빈 보고서 양식'을 여기에 등록 (확장성 확보)
    report_background = models.FileField(upload_to='templates/', null=True, help_text="빈 PDF 양식 파일")
    
    # 도면 파일 (C-018)
    plan_file = models.FileField(upload_to='plans/', null=True, help_text="계측계획평면도")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. 센서 (마스터 데이터) - Vision으로 C-018에서 추출한 것들
class Sensor(models.Model):
    TYPE_CHOICES = [
        ('T', '건물경사계'),
        ('CK', '균열측정기'),
        ('I', '지중경사계'),
        ('S', '변형률계'),
        ('W', '지하수위계'),
    ]
    
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sensors')
    sensor_type = models.CharField(max_length=5, choices=TYPE_CHOICES)
    code = models.CharField(max_length=20) # 예: T-1, CK-18
    
    # 초기치 (기준값)
    initial_value = models.FloatField(null=True, blank=True, help_text="초기 측정값")
    initial_date = models.DateField(null=True, blank=True)

    # 관리 기준치 (Safety Level)
    limit_warning = models.FloatField(default=0.0, help_text="1차 관리치(주의)")
    limit_danger = models.FloatField(default=0.0, help_text="2차 관리치(위험)")
    
    # PDF 상의 좌표 (ReportLab으로 찍을 때 사용)
    pdf_x = models.FloatField(default=0.0, help_text="PDF 오버레이용 X좌표")
    pdf_y = models.FloatField(default=0.0, help_text="PDF 오버레이용 Y좌표")

    def __str__(self):
        return f"[{self.project.name}] {self.code}"

# 3. 측정 데이터 (로그) - CSV에서 파싱된 데이터
class Measurement(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='measurements')
    measure_date = models.DateField()
    
    # 일반 센서용 (T, CK, S) - 스칼라 값
    value = models.FloatField(null=True, blank=True, help_text="금회 측정값")
    displacement = models.FloatField(null=True, blank=True, help_text="변위량(Current-Initial)")
    
    # 지중경사계용 (I) - 심도별 데이터를 JSON으로 통째로 저장
    # 예: {"0.5": 0.01, "1.0": 0.05, ...}
    raw_json = models.JSONField(null=True, blank=True, help_text="지중경사계 심도별 데이터")

    class Meta:
        unique_together = ('sensor', 'measure_date') # 중복 방지