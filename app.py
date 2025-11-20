"""
AI 수학 과외 애플리케이션 메인 파일
"""

import streamlit as st
import os
from datetime import datetime
from components import (
    render_analytics,
    ChatInterface,
    render_hint_buttons,
    render_sidebar,
    render_teacher_selection
)
from utils import (
    get_ai_response,
    SessionManager
)

# 페이지 설정
st.set_page_config(
    page_title="AI 수학 과외",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
def load_css():
    st.markdown("""
    <style>
    /* 메인 컨테이너 */
    .main {
        padding: 1rem;
    }
    
    /* 메시지 스타일 */
    .user-message {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .ai-message {
        background: #f3e5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #9c27b0;
    }
    
    /* 통계 카드 */
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stat-card h1 {
        color: #2d3748;
        margin: 0.5rem 0;
    }
    
    .stat-card h3 {
        margin: 0;
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    /* 정답 표시 */
    .correct-answer {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .incorrect-answer {
        background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 2rem 0;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# 세션 초기화
def initialize_session():
    """세션 상태 초기화"""
    session_manager = SessionManager()
    
    # 기본 세션 상태
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'analytics_data' not in st.session_state:
        st.session_state.analytics_data = {
            'total_hints': 0,
            'hint_distribution': [0, 0, 0],
            'problem_types': {},
            'events': []
        }
    
    if 'total_problems' not in st.session_state:
        st.session_state.total_problems = 0
    
    if 'solved_problems' not in st.session_state:
        st.session_state.solved_problems = 0
    
    if 'hint_level' not in st.session_state:
        st.session_state.hint_level = 0
    
    if 'selected_persona' not in st.session_state:
        st.session_state.selected_persona = 'friendly'
    
    if 'user_name' not in st.session_state:
        st.session_state.user_name = '학생'
    
    if 'grade' not in st.session_state:
        st.session_state.grade = '중학생'
    
    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'dark_mode': False,
            'notifications': True,
            'auto_save': True
        }
    
    if 'chat_ended' not in st.session_state:
        st.session_state.chat_ended = False
    
    if 'problem_image' not in st.session_state:
        st.session_state.problem_image = None
    
    if 'solution_image' not in st.session_state:
        st.session_state.solution_image = None
    
    if 'current_problem_id' not in st.session_state:
        st.session_state.current_problem_id = None

def main():
    """메인 애플리케이션"""
    
    # 스타일 로드
    load_css()
    
    # 세션 초기화
    initialize_session()
    
    # 사이드바 렌더링
    render_sidebar()
    
    # 메인 영역
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1>🎓 AI 수학 과외 선생님</h1>
        <p style='color: #718096; font-size: 1.1rem;'>
            단계별 힌트로 스스로 문제를 해결해보세요!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 탭 생성
    tab1, tab2, tab3 = st.tabs(["📚 학습하기", "📊 성과 분석", "❓ 사용 방법"])
    
    with tab1:
        render_study_tab()
    
    with tab2:
        render_analytics()
    
    with tab3:
        render_help_tab()

def render_study_tab():
    """학습 탭 렌더링"""
    
    # 문제 이미지 업로드 섹션
    st.markdown("### 📝 문제 업로드")
    
    problem_image = st.file_uploader(
        "문제 이미지를 업로드하세요",
        type=['png', 'jpg', 'jpeg'],
        key='problem_image_upload',
        help="문제가 담긴 이미지를 업로드하세요"
    )
    
    if problem_image:
        st.session_state.problem_image = problem_image
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(problem_image, caption="업로드된 문제", use_container_width=True)
        
        with col2:
            if st.session_state.get('total_problems', 0) == 0 or st.button("🆕 새 문제로 등록"):
                st.session_state.total_problems += 1
                st.session_state.current_problem_id = datetime.now().strftime("%Y%m%d%H%M%S")
                st.session_state.chat_ended = False
                st.session_state.hint_level = 0
                st.success("새 문제가 등록되었습니다!")
                
                # 세션 매니저를 통해 분석 데이터 업데이트
                session_manager = SessionManager()
                session_manager.update_analytics('problem_started', {
                    'problem_id': st.session_state.current_problem_id
                })
    
    st.divider()
    
    # 선생님 선택 컴포넌트 (힌트 버튼과 채팅 인터페이스 사이에 위치)
    render_teacher_selection()
    
    st.divider()
    
    # 힌트 버튼
    st.markdown("### 💡 힌트 선택")
    
    # 채팅이 종료되었는지 확인
    if st.session_state.get('chat_ended', False):
        st.success("🎉 문제를 해결했습니다! 새로운 문제를 시작하려면 사이드바의 '새 문제 시작' 버튼을 눌러주세요.")
    else:
        render_hint_buttons()
    
    st.divider()
    
    # 채팅 인터페이스
    st.markdown("### 💬 AI 선생님과 대화")
    
    # 채팅 히스토리 표시
    chat_container = st.container()
    with chat_container:
        for role, content, timestamp in st.session_state.chat_history:
            if role == "user":
                st.markdown(f"""
                <div class='user-message'>
                    <strong>👦 {st.session_state.user_name}</strong>
                    <span style='float: right; color: #718096;'>{timestamp}</span>
                    <p>{content}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                persona_emoji = {'friendly': '😊', 'strict': '🧐', 'neutral': '🤖'}
                persona_name = {'friendly': '친근한', 'strict': '엄격한', 'neutral': '중립적'}
                emoji = persona_emoji.get(st.session_state.selected_persona, '👨‍🏫')
                name = persona_name.get(st.session_state.selected_persona, 'AI')
                
                st.markdown(f"""
                <div class='ai-message'>
                    <strong>{emoji} {name} 선생님</strong>
                    <span style='float: right; color: #718096;'>{timestamp}</span>
                    <p>{content}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # 채팅이 종료되지 않았을 때만 입력 가능
    if not st.session_state.get('chat_ended', False):
        # 사용자 입력
        user_input = st.chat_input(
            "질문이나 답을 입력하세요...",
            key="user_input_chat"
        )
        
        if user_input:
            # 타임스탬프
            timestamp = datetime.now().strftime("%H:%M")
            
            # 사용자 메시지 추가
            st.session_state.chat_history.append(
                ("user", user_input, timestamp)
            )
            
            # 풀이 이미지 가져오기 (있다면)
            solution_image = st.session_state.get('solution_image', None)
            
            # AI 응답 생성
            ai_response, is_correct = get_ai_response(
                user_input,
                st.session_state.hint_level,
                st.session_state.selected_persona,
                problem_image=st.session_state.problem_image,
                solution_image=solution_image,
                chat_history=st.session_state.chat_history
            )
            
            # AI 응답 추가
            st.session_state.chat_history.append(
                ("assistant", ai_response, timestamp)
            )
            
            # 정답 확인 결과 처리
            if is_correct:
                st.session_state.chat_ended = True
                st.balloons()
                
                # 정답 메시지 표시
                st.markdown("""
                <div class='correct-answer'>
                    <h1>🎉 정답입니다!</h1>
                    <p>훌륭해요! 문제를 성공적으로 해결했습니다.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 풀이 이미지 초기화
            st.session_state.solution_image = None
            
            # 페이지 새로고침
            st.rerun()

def render_help_tab():
    """사용 방법 탭 렌더링"""
    
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;'>
        <h2 style='margin: 0;'>🎯 AI 수학 과외 선생님 사용법</h2>
        <p style='margin: 0.5rem 0 0 0;'>효과적인 학습을 위한 가이드</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 단계별 사용법
    st.markdown("## 📖 단계별 사용 가이드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 1️⃣ 선생님 선택하기
        - **친근한 선생님 😊**: 따뜻하고 격려하는 스타일
        - **엄격한 선생님 🧐**: 정확하고 체계적인 스타일
        - **중립적 선생님 🤖**: 객관적이고 차분한 스타일
        
        > 💡 선생님은 언제든지 변경할 수 있어요!
        
        ---
        
        ### 2️⃣ 문제 업로드하기
        - 풀고 싶은 수학 문제를 사진으로 찍어 업로드하세요
        - 지원 형식: PNG, JPG, JPEG
        - 문제가 잘 보이도록 깨끗하게 촬영해주세요
        
        ---
        
        ### 3️⃣ 힌트 단계 선택하기
        - **🌱 1단계 힌트**: 문제 접근 방법과 방향성 제시
        - **🌿 2단계 힌트**: 핵심 개념과 중요 포인트 설명
        - **🌳 3단계 힌트**: 실제 풀이 직전까지 구체적 안내
        
        > ⚠️ 1단계부터 차근차근 시도해보세요!
        """)
    
    with col2:
        st.markdown("""
        ### 4️⃣ 대화하며 학습하기
        - 선생님과 대화하며 문제를 풀어보세요
        - 모르는 개념은 질문하면 설명해드립니다
        - **절대 정답을 직접 알려주지 않습니다!**
        
        ---
        
        ### 5️⃣ 정답 제출하기
        
        **방법 1**: 정답 제출 버튼 사용
        - "🏆 정답 제출/확인" 버튼 클릭
        - 답을 입력하고 전송
        
        **방법 2**: 채팅창에 직접 입력
        - 채팅창에 답을 적어서 전송
        
        **방법 3**: 풀이 사진 업로드
        - 텍스트 또는 사진으로 풀이 작성
        - "✅ 풀이 확인 요청" 버튼 클릭
        
        ---
        
        ### 6️⃣ 학습 분석 확인하기
        - "📊 성과 분석" 탭에서 진도 확인
        - 어떤 힌트를 많이 사용했는지 분석
        - 정답률과 학습 패턴 파악
        """)
    
    st.divider()
    
    # 학습 팁
    st.markdown("## 💡 효과적인 학습 팁")
    
    tips_col1, tips_col2, tips_col3 = st.columns(3)
    
    with tips_col1:
        st.markdown("""
        <div style='background: #e3f2fd; padding: 1.5rem; border-radius: 10px; height: 100%;'>
            <h3 style='color: #1976d2;'>🎯 학습 전략</h3>
            <ul>
                <li>먼저 스스로 시도하기</li>
                <li>단계적으로 접근하기</li>
                <li>개념부터 이해하기</li>
                <li>비슷한 문제 반복하기</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tips_col2:
        st.markdown("""
        <div style='background: #f3e5f5; padding: 1.5rem; border-radius: 10px; height: 100%;'>
            <h3 style='color: #7b1fa2;'>📝 좋은 습관</h3>
            <ul>
                <li>매일 꾸준히 학습하기</li>
                <li>틀린 문제 다시 도전하기</li>
                <li>학습 기록 분석하기</li>
                <li>피드백 꼼꼼히 읽기</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with tips_col3:
        st.markdown("""
        <div style='background: #e8f5e9; padding: 1.5rem; border-radius: 10px; height: 100%;'>
            <h3 style='color: #388e3c;'>🚀 성장 마인드</h3>
            <ul>
                <li>실수는 배움의 기회</li>
                <li>시간보다 이해가 중요</li>
                <li>질문하는 것이 최고</li>
                <li>조금씩 성장하기</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # FAQ
    st.markdown("## ❓ 자주 묻는 질문 (FAQ)")
    
    with st.expander("Q1. 힌트를 여러 번 사용해도 되나요?"):
        st.markdown("""
        **네, 물론입니다!** 힌트는 학습을 돕기 위한 도구입니다. 
        필요한 만큼 사용하세요. 다만, 1단계부터 차근차근 시도하면 
        더 효과적인 학습이 가능합니다.
        """)
    
    with st.expander("Q2. 정답을 맞히지 못하면 어떻게 되나요?"):
        st.markdown("""
        **걱정하지 마세요!** 틀린 답을 제출하면 선생님이 어디서 실수했는지 
        힌트를 주고 다시 도전할 수 있게 도와줍니다. 실수는 배움의 과정입니다.
        """)
    
    with st.expander("Q3. 풀이 과정도 확인해줄 수 있나요?"):
        st.markdown("""
        **가능합니다!** "✅ 풀이 확인 요청" 기능을 사용하세요. 
        텍스트로 풀이를 입력하거나 손으로 쓴 풀이를 사진으로 찍어 
        업로드하면 선생님이 확인해드립니다.
        """)
    
    with st.expander("Q4. 개념을 잘 모르겠어요. 어떻게 하나요?"):
        st.markdown("""
        **개념 설명을 요청하세요!** "📝 개념 설명 요청" 버튼을 누르고 
        궁금한 개념을 물어보세요. 선생님이 쉽게 설명해드립니다.
        """)
    
    with st.expander("Q5. 학습 기록은 어떻게 확인하나요?"):
        st.markdown("""
        **"📊 성과 분석" 탭**으로 이동하세요. 
        - 해결한 문제 수
        - 힌트 사용 패턴
        - 정답률
        - 주간 학습 진도
        
        등을 한눈에 확인할 수 있습니다.
        """)
    
    with st.expander("Q6. 선생님 스타일은 언제 바꿀 수 있나요?"):
        st.markdown("""
        **언제든지 변경 가능합니다!** 학습 중간에도 선생님 선택 영역에서 
        다른 스타일을 선택하면 바로 적용됩니다.
        """)
    
    st.divider()
    
    # 학습 목표 설정
    st.markdown("## 🎯 나만의 학습 목표 세우기")
    
    goal_col1, goal_col2 = st.columns([2, 1])
    
    with goal_col1:
        st.markdown("""
        효과적인 학습을 위해 목표를 세워보세요:
        
        ### 단기 목표 (이번 주)
        - [ ] 문제 10개 해결하기
        - [ ] 1단계 힌트만으로 3문제 풀기
        - [ ] 틀린 문제 다시 풀어서 맞추기
        - [ ] 3일 연속 학습하기
        
        ### 중기 목표 (이번 달)
        - [ ] 약한 단원 집중 공략하기
        - [ ] 정답률 80% 이상 달성하기
        - [ ] 개념 설명 요청 줄이기
        - [ ] 학습 시간 꾸준히 유지하기
        
        ### 장기 목표 (학기)
        - [ ] 모든 단원 마스터하기
        - [ ] 힌트 없이 문제 풀기
        - [ ] 어려운 문제도 도전하기
        - [ ] 꾸준한 학습 습관 만들기
        """)
    
    with goal_col2:
        st.info("""
        💪 **성장을 위한 격려**
        
        "천천히 가도 괜찮아요.
        중요한 건 꾸준히
        앞으로 나아가는 거예요!"
        
        한 문제 한 문제
        정확히 이해하며
        풀어가세요. 🌱→🌿→🌳
        """)
    
    st.divider()
    
    # 추가 도움말
    st.markdown("## 🆘 추가 도움이 필요하신가요?")
    
    help_col1, help_col2, help_col3 = st.columns(3)
    
    with help_col1:
        st.markdown("""
        <div style='background: #fff3cd; padding: 1rem; border-radius: 10px; text-align: center;'>
            <h3>📚 학습 자료</h3>
            <p>개념 정리 노트와<br>추가 문제를 제공합니다</p>
        </div>
        """, unsafe_allow_html=True)
    
    with help_col2:
        st.markdown("""
        <div style='background: #d1ecf1; padding: 1rem; border-radius: 10px; text-align: center;'>
            <h3>💬 질문하기</h3>
            <p>언제든지 선생님께<br>질문하세요</p>
        </div>
        """, unsafe_allow_html=True)
    
    with help_col3:
        st.markdown("""
        <div style='background: #d4edda; padding: 1rem; border-radius: 10px; text-align: center;'>
            <h3>📊 진도 확인</h3>
            <p>성과 분석 탭에서<br>발전 상황을 확인하세요</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
