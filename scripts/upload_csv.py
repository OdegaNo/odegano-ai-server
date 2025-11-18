import asyncio
import csv
import sys
from pathlib import Path
import chardet
import os
from dotenv import load_dotenv

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.model.place import Place

load_dotenv()

# MongoDB 설정
MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME")

def detect_encoding(file_path: str) -> str:
    """파일의 인코딩을 자동으로 감지"""
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding']

async def upload_csv_to_mongodb(csv_file_path: str, place_type: str):
    """
    CSV 파일을 읽어서 MongoDB에 업로드
    
    Args:
        csv_file_path: CSV 파일 경로
        place_type: 장소 유형 ('관광지' 또는 '유적지')
    """
    # MongoDB 연결
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Beanie 초기화
    await init_beanie(database=db, document_models=[Place])
    
    # 파일 인코딩 감지
    encoding = detect_encoding(csv_file_path)
    print(f"  📝 감지된 인코딩: {encoding}")
    
    # CSV 파일 읽기
    places_data = []
    
    try:
        with open(csv_file_path, 'r', encoding=encoding) as file:
            csv_reader = csv.DictReader(file)
            
            # 첫 줄에서 컬럼명 확인
            headers = csv_reader.fieldnames
            print(f"  📋 컬럼: {', '.join(headers[:5])}...")
            
            for idx, row in enumerate(csv_reader):
                try:
                    # CSV 컬럼명에 맞게 조정
                    # 관광지 CSV: 관광지명, 소재지도로명주소, 관광지소개 등
                    # 유적지 CSV: poi_nm, sido_nm, sgg_nm, bemd_nm, ri_nm, mcate_nm 등
                    
                    # 명칭 추출
                    name = row.get('관광지명', row.get('poi_nm', row.get('명칭', row.get('이름', '')))).strip()
                    
                    # 주소 조합 (유적지는 여러 컬럼을 합쳐야 함)
                    address = ''
                    if 'mcate_nm' in row:  # 유적지 CSV
                        # mcate_nm, sido_nm, sgg_nm, bemd_nm, ri_nm 등을 조합
                        parts = [
                            row.get('sido_nm', '').strip(),
                            row.get('sgg_nm', '').strip(),
                            row.get('bemd_nm', '').strip(),
                            row.get('ri_nm', '').strip(),
                            row.get('branch_nm', '').strip(),
                        ]
                        address = ' '.join([p for p in parts if p])
                    else:  # 관광지 CSV
                        address = row.get('소재지도로명주소', row.get('소재지지번주소', row.get('주소', row.get('소재지', '')))).strip()
                    
                    # 설명
                    description = row.get('관광지소개', row.get('설명', row.get('개요', ''))).strip()
                    
                    # 지역
                    region = row.get('시도', row.get('sido_nm', row.get('지역', ''))).strip()
                    
                    place_data = {
                        'name': name,
                        'type': place_type,
                        'address': address,
                        'description': description,
                        'region': region,
                    }
                    
                    # 위도, 경도가 있다면 추가
                    lat_key = next((k for k in row.keys() if '위도' in k or 'latitude' in k.lower()), None)
                    lon_key = next((k for k in row.keys() if '경도' in k or 'longitude' in k.lower()), None)
                    
                    if lat_key and row.get(lat_key):
                        try:
                            place_data['latitude'] = float(row[lat_key])
                        except (ValueError, TypeError):
                            pass
                            
                    if lon_key and row.get(lon_key):
                        try:
                            place_data['longitude'] = float(row[lon_key])
                        except (ValueError, TypeError):
                            pass
                    
                    if place_data['name']:  # 이름이 있는 경우만 추가
                        places_data.append(Place(**place_data))
                        
                except Exception as e:
                    print(f"  ⚠️  {idx+1}번째 행 처리 중 오류: {str(e)}")
                    continue
        
        # MongoDB에 일괄 삽입
        if places_data:
            await Place.insert_many(places_data)
            print(f"  ✅ {len(places_data)}개의 {place_type} 데이터를 업로드했습니다.")
        else:
            print(f"  ⚠️  업로드할 데이터가 없습니다.")
            
    except Exception as e:
        print(f"  ❌ 오류 발생: {str(e)}")
    finally:
        client.close()

async def main():
    """메인 함수"""
    print("🚀 CSV 파일을 MongoDB에 업로드합니다.\n")
    
    # data 폴더 경로
    data_dir = project_root / "data"
    
    # 업로드할 파일 목록
    files_to_upload = [
        {"path": data_dir / "tourist_spots.csv", "type": "관광지"},
        {"path": data_dir / "historic_sites.csv", "type": "유적지"},
    ]
    
    for file_info in files_to_upload:
        file_path = file_info["path"]
        place_type = file_info["type"]
        
        if file_path.exists():
            print(f"📁 {file_path.name} 파일을 업로드 중...")
            await upload_csv_to_mongodb(str(file_path), place_type)
        else:
            print(f"⚠️  {file_path.name} 파일을 찾을 수 없습니다.")
    
    print("\n✨ 모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    asyncio.run(main())
