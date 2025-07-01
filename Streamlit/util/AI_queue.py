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

# 완료 처리된 데이터 삭제
def dequeue_task(id):
    run_query(
        "DELETE FROM task_queue WHERE status = 'done' AND user_id = %s",
        (id,),
        fetch = False
    )
    if run_query("SELECT * FROM task_queue").empty:
        clear_queue()

# 큐 데이터 조회
def get_queue(id):
    row = run_query(
        "SELECT id, user_id FROM task_queue WHERE status = 'waiting' ORDER BY id ASC LIMIT 1",
    )    
    if not row.empty and row.iloc[0]['user_id'] == id:
        start_task(row.iloc[0]['id'])
        return True
    else:
        return False


def search_queue(id):
    row = run_query(
        "SELECT id FROM task_queue WHERE user_id = %s ORDER BY id ASC",
        (id,),
    )
    return (row.iloc[0]['id']-1)


#작업 시작 
def start_task(id):
    run_query(
        "UPDATE task_queue SET status = 'processing' WHERE user_id = %s",
        (id,),
        fetch  = False
    )

#작업 종료 후 전환 이후 dequeue_task 호출해서 데이터 삭제
def end_task(id):
    run_query(
        "UPDATE task_queue SET status = 'done' WHERE user_id = %s",
        (id,),
        fetch  = False
    )
    dequeue_task(id)

def clear_queue():
    run_query("TRUNCATE TABLE task_queue")

