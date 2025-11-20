# components/teacher_selection.py

import streamlit as st

def render_teacher_selection():
    """선생님 페르소나 선택 UI"""

    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 1rem; border-radius: 15px; margin: 1rem 0;'>
        <h3 style='margin: 0;'>👨‍🏫 선생님 스타일 선택</h3>
    </div>
    """, unsafe_allow_html=True)

    # 페르소나 옵션
    personas = {
        'friendly': {
            'title': "학원계의 힐링 전도사",
            'description': "따뜻하게 격려하며 자신감을 키워주는 스타일. 실수해도 괜찮다고 다독여주며 긍정적인 피드백을 많이 제공합니다.",
            'color': "#48bb78",
            'image': "https://cdn-icons-png.flaticon.com/512/2922/2922510.png"
        },
        'strict': {
            'title': "대치동 호랭이 강사",
            'description': "체계적이고 정확한 학습을 강조하는 스타일. 개념 이해 여부를 꼼꼼하게 체크하며 논리적 사고를 중시합니다.",
            'color': "#f6ad55",
            'image': "https://cdn-icons-png.flaticon.com/512/2922/2922688.png"
        },
        'neutral': {
            'title': "인간AI",
            'description': "객관적이고 차분하게 설명하는 스타일. 감정 개입 없이 사실과 논리에 기반해 풀이 방향을 안내합니다.",
            'color': "#667eea",
            'image': "https://cdn-icons-png.flaticon.com/512/2922/2922656.png"
        },
    }

    # 현재 선택된 값 (기본값 friendly)
    current = st.session_state.get("selected_persona", "friendly")

    # 가로로 3개 카드 배치
    cols = st.columns(3)

    for idx, (key, info) in enumerate(personas.items()):
        with cols[idx]:
            is_selected = (current == key)

            # 카드 UI
            st.markdown(f"""
            <div style="
                border-radius: 12px;
                border: 2px solid {'#00000010' if not is_selected else info['color']};
                padding: 1rem;
                text-align: center;
                background: {'#ffffff' if not is_selected else info['color']+'15'};
                box-shadow: 0 4px 8px rgba(0,0,0,0.05);
            ">
                <img src="{info['image']}" width="90" style="margin-bottom:10px; border-radius: 50%;">
                <h4 style="margin: 0; padding: 0; font-weight: 600;">{info['title']}</h4>
                <p style="font-size: 0.9rem; color: #4a5568;">{info['description']}</p>
            </div>
            """, unsafe_allow_html=True)

            # 선택 버튼
            if st.button(f"{info['title']} 선택", key=f"select_{key}", use_container_width=True):
                st.session_state.selected_persona = key
                st.rerun()

    # 선택된 선생님 정보 표시 (하단)
    selected = st.session_state.get("selected_persona", "friendly")
    selected_info = personas[selected]

    st.markdown(f"""
    <div style='background: {selected_info['color']}20;
                border-left: 4px solid {selected_info['color']};
                padding: 1rem;
                border-radius: 8px;
                margin-top: 1.5rem;'>
        <p style='margin: 0; font-weight: 500; color: #2d3748;'>
            현재 선택된 선생님: <b>{selected_info['title']}</b><br>
            {selected_info['description']}
        </p>
    </div>
    """, unsafe_allow_html=True)
