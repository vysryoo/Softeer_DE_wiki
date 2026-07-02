import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import re
import country_converter as coco 


def log(message):
    # ETL 프로세스의 각 단계를 etl_project_gdp.txt 파일에 기록
    timestamp_format = "%Y-%B-%d-%H-%M-%S"
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open("etl_project_log.txt", "a", encoding="utf-8") as f:
        f.write(f"{timestamp}, {message}\n")


def extract(url):
    log(f"Start Extraction: {url}")
    headers = {
        'User-Agent': 'ETLProjectGDP/1.0(https://github.com/vysryoo/etl-project-gdp)'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table', {'class': 'wikitable'})
    target_table = tables[0]  
    rows = target_table.find_all('tr')
    data = []

    # 첫 2줄은 헤더이므로 건너뛰고 데이터 추출
    for row in rows[2:]:
        cols = row.find_all(['td', 'th'])
        if len(cols) >= 2:
            country = cols[0].text
            gdp = cols[1].text 
            data.append({
                'Country': country,
                'GDP_USD_million': gdp
            })
    df = pd.DataFrame(data)
    log(f"End Extraction: {len(df)} records extracted")
    return df


def transform(df):
    log("Start Transformation")
    df['Country'] = df['Country'].str.replace(r'\[.*?\]', '', regex=True).str.strip()
    df['Region'] = coco.convert(names=df['Country'].tolist(), to='continent', not_found='Unknown')

    def clean_gdp(x):
            if pd.notnull(x):

                base_str = str(x).split('(')[0].split('[')[0]
                cleaned_str = re.sub(r'[^\d.]', '', base_str)
                if cleaned_str: 
                    return round(float(cleaned_str) / 1000, 2)

    df['GDP_USD_billion'] = df['GDP_USD_million'].apply(clean_gdp)
    df.drop(columns=['GDP_USD_million'], inplace=True)

    # 결측치는 제거
    df.dropna(subset=['GDP_USD_billion'], inplace=True)
    df = df.sort_values(by='GDP_USD_billion', ascending=False).reset_index(drop=True)
    log("End Transformation")
    return df


def load(df, filename):
    
    log(f"Start Loading: {filename}")
    df.to_json(filename, orient="records", force_ascii=False, indent=4)
    log(f"End Loading: {len(df)} records loaded into {filename}")


def display(df):
    log("Start Displaying Data")

    # GDP가 100B USD 이상인 국가들
    print("\n--- [GDP > 100B USD] ---")
    high_gdp = df[df['GDP_USD_billion'] >= 100]
    print(high_gdp[['Country', 'Region', 'GDP_USD_billion']])

    # 각 지역별 상위 5개 국가의 평균 GDP 계산
    print("\n--- [Region Top 5 Average GDP] ---")
    top5_avg = df.groupby('Region').head(5).groupby('Region')['GDP_USD_billion'].mean().round(2)
    print(top5_avg)
    log("End Displaying Data")
    
if __name__ == "__main__":

    url = "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_%28nominal%29"
    df = transform(extract(url))
    load(df, "Countries_by_GDP.json")
    display(df)
