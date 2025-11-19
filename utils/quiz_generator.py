# Quiz 생성 모듈

import openai
import json
import random
from typing import Dict, List, Optional
from config import OPENAI_API_KEY, MODEL_NAME, TEMPERATURE
from .prompts import PromptTemplates

class QuizGenerator:
    """퀴즈 생성 및 평가를 담당하는 클래스"""
    
    def __init__(self):
        """OpenAI 클라이언트 초기화"""
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
        self.prompt_templates = PromptTemplates()
        
    def generate_quiz(self, text: str, summary: str, quiz_type: str, count: int = 5) -> Dict:
        """
        텍스트와 요약을 바탕으로 퀴즈 생성
        
        Args:
            text: 원본 텍스트
            summary: 요약된 텍스트
            quiz_type: 퀴즈 유형 (OX, 객관식, 빈칸)
            count: 문제 개수
            
        Returns:
            퀴즈 데이터 딕셔너리
        """
        try:
            prompt = self.prompt_templates.get_quiz_prompt(text, summary, quiz_type, count)
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 교육 평가 전문가입니다. JSON 형식으로만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            # JSON 파싱
            content = response.choices[0].message.content
            # JSON 블록만 추출 (```json ... ``` 제거)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            quiz_data = json.loads(content.strip())
            quiz_data["quiz_type"] = quiz_type
            
            return quiz_data
            
        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 기본 구조 반환
            return self._create_fallback_quiz(quiz_type, count)
        except Exception as e:
            return {"error": f"퀴즈 생성 중 오류 발생: {str(e)}"}
    
    def _create_fallback_quiz(self, quiz_type: str, count: int) -> Dict:
        """
        API 오류 시 사용할 기본 퀴즈 구조
        
        Args:
            quiz_type: 퀴즈 유형
            count: 문제 개수
            
        Returns:
            기본 퀴즈 구조
        """
        if quiz_type == "OX 퀴즈":
            questions = [
                {
                    "id": i + 1,
                    "question": f"본문의 내용과 일치합니까? (문제 {i + 1})",
                    "answer": random.choice(["O", "X"]),
                    "explanation": "본문을 다시 읽어보세요."
                }
                for i in range(count)
            ]
        elif quiz_type == "객관식 퀴즈":
            questions = [
                {
                    "id": i + 1,
                    "question": f"다음 중 올바른 것은? (문제 {i + 1})",
                    "options": ["선택지 1", "선택지 2", "선택지 3", "선택지 4"],
                    "answer": random.randint(0, 3),
                    "explanation": "본문을 다시 읽어보세요."
                }
                for i in range(count)
            ]
        else:  # 빈칸 채우기
            questions = [
                {
                    "id": i + 1,
                    "question": f"다음 빈칸에 들어갈 말은? _____ (문제 {i + 1})",
                    "answer": "정답",
                    "explanation": "본문을 다시 읽어보세요."
                }
                for i in range(count)
            ]
            
        return {
            "quiz_type": quiz_type,
            "questions": questions
        }
    
    def evaluate_answers(self, quiz_data: Dict, user_answers: List) -> Dict:
        """
        사용자 답변 평가
        
        Args:
            quiz_data: 퀴즈 데이터
            user_answers: 사용자 답변 리스트
            
        Returns:
            평가 결과
        """
        results = {
            "total": len(quiz_data["questions"]),
            "correct": 0,
            "incorrect": 0,
            "details": []
        }
        
        for i, question in enumerate(quiz_data["questions"]):
            user_answer = user_answers[i] if i < len(user_answers) else None
            
            if quiz_data["quiz_type"] == "OX 퀴즈":
                is_correct = user_answer == question["answer"]
            elif quiz_data["quiz_type"] == "객관식 퀴즈":
                is_correct = user_answer == question["answer"]
            else:  # 빈칸 채우기
                # 대소문자 구분 없이, 공백 제거 후 비교
                if user_answer and question["answer"]:
                    is_correct = (user_answer.strip().lower() == 
                                question["answer"].strip().lower())
                else:
                    is_correct = False
            
            if is_correct:
                results["correct"] += 1
            else:
                results["incorrect"] += 1
                
            results["details"].append({
                "question_id": question["id"],
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": question["answer"],
                "is_correct": is_correct,
                "explanation": question["explanation"]
            })
        
        results["percentage"] = round((results["correct"] / results["total"]) * 100, 1)
        
        return results
    
    def generate_feedback(self, quiz_results: Dict) -> str:
        """
        퀴즈 결과에 대한 피드백 생성
        
        Args:
            quiz_results: 퀴즈 평가 결과
            
        Returns:
            피드백 메시지
        """
        try:
            prompt = self.prompt_templates.get_feedback_prompt(quiz_results)
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 따뜻하고 격려적인 교육 상담사입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            # 기본 피드백 제공
            percentage = quiz_results['percentage']
            if percentage >= 80:
                return f"🎉 훌륭해요! {percentage}%의 정답률을 보였어요! 계속 이렇게 잘하면 됩니다!"
            elif percentage >= 60:
                return f"👍 잘하고 있어요! {percentage}%의 정답률입니다. 조금만 더 노력하면 완벽해질 거예요!"
            else:
                return f"💪 괜찮아요! {percentage}%의 정답률이지만, 실수를 통해 배우는 거예요. 다시 도전해보세요!"
    
    def create_review_quiz(self, incorrect_questions: List[Dict]) -> Dict:
        """
        틀린 문제를 바탕으로 복습 퀴즈 생성
        
        Args:
            incorrect_questions: 틀린 문제 목록
            
        Returns:
            복습 퀴즈
        """
        try:
            questions_text = json.dumps(incorrect_questions, ensure_ascii=False, indent=2)
            
            prompt = f"""
다음은 학생이 틀린 문제들입니다. 
이 문제들과 비슷하지만 약간 다른 복습 문제를 만들어주세요.

틀린 문제들:
{questions_text}

요구사항:
1. 같은 개념을 묻되 표현을 바꿔서
2. 난이도는 약간 더 쉽게
3. 힌트를 포함해서
4. 같은 형식으로 (OX, 객관식, 빈칸)

JSON 형식으로 응답하세요:
{{
    "questions": [
        {{
            "id": 번호,
            "question": "문제",
            "answer": "정답",
            "hint": "힌트",
            "explanation": "설명"
        }}
    ]
}}
"""
            
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "당신은 복습 문제를 만드는 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.6
            )
            
            content = response.choices[0].message.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
                
            return json.loads(content.strip())
            
        except Exception as e:
            return {"questions": [], "error": str(e)}
    
    def generate_adaptive_quiz(self, text: str, summary: str, 
                             previous_results: Optional[Dict] = None) -> Dict:
        """
        이전 결과를 바탕으로 난이도가 조절되는 적응형 퀴즈 생성
        
        Args:
            text: 원본 텍스트
            summary: 요약 텍스트
            previous_results: 이전 퀴즈 결과
            
        Returns:
            적응형 퀴즈
        """
        # 이전 결과에 따른 난이도 조정
        if previous_results:
            percentage = previous_results.get('percentage', 50)
            if percentage >= 80:
                difficulty = "더 어려운"
                quiz_type = "객관식 퀴즈"  # 더 어려운 유형
            elif percentage >= 60:
                difficulty = "비슷한 난이도의"
                quiz_type = "OX 퀴즈"
            else:
                difficulty = "더 쉬운"
                quiz_type = "OX 퀴즈"  # 더 쉬운 유형
        else:
            difficulty = "중간 난이도의"
            quiz_type = "OX 퀴즈"
        
        # 적응형 퀴즈 생성
        try:
            prompt = f"""
{difficulty} 문제 5개를 만들어주세요.

원본 텍스트:
{text}

요약:
{summary}

퀴즈 유형: {quiz_type}

JSON 형식으로 응답하세요.
"""
            
            return self.generate_quiz(text, summary, quiz_type, 5)
            
        except Exception as e:
            return {"error": str(e)}
