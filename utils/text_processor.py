# Text생성 & 요약 모듈

import openai
import json
from typing import Dict, Optional
from config import OPENAI_API_KEY, MODEL_NAME, MAX_TOKENS, TEMPERATURE
from .prompts import PromptTemplates

class TextProcessor:
    """텍스트 처리 및 요약을 담당하는 클래스"""
    
    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.prompt_templates = PromptTemplates()
        
    def summarize_text(self, text: str, level_info: Dict) -> str:
        """
        주어진 텍스트를 선택된 난이도에 맞게 요약
        
        Args:
            text: 요약할 원본 텍스트
            level_info: 난이도 정보 딕셔너리
            
        Returns:
            요약된 텍스트
        """
        try:
            prompt = self.prompt_templates.get_summary_prompt(text, level_info)
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 학생들의 문해력 향상을 돕는 친절한 선생님입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"요약 생성 중 오류가 발생했습니다: {str(e)}"
    
    def extract_keywords(self, text: str) -> list:
        """
        텍스트에서 핵심 키워드 추출
        
        Args:
            text: 키워드를 추출할 텍스트
            
        Returns:
            키워드 리스트
        """
        try:
            prompt = f"""
다음 텍스트에서 가장 중요한 키워드 5개를 추출해주세요.
각 키워드에 대해 초등학생도 이해할 수 있는 짧은 설명을 추가하세요.

텍스트:
{text}

JSON 형식으로 응답하세요:
{{
    "keywords": [
        {{
            "word": "키워드",
            "explanation": "쉬운 설명"
        }}
    ]
}}
"""
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 텍스트 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("keywords", [])
            
        except Exception as e:
            return []
    
    def analyze_difficulty(self, text: str) -> Dict:
        """
        텍스트의 난이도 분석
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            난이도 분석 결과
        """
        try:
            prompt = f"""
다음 텍스트의 난이도를 분석해주세요.

텍스트:
{text[:1000]}...

분석 항목:
1. 전반적인 난이도 (초등저/초등고/중등/고등/대학)
2. 어려운 단어 개수
3. 평균 문장 길이
4. 전문용어 포함 여부

JSON 형식으로 응답하세요:
{{
    "difficulty_level": "난이도",
    "difficult_words_count": 숫자,
    "avg_sentence_length": "짧음/보통/긴편",
    "has_technical_terms": true/false,
    "recommendation": "추천 학습 수준"
}}
"""
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 텍스트 난이도 분석 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            return {
                "difficulty_level": "분석 실패",
                "difficult_words_count": 0,
                "avg_sentence_length": "알 수 없음",
                "has_technical_terms": False,
                "recommendation": "수동으로 난이도를 선택해주세요"
            }
    
    def explain_difficult_part(self, text: str, difficult_part: str) -> str:
        """
        텍스트의 어려운 부분을 추가로 설명
        
        Args:
            text: 전체 텍스트
            difficult_part: 어려운 부분
            
        Returns:
            추가 설명
        """
        try:
            prompt = self.prompt_templates.get_explanation_prompt(text, difficult_part)
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 복잡한 개념을 쉽게 설명하는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"추가 설명 생성 중 오류가 발생했습니다: {str(e)}"
    
    def create_vocabulary_list(self, text: str, level: str) -> list:
        """
        텍스트에서 학습이 필요한 어휘 목록 생성
        
        Args:
            text: 텍스트
            level: 학습자 수준
            
        Returns:
            어휘 목록
        """
        try:
            prompt = f"""
{level} 수준 학습자를 위해 다음 텍스트에서 학습이 필요한 어휘 10개를 선정해주세요.
각 어휘에 대해 쉬운 설명과 예문을 제공하세요.

텍스트:
{text[:1500]}

JSON 형식으로 응답하세요:
{{
    "vocabulary": [
        {{
            "word": "단어",
            "meaning": "쉬운 뜻 설명",
            "example": "예문",
            "synonym": "비슷한 말"
        }}
    ]
}}
"""
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 어휘 학습 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.5
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("vocabulary", [])
            
        except Exception as e:
            return []
