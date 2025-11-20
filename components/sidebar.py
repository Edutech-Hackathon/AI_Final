# Sidebar 컴포넌트: 선생님 페르소나 선택, 학습 진도, 설정 등을 관리

import streamlit as st
from datetime import datetime, timedelta

def render_sidebar():
    """사이드바 렌더링"""
    
    with st.sidebar:
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2>🎓 AI 수학 과외</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # 학생 정보
        render_student_info()
        
        st.divider()
        
        # 선생님 선택
        render_teacher_selection()
        
        st.divider()
        
        # 학습 진도
        render_progress()
        
        st.divider()
        
        # 빠른 통계
        render_quick_stats()
        
        st.divider()
        
        # 설정
        render_settings()

def render_student_info():
    """학생 정보 표시"""
    st.subheader("👦 학생 정보")
    
    # 학생 이름 입력
    user_name = st.text_input(
        "이름",
        value=st.session_state.get('user_name', '학생'),
        key='user_name_input',
        help="선생님이 부를 이름을 입력하세요"
    )
    st.session_state.user_name = user_name
    
    # 학년 선택
    grade = st.selectbox(
        "학년",
        options=["초등학교", "중학교 1학년", "중학교 2학년", "중학교 3학년", 
                "고등학교 1학년", "고등학교 2학년", "고등학교 3학년"],
        index=3,  # 기본값: 중3
        key='grade_select'
    )
    st.session_state.grade = grade

def render_teacher_selection():
    """선생님 페르소나 선택"""
    st.subheader("👨‍🏫 선생님 선택")
    
    # 페르소나 옵션
    personas = {
        '친근한 선생님 😊': 'friendly',
        '엄격한 선생님 🧐': 'strict',
        '중립적 선생님 🤖': 'neutral'
    }
    
    # 라디오 버튼으로 선택
    selected = st.radio(
        "선생님 스타일",
        options=list(personas.keys()),
        index=0,
        key='persona_radio',
        help="원하는 선생님 스타일을 선택하세요"
    )
    
    st.session_state.selected_persona = personas[selected]
    
    # 선생님 설명
    descriptions = {
        'friendly': "따뜻하게 격려하며 자신감을 심어주는 선생님입니다. 실수해도 괜찮다고 다독여주고, 긍정적인 피드백을 많이 제공합니다.",
        'strict': "체계적이고 정확한 학습을 추구하는 선생님입니다. 개념을 정확히 이해했는지 확인하고, 논리적 사고를 강조합니다.",
        'neutral': "객관적이고 차분하게 가르치는 선생님입니다. 감정을 배제하고 사실과 논리에 기반한 설명을 제공합니다."
    }
    
    st.info(descriptions[st.session_state.selected_persona])

def render_progress():
    """학습 진도 표시 (문제 수 중심)"""
    st.subheader("📈 나의 성장")
    
    total = st.session_state.get('total_problems', 0)
    solved = st.session_state.get('solved_problems', 0)
    
    # 단순화된 진도 표시
    if total > 0:
        progress = min(solved / total, 1.0)
        st.progress(progress)
        st.caption(f"도전 과제: {solved}개 해결 / {total}개 시도")
    else:
        st.progress(0)
        st.caption("오늘의 첫 문제를 풀어보세요!")
    
    # 메트릭도 단순화
    st.metric(
        label="해결한 문제",
        value=f"{solved}개",
        delta="Keep going!" if solved > 0 else None
    )

def render_quick_stats():
    """빠른 통계 표시"""
    st.subheader("📊 빠른 통계")
    
    analytics = st.session_state.analytics_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            label="총 힌트 사용",
            value=analytics.get('total_hints', 0),
            help="지금까지 사용한 힌트 횟수"
        )
    
    with col2:
        # 가장 많이 사용한 힌트 레벨
        distribution = analytics.get('hint_distribution', [0, 0, 0])
        if sum(distribution) > 0:
            max_level = distribution.index(max(distribution)) + 1
            st.metric(
                label="주로 사용 힌트",
                value=f"{max_level}단계",
                help="가장 많이 사용한 힌트 레벨"
            )
        else:
            st.metric(
                label="주로 사용 힌트",
                value="없음"
            )
    
    # 힌트 분포 차트
    if sum(distribution) > 0:
        st.caption("힌트 사용 분포")
        chart_data = {
            '1단계': distribution[0],
            '2단계': distribution[1],
            '3단계': distribution[2]
        }
        st.bar_chart(chart_data)

def render_settings():
    """설정 옵션"""
    st.subheader("⚙️ 설정")
    
    # 다크 모드 토글
    dark_mode = st.checkbox(
        "다크 모드",
        value=False,
        key='dark_mode_toggle',
        help="화면을 어둡게 변경합니다"
    )
    
    # 알림 설정
    notifications = st.checkbox(
        "학습 알림",
        value=True,
        key='notifications_toggle',
        help="학습 목표 달성시 알림을 받습니다"
    )
    
    # 자동 저장
    auto_save = st.checkbox(
        "대화 자동 저장",
        value=True,
        key='auto_save_toggle',
        help="대화 내용을 자동으로 저장합니다"
    )
    
    st.session_state.settings = {
        'dark_mode': dark_mode,
        'notifications': notifications,
        'auto_save': auto_save
    }
    
    # 데이터 초기화 버튼
    st.divider()
    
    if st.button("🗑️ 대화 기록 초기화", type="secondary", use_container_width=True):
        if st.button("정말 초기화하시겠습니까?", type="primary"):
            st.session_state.chat_history = []
            st.session_state.total_problems = 0
            st.session_state.solved_problems = 0
            st.success("대화 기록이 초기화되었습니다!")
            st.rerun()