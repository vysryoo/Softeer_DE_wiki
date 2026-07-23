"""
W4M2_final.ipynb 실행에 필요한 원본 데이터를 내려받는다.

받는 것
  data/yellow_2024-03.parquet   TLC Yellow Taxi 2024-03 트립
  data/taxi_zone_lookup.csv     TLC 존 룩업
  zones/taxi_zones.shp (+.dbf/.shx/.prj)  TLC 존 shapefile
  warehouse/nyc311/year=2024/month=3/*.parquet  NYC 311 SR (2024-03, 전체 agency)

사용
  cd missions/W4 && source venv/bin/activate
  python scripts/fetch_data.py
"""
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parent.parent  # missions/W4
DATA_DIR = ROOT / "data"
ZONES_DIR = ROOT / "zones"
WAREHOUSE_DIR = ROOT / "warehouse" / "nyc311" / "year=2024" / "month=3"

TLC_BASE = "https://d37ci6vzurychx.cloudfront.net"
SODA_URL = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"
SODA_PAGE_SIZE = 50000

SODA_COLUMNS = [
    "unique_key", "created_date", "agency", "complaint_type", "descriptor",
    "status", "resolution_description", "borough",
    "bridge_highway_name", "latitude", "longitude",
]


def download(url: str, dest: Path, chunk: int = 1 << 20) -> None:
    if dest.exists() and dest.stat().st_size > 0:
        print(f"[skip] {dest} 이미 존재")
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"[get] {url}")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        tmp = dest.with_suffix(dest.suffix + ".part")
        with open(tmp, "wb") as f:
            for part in r.iter_content(chunk):
                f.write(part)
        tmp.rename(dest)
    print(f"[ok] {dest} ({dest.stat().st_size / 1e6:.1f} MB)")


def fetch_yellow_trip() -> None:
    download(f"{TLC_BASE}/trip-data/yellow_tripdata_2024-03.parquet",
              DATA_DIR / "yellow_2024-03.parquet")


def fetch_zone_lookup() -> None:
    download(f"{TLC_BASE}/misc/taxi_zone_lookup.csv",
              DATA_DIR / "taxi_zone_lookup.csv")


def fetch_taxi_zones_shp() -> None:
    if (ZONES_DIR / "taxi_zones.shp").exists():
        print(f"[skip] {ZONES_DIR / 'taxi_zones.shp'} 이미 존재")
        return
    zip_path = ZONES_DIR / "taxi_zones.zip"
    download(f"{TLC_BASE}/misc/taxi_zones.zip", zip_path)
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(ZONES_DIR)
    # zip이 taxi_zones/ 하위 폴더를 포함하는 경우 SHAPE_PATH 기준 위치로 평탄화
    nested = ZONES_DIR / "taxi_zones"
    if nested.is_dir():
        for f in nested.iterdir():
            f.rename(ZONES_DIR / f.name)
        nested.rmdir()
    print(f"[ok] {ZONES_DIR} 압축 해제 완료")


def fetch_311_march_2024() -> None:
    out_dir = WAREHOUSE_DIR
    if any(out_dir.glob("*.parquet")) if out_dir.exists() else False:
        print(f"[skip] {out_dir} 이미 존재")
        return

    select = ",".join(SODA_COLUMNS)
    where = "created_date >= '2024-03-01T00:00:00' AND created_date < '2024-04-01T00:00:00'"

    frames = []
    offset = 0
    while True:
        params = {
            "$select": select,
            "$where": where,
            "$order": "unique_key",
            "$limit": SODA_PAGE_SIZE,
            "$offset": offset,
        }
        print(f"[soda] offset={offset}")
        resp = requests.get(SODA_URL, params=params, timeout=120)
        resp.raise_for_status()
        rows = resp.json()
        if not rows:
            break
        frames.append(pd.DataFrame(rows))
        offset += len(rows)
        if len(rows) < SODA_PAGE_SIZE:
            break
        time.sleep(0.2)  # 무토큰 요청 과속 방지

    if not frames:
        print("[warn] 311 데이터가 비어 있음", file=sys.stderr)
        return

    df = pd.concat(frames, ignore_index=True)
    for col in SODA_COLUMNS:
        if col not in df.columns:
            df[col] = None
    df = df[SODA_COLUMNS]
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "part-000.parquet"
    df.to_parquet(out_path, index=False)
    print(f"[ok] {out_path} ({len(df):,} 행)")


if __name__ == "__main__":
    fetch_yellow_trip()
    fetch_zone_lookup()
    fetch_taxi_zones_shp()
    fetch_311_march_2024()
    print("모든 데이터 준비 완료.")
