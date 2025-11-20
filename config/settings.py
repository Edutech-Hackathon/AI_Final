import os
from dotenv import load_dotenv

load_dotenv()

# 앱 기본 설정
APP_CONFIG = {
    'name': 'AI 수학 과외 선생님',
    'version': '1.0.0',
    'author': '교육 혁신 팀',
    'description': '학생의 사고력을 키워주는 단계별 힌트 기반 AI 튜터'
}

# API 설정
API_CONFIG = {
    'openai_api_key': os.getenv('OPENAI_API_KEY'),
    'model_name': 'gpt-4o-mini',
    'max_tokens': 1024,
    'temperature': 0.7
}

# UI 설정
UI_CONFIG = {
    'theme': {
        'primaryColor': '#667eea',
        'backgroundColor': '#ffffff',
        'secondaryBackgroundColor': '#f0f2f6',
        'textColor': '#262730',
        'font': 'sans serif'
    },
    'layout': 'wide',
    'sidebar_state': 'expanded'
}

# 학습 설정
LEARNING_CONFIG = {
    'hint_levels': 3,
    'max_chat_history': 50,
    'auto_save_interval': 5,  # 분
    'session_timeout': 30,  # 분
}

# 파일 경로
PATHS = {
    'data_dir': 'data',
    'prompts_dir': 'prompts',
    'assets_dir': 'assets',
    'logs_dir': 'logs'
}

# 지원 파일 형식
SUPPORTED_FORMATS = {
    'images': ['png', 'jpg', 'jpeg', 'gif'],
    'documents': ['pdf', 'txt']
}

# 페르소나 설정
PERSONAS = {
    'friendly': {
        'name': '친근한 선생님',
        'emoji': '😊',
        'description': '따뜻하고 격려하는 스타일로 가르칩니다.',
        'temperature': 0.8,
        'style': 'casual'
    },
    'strict': {
        'name': '엄격한 선생님',
        'emoji': '🧐',
        'description': '정확하고 체계적으로 가르칩니다.',
        'temperature': 0.5,
        'style': 'formal'
    },
    'neutral': {
        'name': '중립적 선생님',
        'emoji': '🤖',
        'description': '객관적이고 차분하게 가르칩니다.',
        'temperature': 0.6,
        'style': 'neutral'
    }
}

# 학년별 난이도 설정
GRADE_LEVELS = {
    '초등학생': {
        'difficulty': 'easy',
        'topics': ['사칙연산', '분수', '소수', '도형', '측정']
    },
    '중학생': {
        'difficulty': 'medium',
        'topics': ['정수와 유리수', '통계와 확률', '이차방정식', '제곱근과 실수', '삼각비']
    },
    '고등학생': {
        'difficulty': 'very-hard',
        'topics': ['지수와 로그', '수열', '미적분', '확률과 통계', '기하와 벡터']
    }
}

# 통계 설정
ANALYTICS_CONFIG = {
    'track_hints': True,
    'track_time': True,
    'track_problems': True,
    'export_format': 'json',  # json, csv, excel
    'retention_days': 90
}

# 보안 설정
SECURITY_CONFIG = {
    'enable_auth': False,
    'session_expire': 3600,  # 초
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'allowed_origins': ['*']
}

# 디버그 설정
DEBUG_CONFIG = {
    'debug_mode': os.getenv('DEBUG', 'False').lower() == 'true',
    'log_level': 'INFO',
    'show_errors': True,
    'save_logs': True
}

def get_config(section=None):
    """설정 값 반환"""
    configs = {
        'app': APP_CONFIG,
        'api': API_CONFIG,
        'ui': UI_CONFIG,
        'learning': LEARNING_CONFIG,
        'paths': PATHS,
        'formats': SUPPORTED_FORMATS,
        'personas': PERSONAS,
        'grades': GRADE_LEVELS,
        'analytics': ANALYTICS_CONFIG,
        'security': SECURITY_CONFIG,
        'debug': DEBUG_CONFIG
    }
    
    if section:
        return configs.get(section, {})
    return configs

def validate_config():
    """설정 검증"""
    errors = []
    
    # API 키 검증
    if not API_CONFIG.get('openai_api_key'):
        errors.append("OpenAI API 키가 설정되지 않았습니다.")
    
    # 디렉토리 생성
    for path in PATHS.values():
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            errors.append(f"디렉토리 생성 실패 ({path}): {str(e)}")
    
    return errors

# 설정 검증 실행
config_errors = validate_config()
if config_errors:
    print("설정 검증 오류:")
    for error in config_errors:
        print(f"  - {error}")
