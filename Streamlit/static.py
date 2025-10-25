import streamlit as st
from util.database import *
from css.theme import *

st.header('⭐ 답변 데이터의 평점 시각화')

# 1. 이미지의 데이터를 Pandas DataFrame으로 만듭니다.
# '점수'와 '갯수'라는 두 개의 컬럼을 가집니다.
data = {
    '점수': ['1점', '2점', '3점', '4점', '5점'],
    '갯수': [0, 0, 2, 1220, 23] # 이미지에 나온 순서대로 데이터 입력
}
df = pd.DataFrame(data)

# 데이터프레임을 표로 먼저 보여주기 (선택 사항)
st.write("원본 데이터 표:")
st.dataframe(df)

st.write("---") # 구분선

# 2. st.bar_chart()를 사용해 막대그래프를 그립니다.
st.subheader('막대그래프 (st.bar_chart)')
st.bar_chart(df.set_index('점수'))


# (추가) 라인그래프로도 표현할 수 있습니다.
st.subheader('선그래프 (st.line_chart)')
st.line_chart(df.set_index('점수'))