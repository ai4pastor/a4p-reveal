# A4P Finder에서 보기 (a4p-reveal)

herdr 칸에서 Claude가 알려 준 파일 경로를 **⌃(Control)+클릭**하면 Finder 창이 뜨고 그 파일이 선택된 채로 보입니다.
생성한 이미지를 복사하거나, 지우거나, 다른 앱으로 끌어다 놓을 때 씁니다. 바로 열기는 지금처럼 **⌘+⇧+클릭**입니다.

파일을 만들거나 고치거나 지우지 않습니다(읽기 전용). 기록 파일 하나만 플러그인 상태 폴더에 남깁니다.

## 쓰는 법

- Claude가 결과 파일 경로를 보여 주면, 그 경로 글자를 ⌃를 누른 채 클릭합니다.
- 파일이 지워졌으면 남아 있는 가장 가까운 폴더를 열고, herdr 알림으로 이유를 알려 줍니다.
- ⌃를 누르고 마우스를 올려도 밑줄은 생기지 않습니다(herdr는 웹 주소에만 밑줄을 긋습니다). 클릭은 됩니다.

## 작동 조건 — 세 가지가 모두 있어야 합니다

1. **이 플러그인**: 이 폴더에서 `herdr plugin link "$PWD"`
2. **herdr 칸에서 숨은 링크(OSC 8) 켜기** — `~/.zshrc` 에 한 줄:

   ```sh
   [[ "$TERM_PROGRAM" == herdr ]] && export FORCE_HYPERLINK=1
   ```

   Claude Code는 터미널 이름이 정해진 목록(ghostty·iTerm 등)에 있을 때만 숨은 링크를 찍는데, herdr 칸의 이름(`herdr`)은 목록에 없습니다. 이미 떠 있는 Claude는 다시 열어야 적용됩니다.
3. **Claude가 경로를 마크다운 링크로 적기** — `CLAUDE.md` 에:

   ```text
   결과 파일 경로는 [~/경로](file:///Users/<사용자>/경로) 처럼 마크다운 링크로 적는다.
   보이는 글자는 경로 그대로 두고, 괄호 안 주소는 file:/// 로 시작하는 전체 경로로 쓴다(한글은 그대로 써도 된다).
   ```

## 왜 ⌘가 아니라 ⌃인가

herdr가 마우스를 잡고 있는 동안에는 ⌘+클릭이 일반 클릭과 구분되지 않아서, herdr 링크 처리기는 맥에서도 ⌃+클릭을 씁니다.
⌘+⇧+클릭은 ⇧ 때문에 herdr를 건너뛰고 Ghostty가 직접 처리해서 파일을 바로 엽니다.

## 확인과 문제 해결

- 실행 기록: `herdr plugin log --plugin a4p-reveal`
- 클릭한 주소 기록: `~/.local/state/herdr/plugins/a4p-reveal/reveal.log`
- 시험: `/usr/bin/python3 -I -m unittest discover -s tests`
- 할 일만 보기(실행 안 함): `A4P_REVEAL_DRY_RUN=1 HERDR_PLUGIN_CLICKED_URL='file:///…' ./reveal.py`

## 라이선스

MIT
