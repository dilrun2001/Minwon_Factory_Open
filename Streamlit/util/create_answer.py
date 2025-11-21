import streamlit as st
from util.AI_queue import *
import time
from util.state_copy import *
from css.theme import *
from util.page_convert import *


# ========================================================================================================================
#답변 생성 체크
# ========================================================================================================================
def input_answer():
    global result_check
    data = st.session_state.df
    print(data['답변요지'])
    #answers = []
    #raganswers = []
    yogi_check =(data[data['답변요지'] == ""].index+1).tolist()
    print(yogi_check)
    if yogi_check:#((data['답변요지'] =="") ).any():
        show_popup(":red[:material/block:]  답변 생성 오류", f'''입력하신 민원에 대한 :red[답변 요지]를 전부 입력해주세요.    
                   미입력 민원: :red[{'번, '.join(map(str, yogi_check))}번]'''
                   , popup_check=True)
        #st.toast(f"해당 민원에 대한 답변 요지를 입력해주세요. :red[미입력 민원: {', '.join(map(str, yogi_check))}]", icon =":material/block:")
        return
    else:    
        #show_popup("민원 입력", f"민원을 생성하겠습니까?", generate_answer)
        st.session_state.current_page = 1
        generate_answer()
        

# ========================================================================================================================
#선택한 답변 재생성 가능 여부 체크
# ========================================================================================================================
def reinput_answer():
    data = st.session_state.df
    recreate_list = []
    for i, row in data.iterrows():
        if row['수정']:
            recreate_list.append(i)
    recreate_check = data['수정'].sum() 
    print(recreate_check)
    st.session_state.recreate_count = recreate_check
    print(st.session_state.recreate_count)
    if recreate_check == 0:
        show_popup(":red[:material/block:]  답변 재생성 오류", f"""재생성할 답변이 존재하지 않습니다.\n답변 영역 내 민원 수정 체크 박스를 확인해주세요.""", popup_check = True)
        #st.toast(f"재생성할 민원을 체크해주세요. 답변 영역 내 :red[좌측 상단]을 확인해주세요.", icon = ":material/block:")
    else:
        
        generate_answer(recreate = True, multi=True)


# ========================================================================================================================
# 답변 생성 함수
# recreate -> 여부 따라 답변 재생성 함수인지 체크
# multi -> 여부 따라 복합 생성 혹은 단일 생성 체크
# yogi -> 여부 따라 민원 요약 생성인지 체크
# ========================================================================================================================
def generate_answer(index = 0, recreate = False, multi = False, yogi = False):
    enqueue_task(st.session_state.id)
    data = st.session_state.df
    results, formats, answers, raganswers = [], [], [], []
    with show_loading_overlay() as update:
    #with js_overlay_spinner() as update:
        task_id = None
        while not task_id:
            task_id = get_queue(st.session_state.id)
            if not task_id:
                num = search_queue(st.session_state.id)
                test = get_waiting_count_ahead(st.session_state.id)
                update(f"선행 처리 중인 작업이 있습니다. 대기열에 등록됩니다.")
                time.sleep(3)
                update(f"대기 중...", rank = num, ahead=test)
                time.sleep(3)
        update("대기열에 등록되었습니다. 요청하신 작업을 시작합니다.")
        time.sleep(0.5)
        match (recreate, multi, yogi):
            # ========================================================================================================================
            #답변 단일 재생성
            # ========================================================================================================================
            
            case (True, False, False): 
                if st.session_state.ai_option:
                        update(f"{index+1}번 민원의 답변을 재생성하는 중입니다.")
                        if st.session_state.model == "사하아이 연동":
                            answer = useAi.SahaAi_request(minwon=data.iloc[index]['민원내용'], answer=data.iloc[index]['답변요지'],answer_format=data.iloc[index]['답변양식'])
                        else:
                            answer = useAi.AI_print_answer(minwon=data.iloc[index]['민원내용'], answer=data.iloc[index]['답변요지'],answer_format=data.iloc[index]['답변양식'])
                        data.loc[index, '답변결과'] = answer
                        st.session_state[f"result_first_{index}"] = answer
                        #match data.loc[index, '최종답변 체크']:
                        #        case "답변결과":

                else:
                    timer = 5
                    update(f"단일 민원 생성 테스트. {timer}초 동안 해당 화면이 유지됩니다.")
                    data.at[index, '답변결과'] = "해당 답변은 단일 민원 생성 테스트에 사용된 답변입니다."
                    st.session_state[f"result_first_{index}"] = "해당 답변은 단일 민원 생성 테스트에 사용된 답변입니다."
                    time.sleep(timer)
                end_task(task_id)
                st.rerun()
            
            # ========================================================================================================================
            #답변 멀티 재생성
            # ========================================================================================================================            
            case (True, True, False):
                    if st.session_state.ai_option:
                        for i, row in data.iterrows():
                            cnt = data['수정'].sum() 
                            if row['수정'] == True:
                                cnt -= 1
                                update(f"{i+1}번 민원의 답변을 재생성하는 중입니다. ")
                                if st.session_state.model == "사하아이 연동":
                                    answer = useAi.SahaAi_request(minwon = row['민원내용'], answer = row['답변요지'], answer_format = row['답변양식'])
                                else:
                                    answer = useAi.AI_print_answer(minwon = row['민원내용'], answer = row['답변요지'], answer_format = row['답변양식'])
                                data.at[i, '답변결과'] = answer
                                st.session_state[f"result_first_{i}"] = answer
                    else:
                        for i, row in data.iterrows():
                            #cnt = row['수정']
                            if row['수정'] == True:
                                update(f"{i+1}번 민원의 답변 재생성 테스트. 답변은 생성되지 않습니다.")
                                data.at[i, '답변결과'] = "해당 답변은 멀티 민원 생성 테스트에 사용된 답변입니다."
                                if data.iloc[index]['최종답변 체크'] == '답변결과':
                                    data.at[i, '최종답변'] = data.iloc[i]['답변결과']
                                st.session_state[f"result_first_{i}"] = "해당 답변은 멀티 민원 생성 테스트에 사용된 답변입니다."
                                time.sleep(1)
                    end_task(task_id)
                    st.rerun()
            # ========================================================================================================================
            #민원 요지 생성
            # ========================================================================================================================
            case (False, False, True):
                for i, row in data.iterrows():
                    format = change_text(config['format']['format'], row['부서명'], row['이름'], row['전화번호'])
                    formats.append(format)
                data['답변양식'] = formats  
                match(st.session_state.model):
                    case "기본 모델":
                        st.session_state.default_count += len(data)
                    case "민원팩토리 모델":
                        st.session_state.mf_count += len(data)
                    case "사하아이 연동":
                        st.session_state.saha_count += len(data)
                print(f"default: {st.session_state.default_count}, minwon factory: {st.session_state.mf_count}, sahaAI: {st.session_state.saha_count}" )
                if st.session_state.ai_option:
                    time.sleep(0.5)
                    for i, row in data.iterrows():
                        update(f"{i+1}번 민원에 대한 민원 요지를 생성 중입니다. 현재 진행 상황 {i+1}/{len(data)}")
                        if st.session_state.model == "사하아이 연동":
                            result_sub = useAi.SahaAi_request_sub(row['민원내용'])
                        else:
                            result_sub = useAi.AI_print_minwon_sub(row['민원내용'])
                        results.append(result_sub)
                    data['민원요지'] = results
                else:
                    for i, row in data.iterrows():
                        data.at[i, '민원요지'] = f"{i+1}번 민원의 요약이 들어갈 자리"
                    time.sleep(2)
                end_task(task_id)
                page_convert()
            # ========================================================================================================================
            # 답변 생성
            # ========================================================================================================================
            case (False, False, False):
                match(st.session_state.model):
                    case "기본 모델":
                        st.session_state.default_count += len(data)
                    case "민원팩토리 모델":
                        st.session_state.mf_count += len(data)
                    case "사하아이 연동":
                        st.session_state.saha_count += len(data)
                print(f"default: {st.session_state.default_count}, minwon factory: {st.session_state.mf_count}, sahaAI: {st.session_state.saha_count}" )
                for i, row in data.iterrows():
                    if st.session_state.ai_option:
                        
                        update(f"{i+1}번 민원에 대한 답변을 생성중입니다. 현재 진행 상황 {i+1}/{len(data)}") #전체 민원 개수는 {len(data)}개 입니다.")
                        if st.session_state.model == "사하아이 연동":
                            answer = useAi.SahaAi_request(minwon=row['민원내용'], answer=row['답변요지'],answer_format=row['답변양식'])
                        else:
                            answer = useAi.AI_print_answer(minwon=row['민원내용'], answer=row['답변요지'],answer_format=row['답변양식'])
                        update(f"{i+1}번 민원에 대한 유사 답변이 존재하는 지 확인합니다.")
                        
                        #ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                    else:
                        update(f"AI가 비활성화되었습니다.")
                        answer = row['답변양식']#useAi.AI_print_answer(minwon=st.session_state.minwon, answer=st.session_state.answer_sub,answer_format=st.session_state.answer_format)
                        #answers.append(answer)
                    #data.at['답변결과', i] = answer
                    if st.session_state.rag_option:
                        st.session_state.name = row['이름']
                        st.session_state.department = row['부서명']
                        st.session_state.tel = row['전화번호']
                        raganswer = "rag 미지원"#ragai.find_similar_respond(minwon_summary=row['민원요지'],answer_yogi=row['답변요지'])    
                    else:
                        update(f"RAG가 비활성화되었습니다.")
                        raganswer= f"유사 답변 기능은 현재 지원하지 않습니다."#ragai.find_similar_respond(minwon_summary=st.session_state.minwon_sub,answer_yogi=st.session_state.answer_sub)
                    answers.append(answer)
                    raganswers.append(raganswer)
                data['답변결과'] = answers
                data['RAG'] = raganswers
                end_task(task_id)
                page_convert()
                st.rerun()
              





