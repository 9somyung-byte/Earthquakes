import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium
import os

# --- 1. 구글 드라이브 대용량 파일 다운로드 설정 ---
# ⚠️ 중요: 아래 '본인의_구글_드라이브_파일_ID' 부분을 실제 파일 ID로 꼭 변경해 주세요!
FILE_ID = 'Earthquakes_ready.csv' 
DATA_URL = f'https://drive.google.com/file/d/1YDgCyJRuMpGbYHFXWU90DqwgjpYWjvT2/view?usp=drive_link'

# --- 2. 데이터 로딩 함수 (캐싱 적용으로 속도 향상) ---
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

# --- 3. 데이터 및 모델 불러오기 ---
try:
    # 구글 드라이브에서 데이터 불러오기
    df = load_data(DATA_URL)
    
    # 모델 파일 로딩 (모델 파일도 용량이 크다면 같은 방식으로 구글 드라이브 연동이 필요할 수 있습니다)
    # 현재는 로컬 프로젝트 폴더에 있다고 가정합니다.
    # model = joblib.load('지진모델파일명.pkt') 
    
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다. 구글 드라이브 링크나 파일 ID를 확인해주세요. 에러 내용: {e}")
    st.stop()

# --- 4. 스트림릿 UI 및 지도 시각화 부분 ---
st.title("🌍 세계 지진 데이터 기반 위험도 예측 시스템")
st.write("위도와 경도를 입력하면 해당 지역 주변의 지진 데이터를 분석하여 위험도를 예측합니다.")

# 예시용 입력창 및 지도 표시 (기존에 작성하신 UI 코드에 맞게 커스텀하세요)
lat = st.number_input("위도(Latitude) 입력:", value=37.5665)
lon = st.number_input("경도(Longitude) 입력:", value=126.9780)

if st.button("위험도 예측하기"):
    st.success(f"입력하신 좌표 ({lat}, {lon}) 주변의 지진 위험도를 분석합니다...")
    
    # 지도 생성 및 표시
    m = folium.Map(location=[lat, lon], zoom_start=5)
    folium.Marker([lat, lon], popup="예측 지점", icon=folium.Icon(color='red')).add_to(m)
    st_folium(m, width=700, height=500)
