# Hint 버튼 컴포넌트 : 단계별 힌트 버튼을 관리하고 렌더링

import streamlit as st

def render_hint_buttons():
    """힌트 버튼 렌더링"""
    
    # 힌트 단계 설명
    st.markdown("""
    <div style='background: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
        <p><strong>💡 힌트를 단계별로 선택하세요:</strong></p>
        <ul style='margin: 0.5rem 0;'>
            <li><strong>1단계</strong>: 문제를 어떻게 접근할지 방향을 잡아드려요</li>
            <li><strong>2단계</strong>: 핵심 개념과 중요한 포인트를 짚어드려요</li>
            <li><strong>3단계</strong>: 풀이 직전까지 구체적으로 안내해드려요</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # 3개 컬럼으로 버튼 배치
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(
            "🌱 1단계 힌트",
            key="hint_1",
            help="문제 접근 방법을 알려드립니다",
            use_container_width=True,
            type="secondary"
        ):
            handle_hint_click(1)
            st.success("1단계 힌트를 요청했습니다!")
    
    with col2:
        if st.button(
            "🌿 2단계 힌트",
            key="hint_2",
            help="핵심 개념을 설명해드립니다",
            use_container_width=True,
            type="secondary"
        ):
            handle_hint_click(2)
            st.success("2단계 힌트를 요청했습니다!")
    
    with col3:
        if st.button(
            "🌳 3단계 힌트",
            key="hint_3",
            help="구체적인 풀이 방향을 제시합니다",
            use_container_width=True,
            type="secondary"
        ):
            handle_hint_click(3)
            st.success("3단계 힌트를 요청했습니다!")
    
    # 현재 선택된 힌트 레벨 표시
    if st.session_state.hint_level > 0:
        display_hint_level_indicator()
    
    # 추가 옵션
    render_additional_options()

def handle_hint_click(level):
    """힌트 버튼 클릭 처리"""
    st.session_state.hint_level = level
    
    # 통계 업데이트
    st.session_state.analytics_data['total_hints'] += 1
    st.session_state.analytics_data['hint_distribution'][level - 1] += 1
    
    # 로그 메시지 추가
    from datetime import datetime
    timestamp = datetime.now().strftime("%H:%M")
    
    hint_messages = {
        1: "어떻게 접근해야 할지 모르겠어요! (1단계 힌트)",
        2: "핵심 개념이 궁금해요! (2단계 힌트)",
        3: "마지막 힌트가 필요해요! (3단계 힌트)"
    }
    
    st.session_state.chat_history.append(
        ("user", hint_messages[level], timestamp)
    )

def display_hint_level_indicator():
    """현재 힌트 레벨 인디케이터 표시"""
    level = st.session_state.hint_level
    
    colors = {
        1: "#48bb78",  # 초록색
        2: "#f6ad55",  # 주황색
        3: "#fc8181"   # 빨간색
    }
    
    descriptions = {
        1: "기초 힌트",
        2: "중급 힌트",
        3: "고급 힌트"
    }
    
    st.markdown(f"""
    <div style='
        background: {colors[level]}20;
        border: 2px solid {colors[level]};
        padding: 0.5rem 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    '>
        <strong style='color: {colors[level]};'>
            {level}단계 {descriptions[level]} 선택됨
        </strong>
    </div>
    """, unsafe_allow_html=True)

def render_additional_options():
    """추가 옵션 렌더링"""
    
    with st.expander("🔧 추가 도구", expanded=False):
        col1, col2 = st.columns(2)
        
        # ① 정답 입력하기
        with col1:
            if st.button(
                "✅ 정답 입력하기",
                key="submit_answer",
                use_container_width=True,
                help="지금까지 생각한 최종 답을 입력합니다"
            ):
                st.session_state.request_type = "answer"
                st.info("정답이라고 생각하는 값을 아래 대화창에 **숫자만** 입력해보세요!")

        # ② 풀이 확인
        with col2:
            if st.button(
                "✏️ 풀이 확인",
                key="check_solution",
                use_container_width=True,
                help="작성한 풀이가 맞는지 확인해드립니다"
            ):
                st.session_state.request_type = "check"
                st.info("풀이를 아래 입력창에 적어주면 선생님이 확인해줄게!")

        col3, col4 = st.columns(2)

        # ③ 유사 문제
        with col3:
            if st.button(
                "📚 유사 문제",
                key="similar_problem",
                use_container_width=True,
                help="비슷한 유형의 문제를 제공합니다"
            ):
                st.session_state.request_type = "similar"
                st.info("유사 문제를 요청했습니다. 잠시만 기다려줘!")

def get_hint_emoji(level):
    """힌트 레벨에 따른 이모지 반환"""
    emojis = {
        1: "🌱",
        2: "🌿",
        3: "🌳"
    }
    return emojis.get(level, "💡")

def get_hint_color(level):
    """힌트 레벨에 따른 색상 반환"""
    colors = {
        1: "green",
        2: "orange",
        3: "red"
    }
    return colors.get(level, "blue")