# 학습 분석 컴포넌트: 문제 해결 성과 및 정답률 중심 분석

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def render_analytics():
    """학습 분석 대시보드 렌더링"""
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;'>
        <h2 style='margin: 0;'>📊 학습 성과 분석</h2>
        <p style='margin: 0.5rem 0 0 0;'>문제 해결 능력과 학습 패턴을 확인하세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 메트릭 카드 렌더링
    render_metric_cards()
    
    st.divider()
    
    # 차트 섹션
    col1, col2 = st.columns(2)
    
    with col1:
        render_hint_distribution_chart()
    
    with col2:
        # 시간 차트 대신 주간 문제 해결 차트로 변경
        render_weekly_progress_chart()
    
    st.divider()
    
    # 상세 분석 (강점/약점만 남김)
    render_detailed_analysis()

def render_metric_cards():
    """주요 메트릭 카드 표시 (시간 -> 정답률 변경)"""
    
    analytics = st.session_state.analytics_data
    total_problems = st.session_state.get('total_problems', 0)
    solved_problems = st.session_state.get('solved_problems', 0)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class='stat-card'>
            <h3 style='color: #667eea;'>문제 해결</h3>
            <h1>{}/{}</h1>
            <p style='color: #718096;'>해결/시도</p>
        </div>
        """.format(solved_problems, total_problems), unsafe_allow_html=True)
    
    with col2:
        total_hints = analytics.get('total_hints', 0)
        st.markdown("""
        <div class='stat-card'>
            <h3 style='color: #48bb78;'>힌트 사용</h3>
            <h1>{}</h1>
            <p style='color: #718096;'>총 사용 횟수</p>
        </div>
        """.format(total_hints), unsafe_allow_html=True)
    
    with col3:
        # 학습 시간 대신 정답률(해결률) 표시
        solve_rate = 0
        if total_problems > 0:
            solve_rate = round((solved_problems / total_problems) * 100, 1)
            
        st.markdown("""
        <div class='stat-card'>
            <h3 style='color: #f6ad55;'>정답률</h3>
            <h1>{}%</h1>
            <p style='color: #718096;'>문제 해결 비율</p>
        </div>
        """.format(solve_rate), unsafe_allow_html=True)
    
    with col4:
        distribution = analytics.get('hint_distribution', [0, 0, 0])
        if sum(distribution) > 0:
            avg_level = sum((i+1) * v for i, v in enumerate(distribution)) / sum(distribution)
            avg_level = round(avg_level, 1)
        else:
            avg_level = 0
        
        st.markdown("""
        <div class='stat-card'>
            <h3 style='color: #fc8181;'>평균 난이도</h3>
            <h1>{}</h1>
            <p style='color: #718096;'>힌트 레벨</p>
        </div>
        """.format(avg_level), unsafe_allow_html=True)

def render_hint_distribution_chart():
    """힌트 분포 차트"""
    st.subheader("📊 힌트 사용 분포")
    
    distribution = st.session_state.analytics_data.get('hint_distribution', [0, 0, 0])
    
    if sum(distribution) > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['1단계 힌트', '2단계 힌트', '3단계 힌트'],
            values=distribution,
            hole=.3,
            marker=dict(colors=['#48bb78', '#f6ad55', '#fc8181'])
        )])
        
        fig.update_layout(
            height=300,
            showlegend=True,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        max_idx = distribution.index(max(distribution))
        hint_names = ['기초 접근', '핵심 개념', '구체적 안내']
        st.info(f"💡 주로 **{hint_names[max_idx]}** 힌트를 사용하고 있어요!")
    else:
        st.info("아직 힌트를 사용하지 않았어요.")

def render_weekly_progress_chart():
    """주간 문제 해결 진도 차트"""
    st.subheader("📈 주간 학습 성과")
    
    # 날짜 생성
    dates = pd.date_range(end=datetime.now(), periods=7).tolist()
    
    current_solved = st.session_state.get('solved_problems', 0)
    solved_counts = [0, 0, 0, 0, 0, 0, current_solved]
    
    df = pd.DataFrame({
        '날짜': [d.strftime('%m/%d') for d in dates],
        '해결한 문제': solved_counts
    })
    
    fig = px.bar(
        df, 
        x='날짜', 
        y='해결한 문제',
        text='해결한 문제',
        color='해결한 문제',
        color_continuous_scale='Bluered'
    )
    
    fig.update_layout(
        height=300,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        yaxis=dict(title='문제 수')
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    weekly_total = sum(solved_counts)
    st.success(f"🔥 이번 주 총 **{weekly_total}문제**를 해결했어요!")

def render_detailed_analysis():
    """상세 분석 섹션 (강점/약점 분석만)"""
    st.subheader("🔍 상세 학습 분석")
    render_strengths_weaknesses()

def render_strengths_weaknesses():
    """강점과 약점 분석"""

    # 푼 문제가 적을 경우 안내 메시지 표시
    solved_count = st.session_state.get('solved_problems', 0)
    
    if solved_count < 3:  # 문제가 3개 미만일 때
        st.info("📊 문제를 3개 이상 풀면 AI가 강점과 약점을 분석해드려요!")
    
    # 스킬 레벨 차트 (현재는 기본 값)
    categories = ['대수', '기하', '함수', '확률', '통계']
    values = [20, 20, 20, 20, 20]  # 기본 값
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        marker=dict(color='#667eea')
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=300,
        margin=dict(t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
