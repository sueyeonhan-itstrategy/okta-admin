"""두 옥타 그룹에 동시에 소속된 사용자를 조회합니다.

사용 예:
  python group_intersection.py "App-Slack" "Dept-Engineering"
"""

import sys

from okta_client import OktaClient


def find_common_members(client: OktaClient, group_a: str, group_b: str) -> list[dict]:
    members_a = client.get_group_members_by_name(group_a)
    members_b = client.get_group_members_by_name(group_b)

    ids_b = {m["id"] for m in members_b}
    return [m for m in members_a if m["id"] in ids_b]


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)

    group_a, group_b = sys.argv[1], sys.argv[2]
    client = OktaClient()

    common = find_common_members(client, group_a, group_b)

    print(f"'{group_a}' ∩ '{group_b}' 멤버 수: {len(common)}")
    for m in common:
        print(f"- {m['profile']['login']} ({m['status']})")


if __name__ == "__main__":
    main()
