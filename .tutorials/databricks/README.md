# Databricks
Databricks를 사용하여 mlflow를 구현하는 방법을 보여주는 예제입니다.

## databricks 접속 설정 방법
#### 1. databricks 접속
https://docs.databricks.com/aws/en/mlflow/ 페이지에서 우측 상단에 있는 `TRY DATABRICKS` 버튼을 클릭하고 안내에 따라 databricks를 접속합니다.


#### 2. databricks 환경 변수 설정
`.env.example` 파일을 복사하여 `.env` 파일을 생성하고, databricks 환경 변수를 설정합니다. DATABRICKS_HOST는 접속된 databricks의 URL을 입력합니다. DATABRICKS_TOKEN은 접속한 데이터브릭스 환경에서 Settings > Developer > Access Tokens 의 Manage버튼을 클릭하여 안내에 따라 생성한 토큰을 입력합니다. 아래는 예시입니다.
```
DATABRICKS_HOST=https://dbc-792예시11-532d.cloud.databricks.com
DATABRICKS_TOKEN=dapi02222b2a52예시122a5b3dba48fb517w321
```

## 실습 코드
mlflow를 사용하여 모델의 학습 과정을 기록하고, 기록된 모델을 다운로드 받아 활용하는 과정을 구현합니다.
