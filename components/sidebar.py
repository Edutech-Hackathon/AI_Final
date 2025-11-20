import streamlit as st

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
        value=st.session_state.get('user_name', '이름을 입력하세요'),
        key='user_name_input',
        help="선생님이 부를 이름을 입력하세요"
    )
    st.session_state.user_name = user_name
    
    # 학년 선택
    grade = st.selectbox(
        "학년 수준",
        options=["초등학생", "중학생", "고등학생"],
        index=2,
        key='grade_select',
        help="학년 수준을 선택하세요"
    )
    st.session_state.grade = grade

def render_progress():
    """학습 진도 표시 (문제 수 중심)"""
    st.subheader("📈 나의 성장")
    
    total = st.session_state.get('total_problems', 0)
    solved = st.session_state.get('solved_problems', 0)
    
    if total > 0:
        progress = min(solved / total, 1.0)
        st.progress(progress)
        st.caption(f"도전 과제: {solved}개 해결 / {total}개 시도")
    else:
        st.progress(0)
        st.caption("오늘의 첫 문제를 풀어보세요!")
    
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
    
    # 다크 모드 제거했음

    notifications = st.checkbox(
        "학습 알림",
        value=True,
        key='notifications_toggle',
        help="학습 목표 달성시 알림을 받습니다"
    )
    
    auto_save = st.checkbox(
        "대화 자동 저장",
        value=True,
        key='auto_save_toggle',
        help="대화 내용을 자동으로 저장합니다"
    )
    
    # settings에 dark_mode 키도 제거
    st.session_state.settings = {
        'notifications': notifications,
        'auto_save': auto_save
    }
    
    st.divider()
    
    if st.button("🗑️ 대화 기록 초기화", type="secondary", use_container_width=True):
        if st.button("정말 초기화하시겠습니까?", type="primary"):
            st.session_state.chat_history = []
            st.session_state.total_problems = 0
            st.session_state.solved_problems = 0
            st.success("대화 기록이 초기화되었습니다!")
            st.rerun()
