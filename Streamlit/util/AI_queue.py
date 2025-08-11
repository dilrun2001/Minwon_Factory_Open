from util.database import *
import streamlit as st
import util.llama3_korea_bllossomQ8 as useAi #우리가 만든 ai를 사용하기위한 임포트


# 큐 데이터 삽입
def enqueue_task(id):
    run_query(
        "INSERT INTO task_queue (user_id) VALUES (%s)",
        (id,),
        fetch = False
    )


#큐 데이터 조회 신규
def get_queue(user_id):
    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False 

        with conn.cursor() as cursor:
            #'processing' 상태인 작업이 있는지 확인
            cursor.execute("SELECT 1 FROM task_queue WHERE status = 'processing' LIMIT 1")
            if cursor.fetchone():
                conn.rollback()
                return None

            # 요청한 작업이 대기열 1순위인지 확인하고 행을 잠굼
            lock_query = """
                SELECT id, user_id FROM task_queue
                WHERE status = 'waiting'
                ORDER BY created_at ASC
                LIMIT 1
                FOR UPDATE
            """
            cursor.execute(lock_query)
            next_task = cursor.fetchone()

            #대기열이 비어있거나, 내가 1순위가 아니면 리턴값 0.
            if not next_task or next_task['user_id'] != user_id:
                conn.rollback()
                return None

            #내 차례가 맞으면 상태를 'processing'으로 변경하고 task_id를 가져옴.
            task_id_to_process = next_task['id']
            update_query = "UPDATE task_queue SET status = 'processing' WHERE id = %s"
            cursor.execute(update_query, (task_id_to_process,))
            
            #변경사항을 DB에 최종 반영 task_id를 반환
            conn.commit()
            return task_id_to_process

    except Exception as e:
        print(f"데이터베이스 트랜잭션 오류 발생: {e}")
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()



def search_queue(user_id):
    """
    사용자의 실제 대기 순번을 계산하여 반환
    ROW_NUMBER() 윈도우 함수를 사용하여 'waiting' 상태인 작업들의 순위 
    """
    # 이 쿼리는 'waiting' 상태인 모든 작업을 created_at 순서로 정렬,
    # 각 행에 1부터 시작하는 순번(waiting_number)
    # 그 결과 중에서 내 user_id에 해당하는 순번을 찾아 반환
    query = """
        SELECT waiting_number
        FROM (
            SELECT 
                user_id, 
                ROW_NUMBER() OVER (ORDER BY created_at ASC) as waiting_number 
            FROM task_queue 
            WHERE status = 'waiting'
        ) as ranked_queue
        WHERE user_id = %s
    """

    result_df = run_query(query, (user_id,), fetch=True)
    
    # 내 순번이 있으면 해당 번호를, 없으면 0을 반환합니다.
    if not result_df.empty:
        return result_df.iloc[0]['waiting_number']
    else:
        return 0



#작업 시작
def start_task(user_id):

    run_query(
        """
        UPDATE task_queue SET status = 'processing' WHERE user_id = %s AND status = 'waiting' ORDER BY created_at ASC LIMIT 1
        """,
        (user_id,),
        fetch=False
    )
 
def end_task(task_id):

    if not isinstance(task_id, int):
        print(f"[END_TASK-ERROR] 잘못된 task_id를 받았습니다: {task_id}")
        return

    conn = None
    try:
        conn = get_connection()
        conn.autocommit = False

        with conn.cursor() as cursor:
            # 'processing' 상태인 것을 한 번 더 확인하여 안전장치를 추가.
            query = "DELETE FROM task_queue WHERE id = %s AND status = 'processing'"
            affected_rows = cursor.execute(query, (task_id,))
            
            if affected_rows == 0:
                conn.rollback()
                return

            conn.commit()

    except Exception as e:
        print(f"[END_TASK-ERROR] 작업 종료 처리 중 오류 발생: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def dequeue_task(task_id):
    #task_id를 받아 작업 삭제
    run_query(
        "DELETE FROM task_queue WHERE id = %s AND status = 'done'",
        (task_id,),
        fetch=False
    )
    # 테이블에 남은 작업이 있는지 확인 후, 없다면 초기화
    if run_query("SELECT 1 FROM task_queue LIMIT 1").empty:
        clear_queue()

def clear_queue():
    run_query("TRUNCATE TABLE task_queue", fetch=False)


