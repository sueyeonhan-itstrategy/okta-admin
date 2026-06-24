# Okta Admin API 조회 도구

옥타 어드민 데이터 확인(그룹 멤버, 앱 할당 현황 등)을 위한 읽기 전용 API 호출 스크립트 모음입니다.

## 설정

```bash
pip install -r requirements.txt
cp .env.example .env
# .env에 OKTA_DOMAIN, OKTA_API_TOKEN 입력
```

## 사용

```bash
# 그룹 멤버 조회
python check_data.py group "App-Slack"

# 앱 할당 현황 조회
python check_data.py app "Slack"

# 사용자 단건 조회
python check_data.py user someone@company.com

# 두 그룹에 동시에 소속된 사용자 조회
python group_intersection.py "App-Slack" "Dept-Engineering"
```

`okta_client.py`의 `OktaClient`를 다른 스크립트에서 import해서 재사용할 수 있습니다.
