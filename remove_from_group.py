"""특정 그룹에 동시에 속한 사용자를 다른 그룹에서 제거합니다.

group_intersection.py 와 동일한 교집합 로직을 사용해, '제거할 그룹'에서
'유지할 그룹'과 공통으로 속한 사용자만 제거합니다.

기본은 dry-run(미리보기) 모드입니다. 실제로 제거하려면 --apply 를 붙이세요.

사용 예:
  # 미리보기만 (아무것도 변경하지 않음)
  python remove_from_group.py --remove-from "app-atl-confluence-partner" --keep-in "app-atl-confluence-subsidiary"

  # 실제로 제거
  python remove_from_group.py --remove-from "app-atl-confluence-partner" --keep-in "app-atl-confluence-subsidiary" --apply
"""

import argparse

from okta_client import OktaClient


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--remove-from", required=True, help="제거 대상 그룹명")
    parser.add_argument("--keep-in", required=True, help="유지할 그룹명 (이 그룹과 겹치는 사용자만 제거)")
    parser.add_argument("--apply", action="store_true", help="실제로 제거를 실행합니다 (기본은 미리보기만)")
    args = parser.parse_args()

    client = OktaClient()

    remove_group = client.find_group_by_name(args.remove_from)
    keep_group = client.find_group_by_name(args.keep_in)
    if not remove_group:
        raise ValueError(f"그룹을 찾을 수 없습니다: {args.remove_from}")
    if not keep_group:
        raise ValueError(f"그룹을 찾을 수 없습니다: {args.keep_in}")

    members_remove = client.get_group_members(remove_group["id"])
    members_keep_ids = {m["id"] for m in client.get_group_members(keep_group["id"])}

    targets = [m for m in members_remove if m["id"] in members_keep_ids]

    mode = "실제 제거" if args.apply else "미리보기 (--apply 없이 실행됨, 아무것도 변경되지 않음)"
    print(f"[{mode}] '{args.remove_from}'에서 제거 대상 ('{args.keep_in}'과 중복): {len(targets)}명")
    for m in targets:
        print(f"- {m['profile']['login']}")

    if not args.apply:
        print("\n실제로 제거하려면 --apply 옵션을 붙여 다시 실행하세요.")
        return

    print()
    for m in targets:
        client.remove_user_from_group(remove_group["id"], m["id"])
        print(f"제거 완료: {m['profile']['login']}")


if __name__ == "__main__":
    main()
