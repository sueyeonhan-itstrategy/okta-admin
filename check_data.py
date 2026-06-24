"""Okta 데이터 확인용 CLI.

사용 예:
  python check_data.py group "App-Slack"
  python check_data.py app "Slack"
  python check_data.py user someone@company.com
"""

import sys
import json

from okta_client import OktaClient


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    command, target = sys.argv[1], sys.argv[2]
    client = OktaClient()

    if command == "group":
        members = client.get_group_members_by_name(target)
        print(f"그룹 '{target}' 멤버 수: {len(members)}")
        for m in members:
            print(f"- {m['profile']['login']} ({m['status']})")

    elif command == "app":
        users = client.get_app_users_by_label(target)
        print(f"앱 '{target}' 할당 사용자 수: {len(users)}")
        for u in users:
            print(f"- {u['profile'].get('email') or u['profile'].get('login')} ({u['status']})")

    elif command == "user":
        user = client.get_user(target)
        if not user:
            print(f"사용자를 찾을 수 없습니다: {target}")
        else:
            print(json.dumps(user, indent=2, ensure_ascii=False))

    else:
        print(f"알 수 없는 명령: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
