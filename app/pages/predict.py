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
    model = mlflow.pyfunc.load_model(f"models:/{model_name}/{model_version}")
    return model
    # ------------------------------------------------------------------------


# --- 모델 선택 ---
st.sidebar.subheader("모델 선택")
# 예제 2) --------------- 사이드바에서 model_name과 model_version을 받음 ---------------
# 모델의 이름과 버전을 사이드바에서 선택할 수 있도록 수정 필요
model_name = st.sidebar.selectbox(
    "모델 이름", ["workspace.default.predictive_maintenance"]
)
model_version = st.sidebar.selectbox("모델 버전", ["1"])
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
    input_uid: int = st.number_input("uid", value=9255)
    input_air_temperature: float = st.number_input("air_temperature", value=298.3)
    input_process_temperature: float = st.number_input(
        "process_temperature", value=309.1
    )
with col2:
    input_rotational_speed: int = st.number_input("rotational_speed", value=1616)
    input_torque: float = st.number_input("torque", value=31.1)
    input_tool_wear: int = st.number_input("tool_wear", value=195)
# ------------------------------------------------

inputs = {
    "uid": input_uid,
    "air_temperature": input_air_temperature,
    "process_temperature": input_process_temperature,
    "rotational_speed": input_rotational_speed,
    "torque": input_torque,
    "tool_wear": input_tool_wear,
}
if all(inputs.values()):
    st.write("입력 데이터")
    input_df = pd.DataFrame([inputs])
    st.dataframe(input_df)
else:
    st.error("모든 입력값을 입력해주세요.")
    st.stop()

st.divider()
# 예측 버튼 클릭 시 실행
if st.button("예측"):
    with st.spinner("예측을 수행 중입니다..."):
        try:
            prediction = model.predict(input_df)
            result = "고장" if prediction[0] == 1 else "정상"
            st.write(result)
        except Exception as e:
            st.error(f"예측 중 오류가 발생했습니다: {e}")
