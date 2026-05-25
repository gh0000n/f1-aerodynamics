import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. 레이아웃 설정
st.set_page_config(layout="wide")
st.title("🏎️ F1 에어로다이나믹스 가상 풍동 최적화 대시보드")
st.write("최종 완성: 거울 영상법 기반 지면 효과 및 DRS 텔레메트리 분석")

# 2. 사이드바 제어 패널
st.sidebar.header("🕹️ 실시간 튜닝 패널")
v_infinity_kmh = st.sidebar.slider("F1 차량 속도 (km/h)", 100, 360, 250, step=10)
v_infinity = v_infinity_kmh / 3.6 

wing_y = st.sidebar.slider("지상고 (Ride Height h, mm)", 50, 500, 150, step=10) / 1000 # mm -> m 변환 정확히 수정
alpha = st.sidebar.slider("윙 받음각 (Angle of Attack, deg)", 0, 25, 12, step=1)

st.sidebar.markdown("---")
drs_on = st.sidebar.toggle("🚀 DRS (Drag Reduction System) 활성화", value=False)

# DRS 작동 데이터 연산
effective_alpha = alpha * 0.3 if drs_on else alpha
base_gamma = -4 * np.pi * v_infinity * np.sin(np.radians(effective_alpha))

# 3. 2D 공간 수치해석 격자 생성
x = np.linspace(-4, 4, 100)
y = np.linspace(0.01, 3, 100)
X, Y = np.meshgrid(x, y)

# 4. 포텐셜 유동 및 거울 영상법 연산
Psi_uniform = v_infinity * Y
r_real_sq = X**2 + (Y - wing_y)**2
Psi_vortex_real = (base_gamma / (2 * np.pi)) * np.log(np.sqrt(r_real_sq) + 1e-5)

r_image_sq = X**2 + (Y + wing_y)**2
Psi_vortex_image = (-base_gamma / (2 * np.pi)) * np.log(np.sqrt(r_image_sq) + 1e-5)

Psi_total = Psi_uniform + Psi_vortex_real + Psi_vortex_image

# 5. 공학적 데이터 산출
rho = 1.225 
chord = 0.4 

ground_effect_multiplier = 1.0 + (chord / (4 * max(0.01, wing_y)))**2
C_L = 2 * np.pi * np.sin(np.radians(effective_alpha)) * ground_effect_multiplier
C_D = (C_L**2) / (np.pi * 1.5) + (0.01 if drs_on else 0.05)

downforce = 0.5 * rho * (v_infinity**2) * chord * C_L
drag = 0.5 * rho * (v_infinity**2) * chord * C_D

# 6. 화면 분할 배치 (버그 방지를 위해 안정적인 피규어 생성 구조 적용)
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📊 2D 가상 풍동 유선(Streamline) 분석")
    
    # 확실하게 새로운 Figure 객체를 명시적으로 생성하여 충돌 방지
    fig1 = plt.figure(figsize=(8, 5))
    ax1 = fig1.add_subplot(111)
    
    # 유선 출력
    ax1.contour(X, Y, Psi_total, levels=40, colors='blue', linewidths=1)
    
    # 윙 프로파일 및 지면선
    wing_x = np.linspace(-0.2, 0.2, 10)
    wing_y_pos = wing_y + wing_x * np.sin(np.radians(effective_alpha))
    ax1.plot(wing_x, wing_y_pos, color='red', linewidth=6, label='F1 Wing')
    ax1.axhline(0, color='black', linewidth=6, label='Track')
    
    ax1.set_xlim(-3, 3)
    ax1.set_ylim(0, 3)
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='upper right')
    
    st.pyplot(fig1, clear_figure=True)

with col2:
    st.subheader("🏎️ 실시간 텔레메트리")
    
    st.metric(label="💥 다운포스 (Downforce)", value=f"{abs(downforce):.1f} N")
    st.metric(label="🛑 공기 저항력 (Drag)", value=f"{drag:.1f} N")
    st.metric(label="📈 에어로 효율성 (L/D)", value=f"{abs(downforce)/max(1e-3, drag):.2f}")

    st.markdown("##### 지상고별 다운포스 변화")
    
    # 맷플롯립 중복 버그 방지를 위해 Streamlit 내장 라인 차트로 대체 (완전 안전함)
    h_arr = np.linspace(0.05, 0.5, 50)
    mult_arr = 1.0 + (chord / (4 * h_arr))**2
    df_arr = 0.5 * rho * (v_infinity**2) * chord * (2 * np.pi * np.sin(np.radians(effective_alpha))) * mult_arr
    
    st.line_chart(df_arr)

# 7. 엔지니어링 리포트
st.markdown("---")
st.subheader("📝 엔지니어링 분석 리포트")
if drs_on:
    st.warning("⚠️ DRS 활성화: 리어 윙 주익 개방으로 항력이 최대로 감소했습니다. 직선 주로 최고 속도 도달 모드입니다.")
else:
    if wing_y <= 0.15:
        st.success("✅ 지면 효과(Ground Effect) 구간:cd Desktop 지면 밀착으로 인해 하부 유속이 빨라지며 비선형적 다운포스가 폭발적으로 증가합니다.")
    else:
        st.info("ℹ️ 일반 주행 모드: 고속/중속 코너링의 밸런스 에어로 세팅 상태입니다.")