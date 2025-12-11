import pandas as pd
import numpy as np
from util.state_copy import *

# 1. CSV 파일 읽기
df = pd.read_csv('sample_history_data.csv')

# [중요] CSV의 빈 값(NaN)을 파이썬의 None으로 바꿉니다.
# (이렇게 해야 DB에 들어갈 때 오류 없이 NULL로 들어갑니다)
df = df.replace({np.nan: None})

print(f"총 {len(df)}개의 데이터를 발견했습니다. 전체 컬럼 입력을 시작합니다...")

# 2. 데이터 삽입 루프
success_count = 0

for idx, row in df.iterrows():
    try:
        # SQL 작성: timestamp, answer_yogi, grade 컬럼 추가
        # (DB 테이블에도 이 이름으로 컬럼이 만들어져 있어야 합니다)
        sql = """
            INSERT INTO history 
            (timestamp, name, minwon, response, answer_yogi, grade) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        # 파라미터 매핑
        params = (
            row['timestamp'],    # 작성 일시
            row['name'],         # 작성자 이름 (CSV name -> DB name)
            row['minwon'],       # 민원 내용
            row['response'],     # 답변 내용
            row['answer_yogi'],  # 답변 요약 (또는 추가 정보)
            row['grade']         # 평점 (숫자)
        )
        
        # 3. 쿼리 실행
        run_query(sql, params=params, fetch=False)
        success_count += 1
        
    except Exception as e:
        print(f"[{idx}번 행 입력 실패]: {e}")

print(f"\n작업 완료! 총 {success_count}건의 모든 데이터가 저장되었습니다.")