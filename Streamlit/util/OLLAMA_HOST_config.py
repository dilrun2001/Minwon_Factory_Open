import os
import logging
from dotenv import load_dotenv

# 로깅 설정 (필요시)
logging.basicConfig(level=logging.WARNING)

def load_environment() -> None:
    load_dotenv()

def get_required_env(var_name: str, default_value: str = None) -> str:
    """
    환경 변수를 가져오되, 없으면 경고 로그를 띄우고 기본값을 반환합니다.
    """
    load_environment()
    value = os.getenv(var_name)
    
    # 값이 없거나 빈 문자열인 경우
    if value is None or value.strip() == "":
        # 1. 오류(raise) 대신 로그를 남깁니다.
        logging.warning(f"주의: 환경변수 '{var_name}'가 없습니다. 기본값('{default_value}')을 사용합니다.")
        
        # 2. 프로그램이 죽지 않도록 기본값을 반환합니다.
        # 만약 default_value도 None이라면, 뒤에서 결국 오류가 날 것입니다.
        return default_value
        
    return value.strip()

# 사용 예시: 환경변수가 없으면 로컬호스트를 기본으로 사용
OLLAMA_HOST: str = get_required_env("OLLAMA_HOST", default_value="http://localhost:3000")

print(f"설정된 호스트: {OLLAMA_HOST}")