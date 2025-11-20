# 선생님 선택 컴포넌트

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
        '친근한 선생님 😊': {
            'key': 'friendly',
            'description': '따뜻하게 격려하며 자신감을 심어주는 선생님입니다. 실수해도 괜찮다고 다독여주고, 긍정적인 피드백을 많이 제공합니다.',
            'color': '#48bb78'
        },
        '엄격한 선생님 🧐': {
            'key': 'strict',
            'description': '체계적이고 정확한 학습을 추구하는 선생님입니다. 개념을 정확히 이해했는지 확인하고, 논리적 사고를 강조합니다.',
            'color': '#f6ad55'
        },
        '중립적 선생님 🤖': {
            'key': 'neutral',
            'description': '객관적이고 차분하게 가르치는 선생님입니다. 감정을 배제하고 사실과 논리에 기반한 설명을 제공합니다.',
            'color': '#667eea'
        }
    }
    
    # 가로로 3개 버튼 배치
    cols = st.columns(3)
    
    for idx, (name, info) in enumerate(personas.items()):
        with cols[idx]:
            # 현재 선택된 페르소나인지 확인
            is_selected = st.session_state.get('selected_persona', 'friendly') == info['key']
            
            # 버튼 스타일
            button_style = "primary" if is_selected else "secondary"
            
            if st.button(
                name,
                key=f"persona_{info['key']}",
                type=button_style,
                use_container_width=True
            ):
                st.session_state.selected_persona = info['key']
                st.success(f"{name}을(를) 선택했습니다!")
                st.rerun()
    
    # 선택된 선생님 설명 표시
    selected_persona = st.session_state.get('selected_persona', 'friendly')
    selected_info = next((info for name, info in personas.items() if info['key'] == selected_persona), None)
    
    if selected_info:
        st.markdown(f"""
        <div style='background: {selected_info['color']}20; 
                    border-left: 4px solid {selected_info['color']}; 
                    padding: 1rem; 
                    border-radius: 5px;
                    margin-top: 1rem;'>
            <p style='margin: 0; color: #2d3748;'>{selected_info['description']}</p>
        </div>
        """, unsafe_allow_html=True)
