import os
import base64
from openai import OpenAI
import streamlit as st
from .prompt_manager import PromptManager

def encode_image_to_base64(image_file):
    """이미지 파일을 base64 문자열로 변환"""
    if image_file is None:
        return None
    try:
        # 파일 포인터를 처음으로 되돌림
        image_file.seek(0)
        return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"이미지 변환 실패: {e}")
        return None

def get_ai_response(user_input, hint_level, persona, uploaded_image=None, chat_history=None):
    """OpenAI API를 통해 답변 생성"""
    
    # 1. API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."

    client = OpenAI(api_key=api_key)
    prompt_manager = PromptManager()

    # 2. 시스템 프롬프트 구성 (페르소나 + 힌트 단계)
    context = {
        'chat_history': chat_history if chat_history else [],
        'student_name': st.session_state.get('user_name', '학생'),
        'grade': st.session_state.get('grade', '중학교 3학년')
    }
    
    system_prompt = prompt_manager.get_prompt(
        persona=persona, 
        hint_level=hint_level, 
        context=context
    )

    # 3. 메시지 구성
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # 이전 대화 기록 추가 (최근 4개만 - 토큰 절약)
    if chat_history:
        recent_history = chat_history[-4:]
        for role, content, _ in recent_history:
            # user와 assistant 역할만 추가 (timestamp 제외)
            messages.append({"role": role, "content": content})

    # 4. 현재 사용자 입력 구성 (텍스트 + 이미지)
    user_content = []
    
    # 텍스트 추가
    if user_input:
        user_content.append({"type": "text", "text": user_input})
    else:
        # 입력 없이 힌트 버튼만 누른 경우
        user_content.append({"type": "text", "text": f"현재 {hint_level}단계 힌트를 주세요."})

    # 이미지 추가
    if uploaded_image:
        base64_image = encode_image_to_base64(uploaded_image)
        if base64_image:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": "high" # 이미지 상세 분석 모드
                }
            })

    messages.append({"role": "user", "content": user_content})

    # 5. API 호출
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"죄송합니다. 답변을 생성하는 중에 오류가 발생했습니다.\n오류 내용: {str(e)}"