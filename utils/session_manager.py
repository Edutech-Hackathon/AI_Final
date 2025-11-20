import streamlit as st
import json
from datetime import datetime
import os

class SessionManager:
    """세션 상태 관리 클래스"""
    
    def __init__(self):
        self.session_file = "data/session_data.json"
        self.initialize_session()
    
    def initialize_session(self):
        """세션 초기화"""
        if 'initialized' not in st.session_state:
            st.session_state.initialized = True
            self.load_session_data()
    
    def save_session_data(self):
        """세션 데이터 저장"""
        try:
            session_data = {
                'user_name': st.session_state.get('user_name', '학생'),
                'grade': st.session_state.get('grade', '중학생'),
                'selected_persona': st.session_state.get('selected_persona', 'friendly'),
                'chat_history': st.session_state.get('chat_history', []),
                'analytics_data': st.session_state.get('analytics_data', {}),
                'total_problems': st.session_state.get('total_problems', 0),
                'solved_problems': st.session_state.get('solved_problems', 0),
                'last_saved': datetime.now().isoformat()
            }
            
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            st.error(f"세션 저장 실패: {str(e)}")
            return False
    
    def load_session_data(self):
        """세션 데이터 로드"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                for key, value in session_data.items():
                    if key != 'last_saved':
                        st.session_state[key] = value
                return True
            return False
        except Exception as e:
            st.error(f"세션 로드 실패: {str(e)}")
            return False
    
    def update_analytics(self, event_type, data=None):
        """분석 데이터 업데이트 (시간 관련 로직 제거)"""
        if 'analytics_data' not in st.session_state:
            st.session_state.analytics_data = {
                'total_hints': 0,
                'hint_distribution': [0, 0, 0],
                'problem_types': {},
                'last_study_date': None,
                'events': []
            }
        
        analytics = st.session_state.analytics_data
        
        # 이벤트 기록
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        if 'events' not in analytics:
            analytics['events'] = []
        analytics['events'].append(event)
        
        # 이벤트 타입별 처리
        if event_type == 'hint_used':
            analytics['total_hints'] += 1
            if data and 'level' in data:
                level = data['level'] - 1
                if 0 <= level < 3:
                    analytics['hint_distribution'][level] += 1
        
        elif event_type == 'problem_solved':
            st.session_state.solved_problems = st.session_state.get('solved_problems', 0) + 1
        
        elif event_type == 'problem_started':
            st.session_state.total_problems = st.session_state.get('total_problems', 0) + 1
        
        analytics['last_study_date'] = datetime.now().isoformat()
        
        if st.session_state.get('settings', {}).get('auto_save', True):
            self.save_session_data()
    
    def get_study_statistics(self):
        """학습 통계 반환"""
        analytics = st.session_state.get('analytics_data', {})
        
        stats = {
            'total_hints': analytics.get('total_hints', 0),
            'average_hint_level': self._calculate_average_hint_level(),
            'solve_rate': self._calculate_solve_rate(),
            'last_study': analytics.get('last_study_date', None)
        }
        
        return stats
    
    def _calculate_average_hint_level(self):
        distribution = st.session_state.get('analytics_data', {}).get('hint_distribution', [0, 0, 0])
        total = sum(distribution)
        if total == 0: return 0
        weighted_sum = sum((i + 1) * count for i, count in enumerate(distribution))
        return round(weighted_sum / total, 2)
    
    def _calculate_solve_rate(self):
        total = st.session_state.get('total_problems', 0)
        solved = st.session_state.get('solved_problems', 0)
        if total == 0: return 0
        return round(solved / total * 100, 1)
