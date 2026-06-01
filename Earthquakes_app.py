import streamlit as st
import pandas as pd
import joblib
import folium
from streamlit_folium import st_folium

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="세계 지진 위험도 예측", layout="wide")
st.title("🌍 세계 지진 데이터 기반 위험도 예측 시스템")
st.markdown("위도와 경도를 입력하면 해당 지역 주변의 지진 데이터를 분석하여 위험도를 예측합니다.")

# [추가] 세션 상태 초기화 - 분석 버튼 클릭 여부 및 결과 저장용
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
    st.session_state.result_risk = ""
    st.session_state.cluster_ratio = None
    st.session_state.near_df_empty = False

# 2. 정제된 데이터 및 모델 로드
@st.cache_data
def load_data():
    df = pd.read_csv("Earthquakes_ready.csv")
    return df

try:
    df_ready = load_data()
    model = joblib.load("Eartquakes_model.pkl")
    scaler = joblib.load("Eartquakes_scaler.pkl")
except FileNotFoundError as e:
    st.error(f"❌ 필수 파일이 누락되었습니다. 코랩 좌측 메뉴에서 다운로드 후 이 프로젝트 폴더에 넣어주세요: {e.filename}")
    st.stop()

# 3. 사이드바 - 사용자 입력 받기
st.sidebar.header("📍 분석할 위치 입력")
lat = st.sidebar.number_input("위도 입력 (-90.0 ~ 90.0)", min_value=-90.0, max_value=90.0, value=10.7, step=0.1)
lon = st.sidebar.number_input("경도 입력 (-180.0 ~ 180.0)", min_value=-180.0, max_value=180.0, value=106.7, step=0.1)

# 군집별 위험도 매핑
risk_dict = {0: '높음 🔴', 1: '낮음 🔵', 2: '중간 🟢'}

# 4. 메인 로직 처리
# 버튼을 누르는 순간 데이터 연산을 수행하고 그 결과를 세션 상태에 '저장'합니다.
if st.sidebar.button("위험도 분석 시작"):
    near_df = df_ready[
        (df_ready['위도'] >= lat - 5) & (df_ready['위도'] <= lat + 5) & 
        (df_ready['경도'] >= lon - 5) & (df_ready['경도'] <= lon + 5)
    ]
    
    if near_df.empty:
        st.session_state.near_df_empty = True
        st.session_state.analyzed = False
    else:
        cluster_ratio = near_df['cluster'].value_counts(normalize=True)
        main_cluster = cluster_ratio.idxmax()
        
        # 세션 상태에 결과 굳히기
        st.session_state.result_risk = risk_dict[main_cluster]
        st.session_state.cluster_ratio = cluster_ratio
        st.session_state.near_df_empty = False
        st.session_state.analyzed = True

# 5. 화면 렌더링 (지도를 만지거나 새로고침되어도 세션 상태에 값이 있으면 상시 유지)
if st.session_state.near_df_empty:
    st.warning("⚠️ 입력하신 좌표 주변 ±5도 이내에 최근 지진 기록이 없어 위험도를 측정할 수 없습니다.")

elif st.session_state.analyzed:
    # 레이아웃 분할 (좌측 결과창, 우측 지도창)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric(label="📊 예측된 위험도", value=st.session_state.result_risk)
        st.subheader("📌 주변 지진 군집 비율")
        for cluster_idx, ratio in st.session_state.cluster_ratio.items():
            st.write(f"- **{risk_dict[int(cluster_idx)]} 그룹**: {ratio*100:.1f}%")
            
    with col2:
        st.subheader("🗺️ 지진 분포 및 입력 위치 지도")
        
        # Folium 지도 생성 (사용자 입력 좌표 중심)
        m = folium.Map(location=[lat, lon], zoom_start=4)
        
        # 지도 시각화 성능 최적화를 위한 샘플링 (최대 2000개 표시)
        sample_size = min(2000, len(df_ready))
        df_sample = df_ready.sample(sample_size, random_state=42)
        colors = {0: 'red', 1: 'blue', 2: 'green'}
        
        # 주변 및 기존 지진 데이터 시각화
        for _, row in df_sample.iterrows():
            try:
                cluster = int(row['cluster'])
                folium.CircleMarker(
                    location=[row['위도'], row['경도']],
                    radius=2,
                    color=colors.get(cluster, 'gray'),
                    fill=True,
                    fill_color=colors.get(cluster, 'gray'),
                    fill_opacity=0.6
                ).add_to(m)
            except:
                continue
        
        # 사용자가 입력한 위치 검은색 별표 마커로 강조 표시
        folium.Marker(
            location=[lat, lon],
            icon=folium.Icon(color='black', icon='star'),
            popup="입력 위치"
        ).add_to(m)
        
        # Streamlit 웹 대시보드 화면에 지도 렌더링
        st_folium(m, width=700, height=450)
else:
    st.info("👈 왼쪽 사이드바에서 위도와 경도를 입력한 후 '위험도 분석 시작' 버튼을 눌러주세요.")