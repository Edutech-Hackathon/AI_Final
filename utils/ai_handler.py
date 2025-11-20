import os
import base64
from openai import OpenAI
import streamlit as st
from utils.prompt_manager import PromptManager

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

def get_ai_response(user_input, hint_level, persona, problem_image=None, solution_image=None, chat_history=None):
    """OpenAI API를 통해 답변 생성"""
    
    # 1. API 키 확인
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "⚠️ OpenAI API 키가 설정되지 않았습니다.", False

    client = OpenAI(api_key=api_key)
    prompt_manager = PromptManager()
    
    # 요청 타입 확인
    request_type = st.session_state.get('request_type', None)

    # 2. 시스템 프롬프트 구성
    if request_type == "check_answer":
        # 정답 확인용 프롬프트 사용
        system_prompt = prompt_manager.get_answer_check_prompt()
        st.session_state.request_type = None  # 요청 처리 후 초기화
    elif request_type == "solution_check":
        # 풀이 확인용 프롬프트 사용
        system_prompt = prompt_manager.get_solution_check_prompt_with_image()
        st.session_state.request_type = None
    else:
        # 일반 힌트 프롬프트 사용
        context = {
            'chat_history': chat_history if chat_history else [],
            'student_name': st.session_state.get('user_name', '학생'),
            'grade': st.session_state.get('grade', '중학생')
        }
        system_prompt = prompt_manager.get_prompt(
            persona=persona, 
            hint_level=hint_level, 
            context=context
        )

    messages = [{"role": "system", "content": system_prompt}]

    # 이전 대화 기록 (정답/풀이 확인 모드가 아닐 때만)
    if chat_history and request_type not in ["check_answer", "solution_check"]:
        recent_history = chat_history[-4:]
        for role, content, _ in recent_history:
            messages.append({"role": role, "content": content})

    # 3. 사용자 내용 구성 (텍스트 + 이미지)
    user_content = []
    
    if user_input:
        user_content.append({"type": "text", "text": user_input})
    else:
        user_content.append({"type": "text", "text": f"현재 {hint_level}단계 힌트를 주세요."})

    # 문제 이미지 추가
    if problem_image:
        b64_prob = encode_image_to_base64(problem_image)
        if b64_prob:
            user_content.append({"type": "text", "text": "[문제 이미지]"})
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_prob}", "detail": "high"}
            })
            
    # 풀이 이미지 추가
    if solution_image:
        b64_sol = encode_image_to_base64(solution_image)
        if b64_sol:
            user_content.append({"type": "text", "text": "[학생 풀이 이미지]"})
            user_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{b64_sol}", "detail": "high"}
            })

    messages.append({"role": "user", "content": user_content})

    # 4. API 호출
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        response_text = response.choices[0].message.content
        
        # 정답 확인 여부 체크
        is_correct = False
        if "[[CORRECT]]" in response_text:
            is_correct = True
            response_text = response_text.replace("[[CORRECT]]", "").strip()
            
            # 정답 처리
            st.session_state.solved_problems = st.session_state.get('solved_problems', 0) + 1
            
            # 분석 데이터 업데이트
            from utils.session_manager import SessionManager
            session_manager = SessionManager()
            session_manager.update_analytics('problem_solved', {
                'problem_id': st.session_state.get('current_problem_id', None),
                'hints_used': st.session_state.get('hint_level', 0)
            })
            
        elif "[[INCORRECT]]" in response_text:
            response_text = response_text.replace("[[INCORRECT]]", "").strip()
        
        return response_text, is_correct
        
    except Exception as e:
        return f"오류 발생: {str(e)}", False
