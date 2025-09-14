import streamlit as st

st.set_page_config(page_title="MLflow Demo", page_icon="✅", layout="wide")

st.title("Predictive Maintenance 예측")
st.write(
    "MLflow에 등록된 모델을 사용하여 장비의 고장 여부를 예측하는 Streamlit 데모 앱입니다."
)

st.header("사용 방법")
st.write("""
1. **Predict**: 사이드바에서 'Predict' 메뉴를 선택하세요. 슬라이더와 숫자 입력을 통해 장비의 센서 값을 조정하고 '예측' 버튼을 클릭하여 고장 여부를 예측할 수 있습니다.
""")

st.sidebar.success("위에서 데모를 선택하세요.")
