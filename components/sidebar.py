# 사이드바 컴포넌트: 학생 정보, 학습 진도, 설정 등을 관리

import streamlit as st
from datetime import datetime, timedelta

def render_sidebar():
    """사이드바 렌더링"""
    
    with st.sidebar:
        # 로고와 타이틀
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
        value=st.session_state.get('user_name', '학생'),
        key='user_name_input',
        help="선생님이 부를 이름을 입력하세요"
    )
    st.session_state.user_name = user_name
    
    # 학년 선택 (3가지 옵션으로 단순화)
    grade = st.selectbox(
        "학년",
        options=["초등학생", "중학생", "고등학생"],
        index=1,  # 기본값: 중학생
        key='grade_select',
        help="학년을 선택하세요"
    )
    st.session_state.grade = grade
    
    # 학년별 학습 주제 표시
    from utils.prompt_manager import GRADE_LEVELS
    if grade in GRADE_LEVELS:
        topics = GRADE_LEVELS[grade]['topics']
        with st.expander("📚 주요 학습 주제", expanded=False):
            for topic in topics:
                st.markdown(f"• {topic}")

def render_progress():
    """학습 진도 표시"""
    st.subheader("📈 오늘의 학습")
    
    # 진도율 계산
    total = st.session_state.get('total_problems', 0)
    solved = st.session_state.get('solved_problems', 0)
    
    if total > 0:
        progress = solved / total
        st.progress(progress)
        st.caption(f"해결한 문제: {solved}/{total}")
    else:
        st.progress(0)
        st.caption("아직 시작하지 않았어요")
    
    # 오늘 푼 문제 수 표시
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            label="해결한 문제",
            value=f"{solved}개",
            delta="+1" if solved > 0 else None
        )
    with col2:
        # 정답률 계산
        solve_rate = 0
        if total > 0:
            solve_rate = round((solved / total) * 100)
        st.metric(
            label="정답률",
            value=f"{solve_rate}%"
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
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 새 문제 시작", type="primary", use_container_width=True):
            # 현재 문제 관련 상태만 초기화
            st.session_state.hint_level = 0
            st.session_state.problem_image = None
            st.session_state.solution_image = None
            st.session_state.request_type = None
            st.session_state.chat_ended = False
            st.success("새 문제를 시작할 수 있습니다!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ 전체 초기화", type="secondary", use_container_width=True):
            # 확인 다이얼로그
            st.warning("⚠️ 모든 학습 기록이 삭제됩니다!")
            if st.button("정말 초기화하시겠습니까?", key="confirm_reset"):
                st.session_state.chat_history = []
                st.session_state.total_problems = 0
                st.session_state.solved_problems = 0
                st.session_state.analytics_data = {
                    'total_hints': 0,
                    'hint_distribution': [0, 0, 0],
                    'problem_types': {},
                    'last_study_date': None,
                    'events': []
                }
                st.success("전체 기록이 초기화되었습니다!")
                st.rerun()
