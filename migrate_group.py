"""사용자 목록을 특정 그룹으로 옮깁니다 (대상 그룹 추가 + 기존 그룹에서 제거).

기본은 dry-run(미리보기) 모드입니다. 실제로 적용하려면 --apply 를 붙이세요.

사용 예:
  # 이메일을 한 줄에 하나씩 적은 파일 사용
  python migrate_group.py --emails-file emails.txt \
      --add-to "app-atl-confluence-subsidiary" \
      --remove-from "app-atl-confluence-user" "app-atl-confluence-partner"

  # 실제 적용
  python migrate_group.py --emails-file emails.txt \
      --add-to "app-atl-confluence-subsidiary" \
      --remove-from "app-atl-confluence-user" "app-atl-confluence-partner" \
      --apply
"""

import argparse

from okta_client import OktaClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emails-file", required=True, help="이메일을 한 줄에 하나씩 적은 파일")
    parser.add_argument("--add-to", required=True, help="추가할 그룹명")
    parser.add_argument("--remove-from", nargs="*", default=[], help="속해 있으면 제거할 그룹명 (여러 개 가능)")
    parser.add_argument("--apply", action="store_true", help="실제로 적용합니다 (기본은 미리보기만)")
    args = parser.parse_args()

    with open(args.emails_file, encoding="utf-8") as f:
        emails = [line.strip() for line in f if line.strip()]

    client = OktaClient()

    add_group = client.find_group_by_name(args.add_to)
    if not add_group:
        raise ValueError(f"그룹을 찾을 수 없습니다: {args.add_to}")

    remove_groups = []
    for name in args.remove_from:
        group = client.find_group_by_name(name)
        if not group:
            raise ValueError(f"그룹을 찾을 수 없습니다: {name}")
        remove_groups.append(group)

    mode = "실제 적용" if args.apply else "미리보기 (--apply 없이 실행됨, 아무것도 변경되지 않음)"
    print(f"[{mode}] 대상 사용자 수: {len(emails)}\n")

    for email in emails:
        user = client.get_user(email)
        if not user:
            print(f"- {email}: 옥타 계정 없음, 스킵")
            continue

        user_id = user["id"]
        user_group_ids = {g["id"] for g in client.get_user_groups(user_id)}

        actions = []
        if add_group["id"] not in user_group_ids:
            actions.append(f"+{args.add_to}")
        for rg in remove_groups:
            if rg["id"] in user_group_ids:
                actions.append(f"-{rg['profile']['name']}")

        if not actions:
            print(f"- {email}: 변경 없음 (이미 대상 그룹, 제거 대상 그룹 미가입)")
            continue

        print(f"- {email}: {', '.join(actions)}")

        if not args.apply:
            continue

        if add_group["id"] not in user_group_ids:
            client.add_user_to_group(add_group["id"], user_id)
        for rg in remove_groups:
            if rg["id"] in user_group_ids:
                client.remove_user_from_group(rg["id"], user_id)

    if not args.apply:
        print("\n실제로 적용하려면 --apply 옵션을 붙여 다시 실행하세요.")


if __name__ == "__main__":
    main()
