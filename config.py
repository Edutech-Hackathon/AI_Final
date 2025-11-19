import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

APP_TITLE = "📚 문해력 향상 AI 튜터"
APP_ICON = "📚"

# Level 세팅
LEVELS = {
    "초등학생 (1-3학년)": {
        "description": "매우 쉬운 단어와 짧은 문장으로 설명",
        "grade": "elementary_low",
        "vocabulary": "기초 어휘 중심",
        "sentence_length": "짧고 간단한 문장"
    },
    "초등학생 (4-6학년)": {
        "description": "일상적인 단어와 쉬운 비유로 설명",
        "grade": "elementary_high",
        "vocabulary": "일상 어휘 중심",
        "sentence_length": "중간 길이 문장"
    },
    "중학생": {
        "description": "교과서 수준의 어휘와 구체적인 예시로 설명",
        "grade": "middle",
        "vocabulary": "교과서 수준 어휘",
        "sentence_length": "복문 포함"
    },
    "고등학생": {
        "description": "학술적 어휘를 포함하되 명확하게 설명",
        "grade": "high",
        "vocabulary": "학술 어휘 포함",
        "sentence_length": "복잡한 문장 구조 가능"
    }
}

# Quiz 세팅
QUIZ_TYPES = ["OX 퀴즈", "객관식 퀴즈", "빈칸 채우기"]
DEFAULT_QUIZ_COUNT = 5
MAX_QUIZ_COUNT = 10

# UI 세팅
SIDEBAR_WIDTH = 300
TEXT_INPUT_HEIGHT = 200
MAX_TEXT_LENGTH = 10000

# 반응 Templates
SUCCESS_MESSAGES = [
    "정답입니다! 🎉 훌륭해요!",
    "맞았어요! 👏 잘하고 있어요!",
    "정확합니다! ⭐ 계속 이렇게만 하세요!",
    "완벽해요! 🌟 대단합니다!"
]

ENCOURAGEMENT_MESSAGES = [
    "아쉬워요! 😊 다시 한번 생각해보세요.",
    "조금 더 생각해볼까요? 💪 할 수 있어요!",
    "거의 다 왔어요! 🔥 한 번 더 도전!",
    "실수해도 괜찮아요! 🌈 배우는 과정이니까요."
]

# Session State Keys
SESSION_KEYS = {
    "current_text": "current_text",
    "summary": "summary",
    "quiz": "quiz",
    "quiz_answers": "quiz_answers",
    "quiz_submitted": "quiz_submitted",
    "score": "score",
    "history": "history"
}
