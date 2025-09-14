import streamlit as st
import mlflow
from dotenv import load_dotenv
from mlflow.pyfunc import PyFuncModel
import pandas as pd

load_dotenv()

# --- MLflow 설정 ---
st.title("개별 예측")
st.write("센서 데이터를 직접 입력하여 고장 여부를 예측합니다.")

mlflow.set_tracking_uri("databricks")


# --- 모델 로드 함수 정의---
def load_model(model_name: str, model_version: str) -> PyFuncModel:
    # 예제 1) 모델 로드 함수 정의 --------------------------------------------------
    # 모델 이름과 버전을 입력받아 mlflow에서 모델을 로드하는 함수를 정의
    pass  # 수정 필요
    # ------------------------------------------------------------------------


# --- 모델 선택 ---
st.sidebar.subheader("모델 선택")
# 예제 2) --------------- 사이드바에서 model_name과 model_version을 받음 ---------------
# 모델의 이름과 버전을 사이드바에서 선택할 수 있도록 수정 필요
model_name = None  # 수정 필요
model_version = None  # 수정 필요
# ---------------------------------------------------------------------------------

# --- 모델 로드 ---
try:
    model = load_model(model_name, model_version)
    st.success(f"MLflow에서 모델을 가져왔습니다: {model.model_id}")
except Exception as e:
    st.error(f"MLflow에서 모델 버전을 가져오는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 입력값 생성 ---
st.subheader("데이터 입력")
# 예제 3) --------------- streamlit의 기능을 활용해서 입력값을 받도록 이 부분을 대체 ---------------
# 각 변수의 입력값을 사용자에게서 받아올 수 있도록 수정 필요. 초기값은 등록된 예제 데이터를 참고
col1, col2 = st.columns(2)
with col1:
    input_uid: int = None  # 수정 필요
    input_air_temperature: float = None  # 수정 필요
    input_process_temperature: float = None  # 수정 필요
with col2:
    input_rotational_speed: int = None  # 수정 필요
    input_torque: float = None  # 수정 필요
    input_tool_wear: int = None  # 수정 필요
# ------------------------------------------------

inputs = {
    "uid": input_uid,
    "air_temperature": input_air_temperature,
    "process_temperature": input_process_temperature,
    "rotational_speed": input_rotational_speed,
    "torque": input_torque,
    "tool_wear": input_tool_wear,
}

input_df = pd.DataFrame([inputs])
st.subheader("입력된 데이터")
st.dataframe(input_df)

st.divider()
# 예측 버튼 클릭 시 실행
if st.button("예측"):
    with st.spinner("예측을 수행 중입니다..."):
        prediction = model.predict(input_df)
        result = "고장" if prediction[0] == 1 else "정상"
        st.write(result)
