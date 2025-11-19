# 🎓 AI 수학 과외 선생님

> 학생의 사고력을 키워주는 단계별 힌트 기반 AI 수학 튜터

## 📌 프로젝트 소개

이 프로젝트는 단순히 답을 알려주는 AI가 아닌, 학생이 스스로 문제를 해결할 수 있도록 단계별 힌트를 제공하는 AI 과외 선생님입니다.

### 핵심 철학
- ❌ 정답을 직접 알려주지 않음
- ✅ 단계별 힌트로 사고력 향상
- ✅ 다양한 선생님 페르소나 제공
- ✅ 학습 진도 및 통계 추적

## 🚀 주요 기능

### 1. 단계별 힌트 시스템
- **1단계**: 문제 접근법과 방향성 제시
- **2단계**: 핵심 개념과 중요 포인트 설명
- **3단계**: 실제 풀이 직전 단계까지 구체적 안내

### 2. 선생님 페르소나
- 👨‍🏫 **친근한 선생님**: 따뜻하고 격려하는 스타일
- 👩‍🏫 **엄격한 선생님**: 정확하고 체계적인 스타일
- 🤖 **중립적 선생님**: 객관적이고 차분한 스타일

### 3. 학습 분석
- 📊 학습 패턴 분석
- 📈 진도 추적
- 🎯 취약 영역 파악

## 📁 프로젝트 구조

```
ai_math_tutor/
│
├── app.py                    # 메인 애플리케이션
├── requirements.txt          # 의존성 패키지
├── .env.example             # 환경변수 예제
│
├── config/                  # 설정 파일
│   ├── __init__.py
│   ├── settings.py         # 앱 설정
│   └── personas.yaml       # 선생님 페르소나 정의
│
├── components/             # UI 컴포넌트
│   ├── __init__.py
│   ├── sidebar.py         # 사이드바 컴포넌트
│   ├── chat_interface.py  # 채팅 인터페이스
│   ├── hint_buttons.py    # 힌트 버튼
│   └── analytics.py       # 분석 대시보드
│
├── utils/                 # 유틸리티 함수
│   ├── __init__.py
│   ├── ai_handler.py      # ai 핸들러
│   ├── prompt_manager.py  # 프롬프트 관리
│   └── session_manager.py # 세션 상태 관리
│
├── prompts/               # 프롬프트 템플릿
│   ├── base_tutor.yaml   # 기본 튜터 프롬프트
│   ├── friendly.yaml     # 친근한 선생님
│   ├── strict.yaml       # 엄격한 선생님
│   └── neutral.yaml      # 중립적 선생님
│
├── assets/                # 정적 자원
│   ├── styles.css        # 커스텀 CSS
│   └── logo.png          # 로고 이미지
│
└── data/                  # 데이터 저장
    ├── (임시) test용 예시문제 
    ├── chat_history/      # 대화 기록
    └── analytics/         # 분석 데이터
```

## 🛠 설치 방법

### 1. 환경 설정
```bash
# 가상환경 생성(선택사항)
conda create -n edutech python=3.11.13 
conda activate edutech

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정
`.env.example` 파일을 복사하여 `.env` 파일을 만들고, OpenAI API 키를 입력하세요:
```
OPENAI_API_KEY=해당 API키
```

### 3. 실행
```bash
streamlit run app.py
```

## 📊 사용 방법

1. **문제 업로드**: 수학 문제 이미지를 업로드하거나 텍스트로 입력
2. **선생님 선택**: 사이드바에서 원하는 선생님 페르소나 선택
3. **힌트 단계 선택**: 필요한 수준의 힌트 선택
4. **대화형 학습**: AI 선생님과 대화하며 문제 해결

