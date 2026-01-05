import sys
import os
import subprocess
import platform
import time

# --- [설정 영역] ---
# 실행할 파이썬 파일들이 들어있는 폴더 이름 (런처와 같은 위치 기준)
TARGET_DIR_NAME = "Streamlit" 

# 타겟 폴더 안에 있는 파일 이름 매핑
APP_FILES = {
    "1": "app.py",
    "2": "app_dev.py"
}

# 기본적으로 설치할 라이브러리 (requirements.txt 외에 강제 설치할 것들)
REQUIRED_LIBRARIES = ["streamlit", "pandas", "pymysql"]
# ------------------

def clear_screen():
    """운영체제별 화면 지우기"""
    current_os = platform.system()
    if current_os == "Windows":
        os.system('cls')
    else:
        os.system('clear')

def get_base_path():
    """exe 실행 시와 py 실행 시의 기준 경로(런처가 있는 곳)를 찾습니다."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def get_target_dir_path():
    """설정된 타겟 폴더의 절대 경로를 반환합니다."""
    base_path = get_base_path()
    return os.path.join(base_path, TARGET_DIR_NAME)

def install_libraries():
    """타겟 폴더의 requirements.txt를 감지하여 설치합니다."""
    print(">>> 라이브러리 환경 구성을 확인합니다...")
    
    target_path = get_target_dir_path()
    
    # 1. 타겟 폴더가 있는지 먼저 확인
    if not os.path.exists(target_path):
        print(f"[오류] 타겟 폴더 '{TARGET_DIR_NAME}'가 없습니다.")
        return

    # 2. 타겟 폴더 안의 requirements.txt 확인
    req_file = os.path.join(target_path, "requirements.txt")
    
    if os.path.exists(req_file):
        print(f"'{req_file}' 감지됨. 설치 진행...")
        try:
            # cwd=target_path를 주어 타겟 폴더 내에서 pip 실행하는 효과를 줌 (경로 이슈 방지)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=target_path)
        except subprocess.CalledProcessError:
            print("! requirements.txt 설치 중 오류 발생")
    else:
        print(f"info: '{TARGET_DIR_NAME}' 폴더 내에 requirements.txt가 없습니다.")

    # 3. 필수 리스트 강제 설치
    if REQUIRED_LIBRARIES:
        print(f"기본 라이브러리 체크: {', '.join(REQUIRED_LIBRARIES)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + REQUIRED_LIBRARIES)
        except subprocess.CalledProcessError:
            print("! 라이브러리 설치 중 오류 발생")
            
    print(">>> 라이브러리 확인 완료.\n")
    time.sleep(1)

def run_streamlit(filename):
    """지정된 폴더로 작업 경로를 변경하여 Streamlit을 실행합니다."""
    target_dir = get_target_dir_path()
    full_path = os.path.join(target_dir, filename)

    # 폴더 존재 확인
    if not os.path.exists(target_dir):
        print(f"\n[심각한 오류] 타겟 폴더 '{TARGET_DIR_NAME}'를 찾을 수 없습니다.")
        print(f"경로: {target_dir}")
        input("엔터 키를 누르면 메뉴로 돌아갑니다.")
        return

    # 파일 존재 확인
    if not os.path.exists(full_path):
        print(f"\n[오류] '{filename}' 파일이 '{TARGET_DIR_NAME}' 폴더 안에 없습니다.")
        input("엔터 키를 누르면 메뉴로 돌아갑니다.")
        return

    print(f"\n>>> 실행 준비 중...")
    print(f"    타겟 파일: {filename}")
    print(f"    실행 위치(CWD): {target_dir}")
    print(">>> 종료하려면 터미널에서 [Ctrl + C]를 누르세요.\n")

    # [핵심] Streamlit 실행 명령어
    # 여기서 'filename'만 넘겨주는 이유는, 아래 cwd 옵션으로 이미 그 폴더에 들어가 있기 때문입니다.
    cmd = [sys.executable, "-m", "streamlit", "run", filename]

    try:
        # cwd=target_dir : 이 옵션이 'cd apps'를 한 뒤 실행하는 것과 같은 효과를 냅니다.
        # 이렇게 해야 apps 폴더 안의 1.py가 상대경로(예: ./data.csv)를 문제없이 읽습니다.
        subprocess.run(cmd, cwd=target_dir)
    except KeyboardInterrupt:
        print("\n>>> 사용자 요청으로 종료되었습니다.")
        time.sleep(1)

def main():
    while True:
        clear_screen()
        print("========================================")
        print("      Minwon Factory Launcher            ")
        print(f"      Target: ./{TARGET_DIR_NAME}/      ")
        print("========================================")
        print(" 1. 앱 실행 (app.py)")
        print(" 2. 앱(개발자 모드) 실행 (app_dev.py)")
        print(" 9. 라이브러리 설치 (requirements.txt)")
        print(" Q. 종료")
        print("========================================")
        
        choice = input(" 메뉴를 선택하세요: ").strip().lower()

        if choice in APP_FILES:
            run_streamlit(APP_FILES[choice])
        elif choice == "9":
            install_libraries()
            input("엔터를 누르면 메뉴로 돌아갑니다.")
        elif choice == "q":
            sys.exit()
        else:
            print("잘못된 입력입니다.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass