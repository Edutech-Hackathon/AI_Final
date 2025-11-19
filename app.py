"""
문해력 향상 AI 튜터 - Streamlit Application
"""
import streamlit as st
import json
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
from config import (
    APP_TITLE, APP_ICON, LEVELS, QUIZ_TYPES, 
    DEFAULT_QUIZ_COUNT, SESSION_KEYS, 
    SUCCESS_MESSAGES, ENCOURAGEMENT_MESSAGES
)
from utils import TextProcessor, QuizGenerator
import random

# 페이지 설정
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 적용
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 0.5rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .quiz-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
def init_session_state():
    """세션 상태 변수 초기화"""
    for key in SESSION_KEYS.values():
        if key not in st.session_state:
            if key == "history":
                st.session_state[key] = []
            else:
                st.session_state[key] = None

# 프로세서 초기화
@st.cache_resource
def get_processors():
    """텍스트 프로세서와 퀴즈 생성기 초기화 (캐싱)"""
    return TextProcessor(), QuizGenerator()

def display_summary(summary):
    """요약 결과 표시"""
    st.markdown("### 📝 요약 결과")
    st.markdown(summary)
    
def display_keywords(keywords):
    """핵심 키워드 표시"""
    if keywords:
        st.markdown("### 🔑 핵심 키워드")
        cols = st.columns(min(3, len(keywords)))
        for i, keyword in enumerate(keywords):
            with cols[i % 3]:
                st.info(f"**{keyword['word']}**\n\n{keyword['explanation']}")

def display_vocabulary(vocabulary):
    """어휘 목록 표시"""
    if vocabulary:
        st.markdown("### 📖 학습 어휘")
        for vocab in vocabulary:
            with st.expander(f"📌 {vocab['word']}"):
                st.write(f"**뜻**: {vocab['meaning']}")
                st.write(f"**예문**: {vocab['example']}")
                if vocab.get('synonym'):
                    st.write(f"**비슷한 말**: {vocab['synonym']}")

def display_quiz(quiz_data):
    """퀴즈 표시 및 답변 수집"""
    st.markdown("### 🎯 이해도 확인 퀴즈")
    
    user_answers = []
    quiz_type = quiz_data.get("quiz_type", "OX 퀴즈")
    
    with st.form("quiz_form"):
        for i, question in enumerate(quiz_data["questions"]):
            st.markdown(f"**문제 {i+1}. {question['question']}**")
            
            if quiz_type == "OX 퀴즈":
                answer = st.radio(
                    "답을 선택하세요:",
                    ["O", "X"],
                    key=f"q_{i}",
                    horizontal=True
                )
                user_answers.append(answer)
                
            elif quiz_type == "객관식 퀴즈":
                options = question.get("options", ["선택지1", "선택지2", "선택지3", "선택지4"])
                answer = st.radio(
                    "답을 선택하세요:",
                    options,
                    key=f"q_{i}"
                )
                user_answers.append(options.index(answer))
                
            else:  # 빈칸 채우기
                answer = st.text_input(
                    "답을 입력하세요:",
                    key=f"q_{i}"
                )
                user_answers.append(answer)
            
            st.markdown("---")
        
        submitted = st.form_submit_button("제출하기 📮")
        
        if submitted:
            st.session_state["quiz_answers"] = user_answers
            st.session_state["quiz_submitted"] = True
            
    return user_answers

def display_results(quiz_data, results):
    """퀴즈 결과 표시"""
    st.markdown("### 📊 퀴즈 결과")
    
    # 점수 표시
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("전체 문제", f"{results['total']}문제")
    with col2:
        st.metric("정답", f"{results['correct']}문제", 
                 delta=f"+{results['correct']}")
    with col3:
        st.metric("정답률", f"{results['percentage']}%")
    
    # 결과 차트
    fig = go.Figure(data=[
        go.Bar(name='정답', x=['결과'], y=[results['correct']], 
              marker_color='green'),
        go.Bar(name='오답', x=['결과'], y=[results['incorrect']], 
              marker_color='red')
    ])
    fig.update_layout(
        barmode='stack',
        height=300,
        showlegend=True,
        title="퀴즈 결과 차트"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # 상세 결과
    st.markdown("### 📝 문제별 결과")
    for detail in results['details']:
        if detail['is_correct']:
            st.success(f"✅ 문제 {detail['question_id']}: 정답!")
        else:
            st.error(f"❌ 문제 {detail['question_id']}: 오답")
            st.write(f"**문제**: {detail['question']}")
            st.write(f"**당신의 답**: {detail['user_answer']}")
            st.write(f"**정답**: {detail['correct_answer']}")
            st.write(f"**해설**: {detail['explanation']}")
        st.markdown("---")

def display_learning_history():
    """학습 기록 표시"""
    if st.session_state.get("history"):
        st.markdown("### 📈 학습 기록")
        
        df = pd.DataFrame(st.session_state["history"])
        
        # 시간별 점수 추이
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['score'],
            mode='lines+markers',
            name='정답률',
            line=dict(color='blue', width=2)
        ))
        fig.update_layout(
            title="학습 진도",
            xaxis_title="시간",
            yaxis_title="정답률 (%)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 학습 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 학습 횟수", len(df))
        with col2:
            st.metric("평균 점수", f"{df['score'].mean():.1f}%")
        with col3:
            st.metric("최고 점수", f"{df['score'].max():.1f}%")

# 메인 앱
def main():
    """메인 애플리케이션"""
    
    # 세션 상태 초기화
    init_session_state()
    
    # 프로세서 가져오기
    text_processor, quiz_generator = get_processors()
    
    # 헤더
    st.title(APP_TITLE)
    st.markdown("어려운 글을 쉽게 이해하고, 퀴즈로 학습해보세요! 🚀")
    
    # 사이드바
    with st.sidebar:
        st.header("⚙️ 설정")
        
        # 난이도 선택
        selected_level = st.selectbox(
            "📊 학습 수준 선택",
            list(LEVELS.keys()),
            help="본인의 학습 수준을 선택하세요"
        )
        
        level_info = LEVELS[selected_level]
        st.info(level_info["description"])
        
        st.markdown("---")
        
        # 퀴즈 설정
        st.subheader("🎯 퀴즈 설정")
        
        quiz_type = st.selectbox(
            "퀴즈 유형",
            QUIZ_TYPES,
            help="원하는 퀴즈 형식을 선택하세요"
        )
        
        quiz_count = st.slider(
            "문제 개수",
            min_value=3,
            max_value=10,
            value=DEFAULT_QUIZ_COUNT,
            help="생성할 퀴즈 문제 개수"
        )
        
        st.markdown("---")
        
        # 추가 기능
        st.subheader("🔧 추가 기능")
        
        show_keywords = st.checkbox("핵심 키워드 추출", value=True)
        show_vocabulary = st.checkbox("학습 어휘 목록", value=False)
        show_difficulty = st.checkbox("난이도 분석", value=False)
        
        st.markdown("---")
        
        # 학습 기록
        if st.button("📈 학습 기록 보기"):
            st.session_state["show_history"] = True
            
        if st.button("🔄 새로 시작"):
            for key in SESSION_KEYS.values():
                if key != "history":
                    st.session_state[key] = None
            st.rerun()
    
    # 메인 컨텐츠
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📄 텍스트 입력")
        
        # 텍스트 입력
        input_text = st.text_area(
            "어려운 텍스트를 붙여넣으세요",
            height=300,
            placeholder="뉴스 기사, 교과서 내용, 논문 등 이해하기 어려운 텍스트를 입력하세요...",
            help="최대 10,000자까지 입력 가능합니다"
        )
        
        # 예시 텍스트 제공
        if st.button("📝 예시 텍스트 불러오기"):
            input_text = """
            인공지능(AI)은 인간의 학습능력, 추론능력, 지각능력을 인공적으로 구현한 컴퓨터 과학의 한 분야이다. 
            최근 딥러닝 기술의 발전으로 AI는 이미지 인식, 자연어 처리, 음성 인식 등 다양한 분야에서 인간 수준을 
            뛰어넘는 성능을 보이고 있다. 특히 대규모 언어 모델(LLM)은 방대한 텍스트 데이터를 학습하여 
            인간처럼 자연스러운 대화를 나누고, 복잡한 질문에 답하며, 창의적인 콘텐츠를 생성할 수 있게 되었다. 
            이러한 AI 기술의 발전은 의료, 교육, 금융, 제조업 등 산업 전반에 걸쳐 혁신을 가져오고 있으며, 
            우리의 일상생활도 크게 변화시키고 있다.
            """
            st.session_state["sample_text"] = input_text
        
        # 예시 텍스트가 있으면 표시
        if "sample_text" in st.session_state:
            input_text = st.session_state["sample_text"]
            st.text_area("예시 텍스트", value=input_text, height=300, disabled=True)
        
        # 요약 버튼
        if st.button("🚀 요약 및 퀴즈 생성", type="primary", disabled=not input_text):
            if len(input_text) < 50:
                st.warning("텍스트가 너무 짧습니다. 50자 이상 입력해주세요.")
            else:
                with st.spinner("텍스트를 분석하고 있습니다..."):
                    # 텍스트 저장
                    st.session_state["current_text"] = input_text
                    
                    # 난이도 분석 (옵션)
                    if show_difficulty:
                        difficulty_analysis = text_processor.analyze_difficulty(input_text)
                        st.info(f"""
                        **난이도 분석 결과**
                        - 전체 난이도: {difficulty_analysis['difficulty_level']}
                        - 어려운 단어: {difficulty_analysis['difficult_words_count']}개
                        - 문장 길이: {difficulty_analysis['avg_sentence_length']}
                        - 추천: {difficulty_analysis['recommendation']}
                        """)
                    
                    # 요약 생성
                    summary = text_processor.summarize_text(input_text, level_info)
                    st.session_state["summary"] = summary
                    
                    # 키워드 추출 (옵션)
                    if show_keywords:
                        keywords = text_processor.extract_keywords(input_text)
                        st.session_state["keywords"] = keywords
                    
                    # 어휘 목록 생성 (옵션)
                    if show_vocabulary:
                        vocabulary = text_processor.create_vocabulary_list(
                            input_text, selected_level
                        )
                        st.session_state["vocabulary"] = vocabulary
                    
                    # 퀴즈 생성
                    quiz_data = quiz_generator.generate_quiz(
                        input_text, summary, quiz_type, quiz_count
                    )
                    st.session_state["quiz"] = quiz_data
                    
                    st.success("✅ 요약과 퀴즈가 생성되었습니다!")
    
    with col2:
        # 결과 표시 영역
        if st.session_state.get("summary"):
            # 요약 표시
            display_summary(st.session_state["summary"])
            
            # 키워드 표시
            if st.session_state.get("keywords"):
                display_keywords(st.session_state["keywords"])
            
            # 어휘 목록 표시
            if st.session_state.get("vocabulary"):
                display_vocabulary(st.session_state["vocabulary"])
            
            st.markdown("---")
            
            # 퀴즈 표시
            if st.session_state.get("quiz") and not st.session_state.get("quiz_submitted"):
                display_quiz(st.session_state["quiz"])
            
            # 결과 표시
            if st.session_state.get("quiz_submitted"):
                # 답안 평가
                results = quiz_generator.evaluate_answers(
                    st.session_state["quiz"],
                    st.session_state["quiz_answers"]
                )
                
                # 결과 표시
                display_results(st.session_state["quiz"], results)
                
                # 피드백 생성
                feedback = quiz_generator.generate_feedback(results)
                st.markdown("### 💬 선생님의 피드백")
                st.info(feedback)
                
                # 학습 기록 저장
                st.session_state["history"].append({
                    "timestamp": datetime.now(),
                    "level": selected_level,
                    "quiz_type": quiz_type,
                    "score": results['percentage'],
                    "correct": results['correct'],
                    "total": results['total']
                })
                
                # 재도전 버튼
                if st.button("🔄 다른 퀴즈 풀기"):
                    st.session_state["quiz_submitted"] = False
                    st.session_state["quiz_answers"] = None
                    # 새로운 퀴즈 생성
                    new_quiz = quiz_generator.generate_quiz(
                        st.session_state["current_text"],
                        st.session_state["summary"],
                        quiz_type,
                        quiz_count
                    )
                    st.session_state["quiz"] = new_quiz
                    st.rerun()
    
    # 학습 기록 표시
    if st.session_state.get("show_history"):
        st.markdown("---")
        display_learning_history()

# 앱 실행
if __name__ == "__main__":
    # API 키 확인
    from config import OPENAI_API_KEY
    
    if not OPENAI_API_KEY:
        st.error("""
        ⚠️ OpenAI API 키가 설정되지 않았습니다!
        
        1. `.env` 파일을 생성하세요
        2. `OPENAI_API_KEY=your-api-key-here`를 추가하세요
        3. 앱을 다시 실행하세요
        """)
    else:
        main()
