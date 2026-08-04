import pandas as pd

df = pd.read_csv('서울특별시 공공자전거 대여이력 정보_2606.csv', encoding='cp949')

# 1. 모든 컬럼(열)이 짤리지 않고 나오도록 설정
pd.set_option('display.max_columns', None)

# 2. 모든 행(줄)이 짤리지 않고 나오도록 설정 (데이터가 너무 많으면 주의!)
pd.set_option('display.max_rows', None)

# 3. 출력 너비를 제한 없이 넓게 설정 (자동 줄바꿈 방지)
pd.set_option('display.width', 1000)

# 4. 컬럼 안의 문자열 내용이 길어도 짤리지 않게 설정
pd.set_option('display.max_colwidth', None)

print(df.head())
print(df.columns)