import streamlit as st
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.types import Schema
from dotenv import load_dotenv

load_dotenv()

# --- 페이지 설정 ---
st.title("파일로 예측")
st.write("CSV 파일을 업로드하여 여러 데이터 포인트에 대한 고장 여부를 예측합니다.")
mlflow.set_tracking_uri("databricks")


def convert_and_download(df, file_name):
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="다운로드 (CSV)",
        data=csv,
        file_name=file_name,
        mime="text/csv",
    )


# --- 모델 버전 선택 (사이드바) ---
try:
    client = MlflowClient(tracking_uri="databricks")
    models = [
        v.name for v in client.search_registered_models() if "workspace" in v.name
    ]
    selected_model = st.sidebar.selectbox("모델 이름을 선택하세요", models)

    versions = [
        v.version for v in client.search_model_versions(f"name='{selected_model}'")
    ]
    sorted_versions = sorted(versions, key=int, reverse=True)

    selected_version = st.sidebar.selectbox(
        "모델 버전을 선택하세요",
        sorted_versions,
        index=0,  # 기본으로 최신 버전 선택
    )
    st.sidebar.info(f"선택된 모델: **{selected_model}**, 버전: **{selected_version}**")

except Exception as e:
    st.error(f"MLflow에서 모델 버전을 가져오는 중 오류가 발생했습니다: {e}")
    st.error("MLflow tracking server가 실행 중인지 확인하세요.")
    st.stop()


# --- 모델 로드 ---
@st.cache_resource
def load_model(model_name: str, model_version: str):
    """모델 URI를 기반으로 MLflow 모델을 로드하고 캐싱합니다."""
    model_uri = f"models:/{model_name}/{model_version}"
    return mlflow.pyfunc.load_model(model_uri)


try:
    model = load_model(selected_model, selected_version)
    input_schema: Schema = model.metadata.get_input_schema()
    if input_schema is None:
        st.error("모델에 등록된 입력 스키마가 없습니다.")
        st.stop()
    input_example: pd.DataFrame = model.metadata.load_input_example()
    if input_example is None:
        st.error("모델에 등록된 입력 예제가 없습니다.")
        st.stop()

    st.success(f"모델(버전: {selected_version})을 성공적으로 로드했습니다.")
except Exception as e:
    st.error(f"모델을 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

st.divider()

# --- 파일 업로드 및 예측 ---
uploaded_file = st.file_uploader("CSV 파일 선택", type="csv")

if uploaded_file is not None:
    input_df_original = pd.read_csv(uploaded_file)

    st.write("업로드된 데이터 (일부):")
    st.dataframe(input_df_original.head())

    st.divider()

    button = st.button("예측 실행")
    if button:
        input_df = input_df_original.copy()
        features_for_model = input_schema.input_names()

        # 파일에 모든 피처가 있는지 확인
        missing_cols = set(features_for_model) - set(input_df.columns)
        if missing_cols:
            st.error(f"입력 파일에 필요한 컬럼이 누락되었습니다: {missing_cols}")
            st.error("파일의 컬럼이 모델이 기대하는 형식과 일치하는지 확인하세요.")
            st.stop()

        # 모델에 필요한 컬럼만 필터링하여 예측
        with st.spinner("예측을 수행 중입니다..."):
            predictions = model.predict(input_df[features_for_model])

        result_df = input_df_original.copy()
        result_df["prediction"] = ["고장" if p == 1 else "정상" for p in predictions]

        st.subheader("예측 결과")

        if result_df is not None:
            display_df_all = result_df
            display_df_defect = result_df[result_df["prediction"] == "고장"]
            display_df_normal = result_df[result_df["prediction"] == "정상"]

        tabs = st.tabs(["전체", "고장", "정상"])
        with tabs[0]:
            st.dataframe(display_df_all)
            convert_and_download(display_df_all, "prediction_results_all.csv")
        with tabs[1]:
            st.dataframe(display_df_defect)
            convert_and_download(display_df_defect, "prediction_results_defect.csv")
        with tabs[2]:
            st.dataframe(display_df_normal)
            convert_and_download(display_df_normal, "prediction_results_normal.csv")
