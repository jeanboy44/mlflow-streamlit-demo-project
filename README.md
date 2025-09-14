# mlflow-streamlit-demo-project

## 설치
### 환경 설치
#### (option 1) conda 사용
1. conda environment 생성 및 활성화
    ```
    conda create -n mlflow-streamlit-demo-project python=3.12
    conda activate mlflow-streamlit-demo-project
    ```
1. 필요한 패키지 설치
    ```
    pip install -r requirements.txt
    ```

#### (option 2) uv 사용
1. uv 설치
   - mac: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`
1. python envrionment 설정
    ```
    uv sync
    ```
1. venv 활성화
    - mac: `source .venv/bin/activate`
    - windows: `.venv\Scripts\activate`

### 테스트
1. test_env.py 실행
```
python scripts/test_env.py
```
