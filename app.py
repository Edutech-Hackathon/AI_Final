import streamlit as st
from dotenv import load_dotenv
import os
from datetime import datetime
import json

from components.sidebar import render_sidebar
from components.chat_interface import ChatInterface
from components.hint_buttons import render_hint_buttons
from components.analytics import render_analytics
from utils.session_manager import SessionManager
from utils.prompt_manager import PromptManager
from config.settings import APP_CONFIG

load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="AI 수학 과외 선생님",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 적용
def load_css():
    """커스텀 CSS 로드"""
    css = """
    <style>
    /* 메인 컨테이너 스타일 */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    /* 힌트 버튼 스타일 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        margin: 0.25rem 0;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 채팅 메시지 스타일 */
    .user-message {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .ai-message {
        background: #e8f4f8;
        padding: 1rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 4px solid #48bb78;
    }
    
    /* 업로드 영역 스타일 */
    .uploadedFile {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1rem;
    }
    
    /* 통계 카드 스타일 */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
    }
    
    /* 힌트 레벨 인디케이터 */
    .hint-level-1 { color: #48bb78; }
    .hint-level-2 { color: #f6ad55; }
    .hint-level-3 { color: #fc8181; }
    
    /* 사이드바 스타일 */
    .sidebar .sidebar-content {
        background: #f7fafc;
        padding: 1rem;
        border-radius: 10px;
    }
    
    /* 진도바 스타일 */
    .progress-bar {
        background: #e2e8f0;
        height: 20px;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .progress-fill {
        background: linear-gradient(90deg, #667eea, #764ba2);
        height: 100%;
        transition: width 0.5s ease;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def init_session_state():
    """세션 상태 초기화 (수정됨)"""
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = SessionManager()
    
    if 'chat_interface' not in st.session_state:
        st.session_state.chat_interface = ChatInterface()
    
    if 'prompt_manager' not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
    
    # 기본 설정값들
    defaults = {
        'chat_history': [],
        'hint_level': 0,
        'selected_persona': 'friendly',
        'total_problems': 0,
        'solved_problems': 0,
        'current_problem': None,
        'analytics_data': {
            'total_hints': 0,
            'hint_distribution': [0, 0, 0],
            'problem_types': {},
            'last_study_date': None
            # study_time 제거됨
        },
        'show_analytics': False,
        'uploaded_image': None,
        'user_name': '학생'
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def main():
    """메인 애플리케이션 실행"""
    
    # CSS 로드
    load_css()
    
    # 세션 상태 초기화
    init_session_state()
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 메인 컨테이너
    main_container = st.container()
    
    with main_container:
        # 헤더
        st.markdown("""
        <div class="main-header">
            <h1>🎓 AI 수학 과외 선생님</h1>
            <p>정답을 알려주지 않고 사고력을 키워주는 단계별 학습 시스템</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 탭 생성
        tab1, tab2, tab3 = st.tabs(["📚 학습하기", "📊 학습 분석", "ℹ️ 사용 방법"])
        
        with tab1:
            render_learning_tab()
        
        with tab2:
            render_analytics_tab()
        
        with tab3:
            render_help_tab()

def render_learning_tab():
    """학습 탭 렌더링"""
    
    # 현재 선택된 선생님 페르소나 표시
    persona_info = get_persona_info(st.session_state.selected_persona)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info(f"**{persona_info['name']} 선생님**과 함께 공부중 {persona_info['emoji']}")
    
    with col2:
        if st.session_state.hint_level > 0:
            st.success(f"현재 힌트 단계: {st.session_state.hint_level}단계")
    
    # 구분선
    st.divider()
    
    # 문제 업로드 섹션
    st.subheader("📷 문제 업로드")
    
    uploaded_file = st.file_uploader(
        "수학 문제 이미지를 업로드하세요",
        type=['png', 'jpg', 'jpeg'],
        help="문제 사진을 찍어서 업로드하거나 스크린샷을 업로드하세요"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.image(uploaded_file, caption="업로드한 문제", use_column_width=True)
            st.session_state.uploaded_image = uploaded_file
        
        with col2:
            st.info("💡 이미지가 업로드되었습니다. 아래에서 힌트 단계를 선택하거나 질문을 입력하세요!")
    
    # 힌트 버튼 섹션
    st.subheader("🎯 힌트 선택")
    
    render_hint_buttons()
    
    # 구분선
    st.divider()
    
    # 채팅 인터페이스
    st.subheader("💬 선생님과 대화")
    
    # 대화 기록 표시
    display_chat_history()
    
    # 사용자 입력
    user_input = st.chat_input("질문을 입력하거나 풀이를 시도해보세요...")
    
    if user_input or st.session_state.hint_level > 0:
        handle_user_input(user_input)

def display_chat_history():
    """대화 기록 표시"""
    for message in st.session_state.chat_history:
        role, content, timestamp = message
        
        if role == "user":
            with st.chat_message("user", avatar="👦"):
                st.markdown(f"**{st.session_state.user_name}**: {content}")
                st.caption(timestamp)
        else:
            persona_info = get_persona_info(st.session_state.selected_persona)
            with st.chat_message("assistant", avatar=persona_info['emoji']):
                st.markdown(f"**{persona_info['name']} 선생님**: {content}")
                st.caption(timestamp)

def handle_user_input(user_input):
    """사용자 입력 처리"""
    from utils.ai_handler import get_ai_response
    
    # 타임스탬프 생성
    timestamp = datetime.now().strftime("%H:%M")
    
    # 사용자 메시지 저장
    if user_input:
        st.session_state.chat_history.append(
            ("user", user_input, timestamp)
        )
    
    # AI 응답 생성
    response = get_ai_response(
        user_input=user_input,
        hint_level=st.session_state.hint_level,
        persona=st.session_state.selected_persona,
        uploaded_image=st.session_state.uploaded_image,
        chat_history=st.session_state.chat_history
    )
    
    # AI 응답 저장
    st.session_state.chat_history.append(
        ("assistant", response, timestamp)
    )
    
    # 통계 업데이트
    update_analytics()
    
    # 힌트 레벨 리셋
    st.session_state.hint_level = 0
    
    # 페이지 리로드
    st.rerun()

def update_analytics():
    """학습 통계 업데이트"""
    if st.session_state.hint_level > 0:
        st.session_state.analytics_data['total_hints'] += 1
        st.session_state.analytics_data['hint_distribution'][st.session_state.hint_level - 1] += 1
    
    st.session_state.analytics_data['last_study_date'] = datetime.now().strftime("%Y-%m-%d %H:%M")

def render_analytics_tab():
    """학습 분석 탭 렌더링"""
    render_analytics()

def render_help_tab():
    """사용 방법 탭 렌더링"""
    st.markdown("""
    ### 🎯 AI 수학 과외 선생님 사용법
    
    #### 1️⃣ 선생님 선택하기
    - 왼쪽 사이드바에서 원하는 선생님 스타일을 선택하세요
    - **친근한 선생님**: 따뜻하고 격려하는 스타일
    - **엄격한 선생님**: 정확하고 체계적인 스타일
    - **중립적 선생님**: 객관적이고 차분한 스타일
    
    #### 2️⃣ 문제 업로드하기
    - 풀고 싶은 수학 문제를 사진으로 찍어 업로드하세요
    - 지원 형식: PNG, JPG, JPEG
    
    #### 3️⃣ 힌트 단계 선택하기
    - **1단계 힌트**: 문제 접근 방법과 방향성 제시
    - **2단계 힌트**: 핵심 개념과 중요 포인트 설명
    - **3단계 힌트**: 실제 풀이 직전까지 구체적 안내
    
    #### 4️⃣ 대화하며 학습하기
    - 선생님과 대화하며 문제를 풀어보세요
    - 모르는 개념은 질문하면 설명해드립니다
    - 절대 정답을 직접 알려주지 않습니다!
    
    #### 5️⃣ 학습 분석 확인하기
    - 학습 분석 탭에서 진도와 패턴을 확인하세요
    - 어떤 유형의 힌트를 많이 사용했는지 분석해보세요
    
    ---
    
    ### 💡 학습 팁
    
    1. **먼저 스스로 시도하기**: 바로 힌트를 보지 말고 먼저 문제를 파악해보세요
    2. **단계적으로 접근하기**: 1단계 힌트부터 차근차근 활용하세요
    3. **개념 이해하기**: 모르는 개념은 꼭 질문해서 이해하고 넘어가세요
    4. **반복 연습하기**: 비슷한 유형의 문제를 여러 번 풀어보세요
    
    ### 🚀 효과적인 학습을 위한 권장사항
    
    - 매일 꾸준히 문제 풀기
    - 틀린 문제는 다시 한번 도전하기
    - 학습 기록을 보며 취약점 파악하기
    - 선생님 피드백을 잘 읽고 이해하기
    """)

def get_persona_info(persona_type):
    """선생님 페르소나 정보 반환"""
    personas = {
        'friendly': {
            'name': '친근한',
            'emoji': '😊',
            'style': '따뜻하고 격려하는'
        },
        'strict': {
            'name': '엄격한',
            'emoji': '🧐',
            'style': '정확하고 체계적인'
        },
        'neutral': {
            'name': '중립적',
            'emoji': '🤖',
            'style': '객관적이고 차분한'
        }
    }
    return personas.get(persona_type, personas['friendly'])

if __name__ == "__main__":
    main()