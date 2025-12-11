import pandas as pd
import numpy as np
import pickle
import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from util.database import *

# 설정값 (파일명 등)
CACHE_FILE = "minwon_history_embeddings.pkl"
MODEL_NAME = "jhgan/ko-sroberta-multitask"

# [중요] run_query 함수 가져오기
try:
    from database import run_query 
except ImportError:
    pass 

# ==============================================================================
# 0. (헬퍼) AI 모델 로드 함수
# ==============================================================================
def load_embedding_model():
    """
    AI 모델을 메모리에 로드하여 반환합니다.
    Streamlit에서는 이 함수에 @st.cache_resource를 붙여서 씁니다.
    """
    print("[System] 임베딩 모델을 로드합니다...")
    return SentenceTransformer(MODEL_NAME)

# ==============================================================================
# 1. 벡터 데이터 생성 함수 (Create)
# ==============================================================================
def create_vector_data():
    """
    DB의 'history' 테이블을 조회하여 벡터 데이터(pkl)를 새로 만듭니다.
    DB 업데이트가 있을 때만 실행하세요.
    """
    print("[Create] DB에서 데이터를 조회하여 벡터 데이터를 생성합니다...")
    
    # 1. DB 조회
    sql = "SELECT minwon, response FROM history"
    try:
        df = run_query(sql)
    except NameError:
        print("run_query 함수가 없습니다.")
        return False
        
    if df is None or df.empty:
        print("[Create] DB에 데이터가 없습니다.")
        return False

    # 2. 모델 로드 (생성할 때도 모델이 필요함)
    model = load_embedding_model()
    
    # 3. 벡터화 (오래 걸림)
    print(f"[Create] {len(df)}건의 데이터를 벡터화 중입니다...")
    embeddings = model.encode(df['minwon'].tolist())
    
    # 4. 파일 저장
    data = {
        'df': df,
        'embeddings': embeddings
    }
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(data, f)
        
    print(f"[Create] 생성 완료! '{CACHE_FILE}'에 저장되었습니다.")
    return True

# ==============================================================================
# 2. 벡터 데이터 로드 함수 (Load)
# ==============================================================================
def load_vector_data():
    """
    저장된 벡터 파일(pkl)을 읽어서 DataFrame과 Embeddings를 반환합니다.
    파일이 없으면 None을 반환합니다.
    """
    if not os.path.exists(CACHE_FILE):
        print(f"[Load] '{CACHE_FILE}' 파일이 없습니다. create_vector_data()를 먼저 실행하세요.")
        return None, None
        
    print(f"[Load] '{CACHE_FILE}' 파일을 읽어옵니다.")
    with open(CACHE_FILE, 'rb') as f:
        data = pickle.load(f)
        
    return data['df'], data['embeddings']

# ==============================================================================
# 3. 유사도 검색 함수 (Search)
# ==============================================================================
def search_vector_data(user_input, df, embeddings, model, top_k=3):
    """
    사용자 입력(user_input)과 기존 데이터(df, embeddings)를 비교하여
    가장 유사한 답변을 찾습니다.
    (주의: model 객체는 외부에서 넘겨받아야 속도가 빠릅니다)
    """
    if df is None or embeddings is None:
        print("[Search] 데이터가 비어있습니다.")
        return []
        
    # 1. 사용자 입력 벡터화
    query_vec = model.encode([user_input])
    
    # 2. 유사도 계산
    similarity_scores = cosine_similarity(query_vec, embeddings)[0]
    
    # 3. 상위 K개 추출
    top_indices = np.argsort(similarity_scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        results.append({
            "score": float(similarity_scores[idx]),
            "minwon": df.iloc[idx]['minwon'],
            "response": df.iloc[idx]['response']
        })
        
    return results