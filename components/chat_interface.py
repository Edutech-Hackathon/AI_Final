# 채팅 인터페이스 컴포넌트: 학생과 AI 선생님 간의 대화를 관리하고 표시

import streamlit as st
from datetime import datetime
import base64

class ChatInterface:
    """채팅 인터페이스 클래스"""
    
    def __init__(self):
        self.messages = []
        self.current_context = None
    
    def add_message(self, role, content, timestamp=None):
        """메시지 추가"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M")
        
        self.messages.append({
            'role': role,
            'content': content,
            'timestamp': timestamp
        })
    
    def clear_messages(self):
        """메시지 초기화"""
        self.messages = []
    
    def get_conversation_context(self):
        """대화 컨텍스트 반환"""
        return self.messages
    
    def format_message_for_display(self, message):
        """메시지를 표시용으로 포맷팅"""
        role = message['role']
        content = message['content']
        timestamp = message['timestamp']
        
        if role == 'user':
            return self._format_user_message(content, timestamp)
        else:
            return self._format_assistant_message(content, timestamp)
    
    def _format_user_message(self, content, timestamp):
        """사용자 메시지 포맷팅"""
        return f"""
        <div class='user-message'>
            <strong>👦 {st.session_state.get('user_name', '학생')}</strong>
            <span style='float: right; color: #718096;'>{timestamp}</span>
            <p>{content}</p>
        </div>
        """
    
    def _format_assistant_message(self, content, timestamp):
        """AI 선생님 메시지 포맷팅"""
        persona_emoji = self._get_persona_emoji()
        persona_name = self._get_persona_name()
        
        return f"""
        <div class='ai-message'>
            <strong>{persona_emoji} {persona_name} 선생님</strong>
            <span style='float: right; color: #718096;'>{timestamp}</span>
            <p>{content}</p>
        </div>
        """
    
    def _get_persona_emoji(self):
        """현재 페르소나의 이모지 반환"""
        personas = {
            'friendly': '😊',
            'strict': '🧐',
            'neutral': '🤖'
        }
        return personas.get(st.session_state.get('selected_persona', 'friendly'), '👨‍🏫')
    
    def _get_persona_name(self):
        """현재 페르소나의 이름 반환"""
        personas = {
            'friendly': '친근한',
            'strict': '엄격한',
            'neutral': '중립적'
        }
        return personas.get(st.session_state.get('selected_persona', 'friendly'), 'AI')
    
    def render_chat_history(self):
        """채팅 히스토리 렌더링"""
        for message in self.messages:
            formatted = self.format_message_for_display(message)
            st.markdown(formatted, unsafe_allow_html=True)
    
    def export_chat_history(self):
        """채팅 히스토리 내보내기"""
        export_data = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'student_name': st.session_state.get('user_name', '학생'),
            'messages': self.messages,
            'statistics': {
                'total_messages': len(self.messages),
                'hints_used': st.session_state.analytics_data.get('total_hints', 0)
            }
        }
        return export_data
    
    def save_to_history(self):
        """대화를 히스토리에 저장"""
        # 실제 구현시에는 데이터베이스나 파일에 저장
        pass
