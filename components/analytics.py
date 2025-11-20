# 학습 분석 컴포넌트: 문제 해결 성과 및 정답률 중심 분석

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from openai import OpenAI
from config.settings import get_config  # GRADE_LEVELS 가져오기

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
    
    # 상세 분석 + 최근 풀이 리뷰
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
    """상세 분석 섹션 (강점/약점 분석 + 최근 풀이 리뷰)"""
    st.subheader("🔍 상세 학습 분석")

    # 안내 문구 (전체 폭)
    solved_count = st.session_state.get('solved_problems', 0)
    if solved_count < 3:
        st.info("📚 문제를 3개 이상 풀면 AI가 강점과 약점을 분석해드려요!")

    # 아래를 1:1 컬럼으로 나누기
    col1, col2 = st.columns(2)

    with col1:
        render_strengths_weaknesses()

    with col2:
        render_solution_review()

def render_strengths_weaknesses():
    """강점과 약점 분석 (레이더 차트)"""

    # 🔹 1) 현재 학년에 맞는 토픽 목록 가져오기
    grades_config = get_config('grades')  # settings.GRADE_LEVELS
    ui_grade = st.session_state.get('grade', '고등학생')

    possible_grade = (ui_grade or '').lower()

    elem_key = next((k for k in grades_config.keys()
                     if 'elementary' in k.lower() or '초등학생' in k), None)
    mid_key = next((k for k in grades_config.keys()
                    if 'middle' in k.lower() or '중학생' in k), None)
    high_key = next((k for k in grades_config.keys()
                     if 'high' in k.lower() or '고등학생' in k), None)

    if '초등학생' in possible_grade or 'elementary' in possible_grade:
        grade_key = elem_key
    elif '중학생' in possible_grade or 'middle' in possible_grade:
        grade_key = mid_key
    elif '고등학생' in possible_grade or 'high' in possible_grade:
        grade_key = high_key
    else:
        grade_key = ui_grade if ui_grade in grades_config else mid_key

    if grade_key and grade_key in grades_config:
        categories = grades_config[grade_key].get('topics', [])
    else:
        categories = ['지수와 로그', '수열', '미적분', '확률과 통계', '기하와 벡터']

    # 🔹 2) topic_stats 기반으로 각 토픽별 점수 계산
    topic_stats = st.session_state.analytics_data.get('topic_stats', {})

    values = []
    for topic in categories:
        stat = topic_stats.get(topic, {'attempted': 0, 'solved': 0})
        attempted = stat.get('attempted', 0)
        solved = stat.get('solved', 0)

        if attempted == 0:
            score = 20  # 아직 안 풀어본 단원은 기본값
        else:
            acc = solved / attempted  # 정답률 0~1
            score = 20 + acc * 80     # 20~100 범위로 스케일링

        values.append(score)

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

def render_solution_review():
    """
    최근에 맞힌 한 문제에 대해
    - 풀이 흐름을 정리하고
    - 잘한 점 / 개선하면 좋을 점을 피드백하는 섹션
    """
    st.markdown("#### 📝 최근 풀이 정리 & 피드백")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.info("⚠️ 풀이 리뷰 생성을 위해 OpenAI API 키가 필요합니다.")
        return

    chat_history = st.session_state.get("chat_history", [])
    if not chat_history:
        st.info("아직 대화 기록이 없어요. 먼저 문제를 풀어보면 풀이 리뷰를 보여줄게요 😊")
        return

    # 1️⃣ 가장 최근에 '정답입니다' 로 시작하는 assistant 메시지를 찾기
    last_correct_idx = None
    for i in range(len(chat_history) - 1, -1, -1):
        role, content, ts = chat_history[i]
        if role == "assistant" and isinstance(content, str) and content.strip().startswith("정답입니다"):
            last_correct_idx = i
            break

    if last_correct_idx is None:
        st.info("아직 정답으로 마무리된 문제가 없어요. 정답을 맞히면 풀이 리뷰가 생성됩니다! ✨")
        return

    # 2️⃣ 해당 문제 주변 대화들을 모아서 컨텍스트 생성
    start_idx = max(0, last_correct_idx - 10)  # 최근 10개 정도 포함
    relevant_history = chat_history[start_idx:last_correct_idx + 1]

    convo_lines = []
    for role, content, ts in relevant_history:
        speaker = "학생" if role == "user" else "선생님"
        convo_lines.append(f"{speaker}: {content}")
    conversation_text = "\n".join(convo_lines)

    # 3️⃣ 캐시 키 (같은 문제에 대해 반복 호출 방지)
    cache_key = (len(chat_history), last_correct_idx)
    if st.session_state.get("solution_review_cache_key") == cache_key:
        cached = st.session_state.get("solution_review_text", "")
        if cached:
            st.markdown(cached)
            return

    client = OpenAI(api_key=api_key)

    system_prompt = f"""
    너는 학생의 사고 과정을 정리해주는 수학 과외 선생님이야.
    아래는 한 문제를 풀면서 학생과 주고받은 실제 대화 기록이야.

    [대화 기록]
    {conversation_text}

    이 기록을 바탕으로, 학생이 푼 "최근 문제 한 개"에 대해 다음 내용을 마크다운으로 정리해줘.

    출력 형식(반드시 지켜줘):

    ### 🧮 최근 푼 문제 풀이 흐름
    - 1단계: ...
    - 2단계: ...
    - 3단계: ...
    (필요하다면 4~5단계까지, 핵심 과정만 간단히 요약)

    ### ✨ 잘한 점
    - 학생이 스스로 잘 해낸 점 2~3가지

    ### 🔍 더 연습하면 좋을 점
    - 개념 이해나 풀이 습관 측면에서 보완하면 좋을 점 2~3가지

    추가 규칙:
    - 정답이 맞았다는 가정하에, 굳이 최종 '숫자 답'을 다시 적지 않아도 돼.
    - 학생이 어떤 생각을 통해 정답에 도달했는지 "흐름"을 중심으로 정리해줘.
    - 말투는 한국어, 부드럽고 응원하는 톤으로.
    - 너무 긴 이론 강의 대신, 이 문제를 풀면서 드러난 특징 위주로 이야기해줘.
    """

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "위 형식에 맞춰서 풀이 흐름과 피드백을 정리해줘."}
            ],
            temperature=0.7,
            max_tokens=500
        )
        review_text = resp.choices[0].message.content.strip()
    except Exception as e:
        st.warning(f"풀이 리뷰 생성 중 오류가 발생했어요: {e}")
        return

    # 캐시에 저장
    st.session_state.solution_review_cache_key = cache_key
    st.session_state.solution_review_text = review_text

    st.markdown(review_text)
