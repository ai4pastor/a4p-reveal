#!/usr/bin/python3 -I
"""A4P Finder에서 보기: herdr 칸에서 ⌃(Control)+클릭한 파일 링크를 Finder 창에서 선택해 보여 준다.

herdr 링크 처리기(link_handlers)가 넘겨준 file:// 주소(HERDR_PLUGIN_CLICKED_URL)를 맥 경로로 바꿔
`open -R` 로 Finder 에서 그 파일을 선택한다. 파일이 없으면 남아 있는 가장 가까운 상위 폴더를 열고
herdr 알림으로 이유를 알린다. 파일을 만들거나 고치거나 지우지 않는다.

시험용: A4P_REVEAL_DRY_RUN=1 이면 실행하지 않고 할 일만 JSON 으로 찍는다.
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse

OPEN = "/usr/bin/open"
LOG_NAME = "reveal.log"
LOG_KEEP = 200  # 기록은 마지막 줄 수만큼만 남긴다
NOTICE_TITLE = "Finder에서 보기"


def path_from_url(url):
    """file:// 주소를 맥 경로로 바꾼다. file 주소가 아니거나 다른 컴퓨터를 가리키면 None."""
    parts = urllib.parse.urlsplit(url.strip())
    if parts.scheme.lower() != "file":
        return None
    path = urllib.parse.unquote(parts.path)
    if parts.netloc == "~":  # file://~/… 처럼 적힌 것도 받아 준다
        return os.path.expanduser("~" + path)
    if parts.netloc not in ("", "localhost") or not path:
        return None
    return path


def nearest_existing(path):
    """없는 경로면 남아 있는 가장 가까운 상위 폴더. 끝까지 없으면 None."""
    while not os.path.exists(path):
        parent = os.path.dirname(path)
        if parent == path:
            return None
        path = parent
    return path


def plan(url):
    """할 일을 정한다: (실행할 명령 또는 None, 알릴 문구 또는 None)."""
    path = path_from_url(url)
    if path is None:
        return None, f"파일 주소가 아니어서 열지 않았습니다: {url}"
    if os.path.exists(path):
        return [OPEN, "-R", path], None
    folder = nearest_existing(path)
    if folder is None:
        return None, f"파일도 상위 폴더도 없습니다: {path}"
    return [OPEN, folder], f"파일이 없어서 남아 있는 폴더를 열었습니다: {folder}"


def notify(text):
    herdr = os.environ.get("HERDR_BIN_PATH") or "herdr"
    subprocess.run([herdr, "notification", "show", NOTICE_TITLE, "--body", text],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)


def log(url, command, notice):
    state_dir = os.environ.get("HERDR_PLUGIN_STATE_DIR")
    if not state_dir:
        return
    os.makedirs(state_dir, exist_ok=True)
    log_path = os.path.join(state_dir, LOG_NAME)
    try:
        with open(log_path, encoding="utf-8") as f:
            lines = f.read().splitlines()[-(LOG_KEEP - 1):]
    except FileNotFoundError:
        lines = []
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"{stamp}\t{url}\t{' '.join(command) if command else '-'}\t{notice or ''}")
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    url = os.environ.get("HERDR_PLUGIN_CLICKED_URL", "")
    command, notice = plan(url)
    if os.environ.get("A4P_REVEAL_DRY_RUN"):
        print(json.dumps({"command": command, "notice": notice}, ensure_ascii=False))
        return 0
    if command:
        subprocess.run(command, check=False)
    if notice:
        notify(notice)
    log(url, command, notice)
    return 0


if __name__ == "__main__":
    sys.exit(main())
