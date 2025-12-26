import math

class SensorNameGenerator:
    """
    J님 현장의 '엑셀 파일명 및 시트명 생성 공식'을 관리하는 클래스
    """

    @staticmethod
    def generate_names(sensor_code, total_count):
        names = []

        # -------------------------------------------------------
        # 1. 변형률계 (S) 규칙
        # "S1-1,3" -> S(변형률) + 1(위치) + 1,3(단)
        # "수직층수(단)는 최대 3단"
        # -------------------------------------------------------
        if sensor_code == 'S':
            # 가정: 3단씩 꽉 채워서 설치된다고 보고 위치를 계산
            # 예: 12개라면 -> 4개 위치 x 3단
            # 만약 3으로 안 나누어떨어지면? -> 마지막 위치는 1~2단만 설치
            
            location_count = math.ceil(total_count / 3) # 위치 개수 계산
            remaining = total_count
            
            for loc in range(1, location_count + 1):
                # 이 위치에 몇 단까지 있는지 계산 (기본 3, 남은게 적으면 그만큼)
                layers_in_this_loc = min(remaining, 3)
                
                # 이름 생성 (예: S1-1, S1-2, S1-3)
                for layer in range(1, layers_in_this_loc + 1):
                    name = f"S{loc}-{layer}" # S위치-단
                    names.append(name)
                
                remaining -= layers_in_this_loc

        # -------------------------------------------------------
        # 2. 지표침하계 (SE) 규칙
        # "3set(9Points)" -> 총 9개지만, 3개씩 묶어서 관리
        # 엑셀 시트에는 P.1, P.2... P.9로 표시
        # -------------------------------------------------------
        elif sensor_code == 'SE':
            # 9개 입력 시 -> P.1 ~ P.9 생성
            for i in range(1, total_count + 1):
                names.append(f"SE Point-{i} (P.{i})")

        # -------------------------------------------------------
        # 3. 유량계 (FM) 규칙
        # -------------------------------------------------------
        elif sensor_code == 'FM' or sensor_code == 'Flow':
            for i in range(1, total_count + 1):
                names.append(f"FM-{i}")

        # -------------------------------------------------------
        # 4. 기타 센서 (T, C, W 등) - 기본 순번
        # -------------------------------------------------------
        else:
            code_map = {'Tilt': 'T', 'Crack': 'C', 'W': 'W', 'I': 'I'}
            prefix = code_map.get(sensor_code, sensor_code)
            
            for i in range(1, total_count + 1):
                names.append(f"{prefix}-{i}")

        return names

# --- 테스트 실행 (J님이 알려준 예시) ---
if __name__ == "__main__":
    # 1. 변형률계 12개일 때 (4개소 x 3단 예상)
    print("--- [S] 변형률계 12개 ---")
    print(SensorNameGenerator.generate_names('S', 12))
    
    # 2. 지표침하계 9개일 때
    print("\n--- [SE] 지표침하계 9개 (Points) ---")
    print(SensorNameGenerator.generate_names('SE', 9))