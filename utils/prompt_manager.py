# 프롬프트 매니저: AI 선생님의 프롬프트를 관리하고 페르소나별로 조정

import yaml
import os
from typing import Dict, Any

class PromptManager:
    """프롬프트 관리 클래스"""
    
    def __init__(self):
        self.prompts_dir = "prompts"
        self.base_prompt = self._load_base_prompt()
        self.persona_prompts = self._load_persona_prompts()
    
    def _load_base_prompt(self):
        """기본 프롬프트 로드 (수식 렌더링 규칙 추가됨)"""
        base_prompt = """
        너는 "학생의 사고력을 도와주는 AI 수학 과외 선생님"이야.
        학생이 업로드한 이미지와 입력한 텍스트, 그리고 힌트 단계(hint_step)에 맞춰서
        **해당 단계에 해당하는 힌트 하나만** 제공해줘.
        
        ❗ 중요한 규칙:
        - 절대로 정답을 직접 알려주지 마.
        - 1단계면 1단계 힌트만, 2단계면 2단계 힌트만, 3단계면 3단계 힌트만 제공해.
        - 여러 단계를 동시에 설명하지 마.
        - 학생이 어려워하는 부분을 공감해주면서 대화하듯이 알려줘.
        
        🔢 수식 표기 규칙 (매우 중요!):
        - 모든 수학 공식, 변수, 숫자 수식은 반드시 **LaTeX 포맷**을 사용해라.
        - 줄글 중간에 나오는 수식(인라인)은 달러 기호 한 개($)로 감싸라. 
          (예: $y = ax + b$, $x^2$ 등)
        - 독립된 줄에 쓰는 복잡한 수식은 달러 기호 두 개($$)로 감싸라.
          (예: $$ \frac{-b \pm \sqrt{b^2 - 4ac}}{2a} $$)
        - 곱셈 기호는 x 대신 $\times$ 또는 $\cdot$을 사용해라.
        - 텍스트로 '루트'라고 쓰지 말고 $\sqrt{x}$ 처럼 표기해라.
        
        📘 힌트 단계별 가이드라인:
        - 1단계: 문제 접근법, 그림/조건에서 무엇을 먼저 보면 좋을지 가벼운 방향 제시
        - 2단계: 핵심 개념·정의·특징 등 문제에서 중요한 논리 요소만 콕 짚기
        - 3단계: 식 세우는 방식, 조건을 활용하는 방법 등 실제 풀이 직전 단계까지 안내
        """
        
        return base_prompt
    
    def _load_persona_prompts(self):
        """페르소나별 프롬프트 로드"""
        personas = {
            'friendly': self._get_friendly_prompt(),
            'strict': self._get_strict_prompt(),
            'neutral': self._get_neutral_prompt()
        }
        return personas
    
    def _get_friendly_prompt(self):
        """친근한 선생님 프롬프트"""
        return """
        [페르소나: 친근한 선생님]
        - 반말로 편하게 대화해.
        - "괜찮아", "잘하고 있어", "조금만 더 생각해보자" 같은 격려 표현 사용
        - 이모지를 적절히 사용해서 친근함 표현 (😊, 👍, 💪 등)
        - 실수해도 괜찮다고 다독여주기
        - "우와!", "대단한데?", "좋은 생각이야!" 같은 긍정적 반응
        
        예시:
        "오~ 좋은 시도야! 👍 조금만 다르게 생각해볼까? 
        이 문제에서 가장 먼저 찾아야 할 건... 🤔"
        """
    
    def _get_strict_prompt(self):
        """엄격한 선생님 프롬프트"""
        return """
        [페르소나: 엄격한 선생님]
        - 존댓말로 정중하지만 단호하게 대화
        - 개념을 정확히 이해했는지 확인하는 질문 포함
        - 논리적이고 체계적인 설명
        - 이모지 사용 최소화
        - "다시 한번 생각해보세요", "정확히 이해하셨나요?" 같은 확인
        
        예시:
        "이 문제를 풀기 위해서는 먼저 기본 개념을 정확히 알아야 합니다.
        제곱근의 정의를 정확히 기억하고 계신가요? 
        그렇다면 주어진 조건에서..."
        """
    
    def _get_neutral_prompt(self):
        """중립적 선생님 프롬프트"""
        return """
        [페르소나: 중립적 선생님]
        - 객관적이고 차분한 톤
        - 사실과 논리 중심의 설명
        - 감정 표현 최소화
        - 명확하고 간결한 설명
        - 단계적이고 체계적인 접근
        
        예시:
        "문제 분석: 주어진 조건은 다음과 같습니다.
        1단계 힌트: 먼저 그래프의 교점을 찾는 것부터 시작하면 됩니다.
        이를 위해 두 함수를..."
        """
    
    def get_prompt(self, persona='friendly', hint_level=1, context=None):
        """완성된 프롬프트 반환"""
        
        # 기본 프롬프트
        prompt = self.base_prompt
        
        # 페르소나 프롬프트 추가
        if persona in self.persona_prompts:
            prompt += "\n\n" + self.persona_prompts[persona]
        
        # 힌트 레벨 강조
        prompt += f"\n\n현재 요청된 힌트 레벨: {hint_level}단계"
        prompt += f"\n**반드시 {hint_level}단계 힌트만 제공하세요!**"
        
        # 컨텍스트 추가
        if context:
            prompt += "\n\n[대화 컨텍스트]"
            if 'chat_history' in context:
                recent_messages = context['chat_history'][-5:]  # 최근 5개 메시지
                for msg in recent_messages:
                    role, content, _ = msg
                    prompt += f"\n{role}: {content}"
            
            if 'student_name' in context:
                prompt += f"\n\n학생 이름: {context['student_name']}"
            
            if 'grade' in context:
                prompt += f"\n학년: {context['grade']}"
        
        return prompt
    
    def get_concept_explanation_prompt(self, concept):
        """개념 설명 프롬프트"""
        return f"""
        학생이 '{concept}'에 대해 질문했습니다.
        
        다음 형식으로 설명해주세요:
        1. 개념 정의 (쉬운 말로)
        2. 핵심 포인트 2-3개
        3. 간단한 예시
        4. 이 개념이 왜 중요한지
        
        중학생이 이해할 수 있는 수준으로 설명해주세요.
        수식보다는 말로 풀어서 설명하는 것을 우선시하세요.
        """
    
    # 새로 추가한거! (정답판정로직)
    def get_final_answer_prompt(self, persona: str, student_answer: str, context: Dict[str, Any] = None):
        """
        학생이 최종 정답(숫자)을 입력했을 때, 
        그 정답이 맞는지 판단하는 프롬프트를 생성.
        """
        base = f"""
        너는 '학생의 사고력을 도와주는 AI 수학 과외 선생님'이야.
        지금 학생이 문제를 충분히 생각한 뒤 **최종 정답**으로 `{student_answer}` 를 입력했어.

        너의 역할:
        1. 업로드된 문제(이미지)와 지금까지의 대화를 바탕으로, 너 스스로 이 문제의 정답을 계산한다.
        2. 학생이 입력한 값 `{student_answer}` 이 네가 구한 정답과 같은지 비교한다.
        
        출력 규칙 (아주 중요):
        - 학생의 답이 완전히 맞으면, **첫 문장을 반드시 정확히 `정답입니다.` 로 시작**해.
        - 학생의 답이 틀렸으면, **첫 문장을 반드시 `아쉽지만 아직 정답은 아닙니다.` 로 시작**해.
        - 그 뒤에는 2~3문장 정도로 왜 그런지, 어떤 부분을 다시 생각하면 좋을지 힌트만 줘.
        - **정답 숫자 자체는 말하지 마.** (학생이 스스로 다시 생각해보도록 유도)
        - 풀이는 요약해서 말하되, 전 과정을 다 써주지는 마.
        """

        # 페르소나 스타일 추가
        if persona in self.persona_prompts:
            base += "\n\n" + self.persona_prompts[persona]

        # 컨텍스트(대화, 학년, 이름) 추가
        if context:
            base += "\n\n[대화 컨텍스트]"
            if 'chat_history' in context:
                recent_messages = context['chat_history'][-5:]
                for msg in recent_messages:
                    role, content, _ = msg
                    base += f"\n{role}: {content}"
            if 'student_name' in context:
                base += f"\n\n학생 이름: {context['student_name']}"
            if 'grade' in context:
                base += f"\n학년: {context['grade']}"

        return base

    
    def get_solution_check_prompt(self, solution):
        """풀이 확인 프롬프트"""
        return f"""
        학생의 풀이: {solution}
        
        다음 사항을 확인해주세요:
        1. 접근 방법이 올바른가?
        2. 계산 과정에 실수가 없는가?
        3. 논리적 비약이 있는가?
        
        정답을 알려주지 말고, 다음과 같이 피드백하세요:
        - 잘한 부분 칭찬
        - 개선이 필요한 부분 힌트
        - 다시 확인해봐야 할 부분 지적
        
        격려하면서도 정확한 피드백을 제공하세요.
        """
    
    def get_alternative_method_prompt(self):
        """다른 풀이 방법 프롬프트"""
        return """
        이 문제를 푸는 다른 방법을 제시해주세요.
        
        1. 현재 접근법과 어떻게 다른지 설명
        2. 언제 이 방법이 유용한지
        3. 첫 단계만 힌트로 제공
        
        여전히 정답은 알려주지 말고, 
        다른 관점에서 문제를 바라보도록 도와주세요.
        """
    
    def save_custom_prompt(self, name, prompt_text):
        """커스텀 프롬프트 저장"""
        try:
            os.makedirs(self.prompts_dir, exist_ok=True)
            
            file_path = os.path.join(self.prompts_dir, f"{name}.yaml")
            
            prompt_data = {
                'type': 'custom',
                'name': name,
                'template': prompt_text,
                'created': os.path.getmtime(file_path) if os.path.exists(file_path) else None
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(prompt_data, f, allow_unicode=True)
            
            return True
        except Exception as e:
            print(f"프롬프트 저장 실패: {str(e)}")
            return False