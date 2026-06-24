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

# 그룹A 멤버 중 그룹B와 중복인 사람을 그룹A에서 제거 (기본 dry-run, --apply로 실제 실행)
python remove_from_group.py --remove-from "App-A" --keep-in "App-B" [--apply]

# 구글 어드민에서 export한 CSV 기준으로 옥타 권한(그룹) 조회
python check_us_subsidiary_okta.py us_users.csv
```

`okta_client.py`의 `OktaClient`를 다른 스크립트에서 import해서 재사용할 수 있습니다.

## 구글 워크스페이스 연동 (check_us_subsidiary_okta.py)

구글과 옥타는 직접 연동되어 있지 않으므로, Google Admin 콘솔 → 사용자 목록에서
조직 단위(OU)로 필터링한 뒤 CSV로 다운로드한 파일을 입력으로 받습니다.
이메일 아이디(@ 앞부분)가 같다는 전제로 `{id}@oliveyoung.co.kr` → `{id}@cj.net`
순서로 옥타에서 찾아 매칭하고, 매칭된 계정의 그룹(권한) 목록을 출력합니다.

CSV는 "Email Address" 또는 "primaryEmail" 컬럼이 있으면 자동으로 인식합니다.
CSV 파일 자체는 `.gitignore`에 포함되어 커밋되지 않습니다.
