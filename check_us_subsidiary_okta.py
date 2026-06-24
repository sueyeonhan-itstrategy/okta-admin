"""구글 워크스페이스에서 export한 사용자 목록 CSV를 기준으로,
해당 계정들의 옥타 권한(그룹)을 조회합니다.

구글과 옥타는 연동되어 있지 않으므로, 이메일 아이디(@ 앞부분)가 같다는
전제로 A@oliveyoung.co.kr / A@cj.net 순으로 옥타에서 찾아 매칭합니다.

CSV는 Google Admin 콘솔 → 사용자 → (필터링 후) → 다운로드로 받은 파일을
그대로 사용하면 됩니다. "Email Address" 또는 "primaryEmail" 컬럼을 자동으로 찾습니다.

사용 예:
  python check_us_subsidiary_okta.py us_users.csv
"""

import argparse
import csv

from okta_client import OktaClient

OKTA_DOMAINS = ["oliveyoung.co.kr", "cj.net"]
EMAIL_COLUMN_CANDIDATES = ["Email Address", "primaryEmail", "Email", "email"]


def extract_emails(csv_path: str) -> list[str]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        column = next((c for c in EMAIL_COLUMN_CANDIDATES if c in (reader.fieldnames or [])), None)
        if not column:
            raise ValueError(
                f"이메일 컬럼을 찾을 수 없습니다. CSV 헤더: {reader.fieldnames}\n"
                f"다음 중 하나가 있어야 합니다: {EMAIL_COLUMN_CANDIDATES}"
            )
        return [row[column].strip() for row in reader if row.get(column, "").strip()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", help="구글 어드민에서 export한 사용자 목록 CSV 경로")
    args = parser.parse_args()

    emails = extract_emails(args.csv_path)
    print(f"CSV 사용자 수: {len(emails)}\n")

    okta = OktaClient()

    for google_email in emails:
        local_id = google_email.split("@")[0]

        matched = None
        for domain in OKTA_DOMAINS:
            candidate = f"{local_id}@{domain}"
            okta_user = okta.get_user(candidate)
            if okta_user:
                matched = (candidate, okta_user)
                break

        print(f"- {google_email}")
        if not matched:
            print("    옥타 계정 없음 (oliveyoung.co.kr / cj.net 모두 매칭 안됨)")
            continue

        okta_email, okta_user = matched
        groups = okta.get_user_groups(okta_user["id"])
        group_names = sorted(g["profile"]["name"] for g in groups)
        print(f"    옥타 계정: {okta_email} ({okta_user['status']})")
        print(f"    그룹({len(group_names)}): {', '.join(group_names) or '없음'}")


if __name__ == "__main__":
    main()
