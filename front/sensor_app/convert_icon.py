import base64

svg_data = '''<svg width="1024" height="1024" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2196F3;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#9C27B0;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="1024" height="1024" rx="180" fill="url(#grad1)"/>
  <rect x="200" y="600" width="120" height="250" rx="15" fill="white" opacity="0.9"/>
  <rect x="360" y="500" width="120" height="350" rx="15" fill="white" opacity="0.95"/>
  <rect x="520" y="400" width="120" height="450" rx="15" fill="white"/>
  <rect x="680" y="350" width="120" height="500" rx="15" fill="white" opacity="0.95"/>
  <path d="M 200 650 Q 360 550 520 450 T 800 350" stroke="white" stroke-width="12" fill="none" stroke-linecap="round" opacity="0.7"/>
  <circle cx="260" cy="650" r="20" fill="white"/>
  <circle cx="420" cy="550" r="20" fill="white"/>
  <circle cx="580" cy="450" r="20" fill="white"/>
  <circle cx="740" cy="350" r="20" fill="white"/>
  <text x="512" y="280" font-family="Arial, sans-serif" font-size="200" font-weight="bold" fill="white" text-anchor="middle">J</text>
</svg>'''

try:
    from PIL import Image
    from io import BytesIO
    import cairosvg
    
    png_data = cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), output_width=1024, output_height=1024)
    with open('C:/Projects/JReports4/front/sensor_app/assets/icon.png', 'wb') as f:
        f.write(png_data)
    print("✅ 아이콘 PNG 생성 완료")
except ImportError:
    print("❌ cairosvg 패키지가 필요합니다")
    print("pip install cairosvg pillow 실행 후 다시 시도하세요")
