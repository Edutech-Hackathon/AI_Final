import os
import base64
from openai import OpenAI
import streamlit as st
from utils.prompt_manager import PromptManager

def encode_image_to_base64(image_file):
    try:
        return base64.b64encode(image_file.getvalue()).decode('utf-8')
    except Exception:
        return None

def get_ai_response(user_input, hint_level, persona, uploaded_image=None, chat_history=None, mode: str = "hint"):
    """
    OpenAI API를 통해 답변 생성
    mode: "hint" (기본) / "answer" (최종 정답 판정)
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다. .env 파일을 확인해주세요."

    client = OpenAI(api_key=api_key)
    prompt_manager = PromptManager()

    # 공통 컨텍스트
    context = {
        'chat_history': chat_history if chat_history else [],
        'student_name': st.session_state.get('user_name', '학생'),
        'grade': st.session_state.get('grade', '중학생')
    }

    # 시스템 프롬프트 선택
    if mode == "answer":
        system_prompt = prompt_manager.get_final_answer_prompt(
            persona=persona,
            student_answer=user_input or "",
            context=context
        )
    else:
        system_prompt = prompt_manager.get_prompt(
            persona=persona,
            hint_level=hint_level,
            context=context
        )

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # 최근 대화 4개만
    if chat_history:
        recent_history = chat_history[-4:]
        for role, content, _ in recent_history:
            messages.append({"role": role, "content": content})

    # 현재 사용자 입력(텍스트+이미지)
    user_content = []
    if user_input:
        user_content.append({"type": "text", "text": user_input})

    if uploaded_image is not None:
        img_base64 = encode_image_to_base64(uploaded_image)
        if img_base64:
            user_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{img_base64}"
                }
            })

    if user_content:
        messages.append({"role": "user", "content": user_content})

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
