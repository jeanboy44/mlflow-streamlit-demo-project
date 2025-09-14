# MLFlow
mlflow의 기본 개념과 사용법을 익히기 위한 실습입니다.

## mlflow 서버 설정
#### 1. mlflow 시작
https://mlflow.org/docs/3.3.2/ml/getting-started/tracking-server-overview/
```
mlflow ui
```
#### 2. mlflow 접속
http://127.0.0.1:5000 으로 접속합니다. 만약 액세스가 거부되었다는 메세지가 뜬다면, 브라우져를 incognito 모드로 실행해주세요.


#### 3. mlflow 종료
```
Ctrl + C
```

## 실습 코드
mlflow를 사용하여 모델의 학습 과정을 기록하고, 기록된 모델을 다운로드 받아 활용하는 과정을 구현합니다.