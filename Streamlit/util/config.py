import os
from dotenv import load_dotenv


def load_environment() -> None:
    """Load environment variables from a local .env file if present."""
    load_dotenv()


def get_required_env(var_name: str) -> str:
    """Return required environment variable or raise a helpful error.

    Enforces providing configuration via environment variables instead of
    hardcoding defaults in source code.
    """
    load_environment()
    value = os.getenv(var_name)
    if value is None or value.strip() == "":
        raise RuntimeError(
            f"환경변수 '{var_name}'가 설정되어 있지 않습니다. "
            "프로젝트 루트의 .env 파일에 값을 설정해주세요. 예)\n"
            f"{var_name}=http://<server-ip>:11434"
        )
    return value.strip()


# Required configurations
OLLAMA_HOST: str = get_required_env("OLLAMA_HOST")
