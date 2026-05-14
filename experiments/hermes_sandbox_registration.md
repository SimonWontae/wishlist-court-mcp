# Hermes sandbox 등록 결과

이 문서는 sandbox 안에서 Hermes MCP 등록을 수행한 결과를 기록한다.

## 등록 방식

기본 Hermes 설정 경로인 `/home/ubtwt/.hermes`는 sandbox 밖에 있으므로, 프로젝트 내부 `.hermes`를 Hermes home으로 지정했다.

```bash
export HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes
```

정상 MCP 등록:

```bash
printf 'y\n' | HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp add wishlist-court \
  --command /home/ubtwt/Projects/wishilist-court-mcp/.venv/bin/python \
  --args /home/ubtwt/Projects/wishilist-court-mcp/src/wishlist_court_server.py
```

망가진 MCP 등록:

```bash
printf 'y\n' | HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp add wishlist-court-broken \
  --command /home/ubtwt/Projects/wishilist-court-mcp/.venv/bin/python \
  --args /home/ubtwt/Projects/wishilist-court-mcp/src/broken_wishlist_court_server.py
```

## 등록 확인

```bash
HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp list
```

확인 결과:

| 이름 | 상태 |
| --- | --- |
| `wishlist-court` | enabled |
| `wishlist-court-broken` | enabled |

설정 파일:

- `.hermes/config.yaml`

## sandbox 제한

`hermes mcp add`의 discovery 연결 테스트와 `hermes mcp test`는 sandbox 안에서 stdio 응답을 받지 못해 타임아웃됐다.

따라서 등록 단계에서는 타임아웃 후 `Save config anyway`에 `y`로 응답해 설정을 저장했고, 이후 `.hermes/config.yaml`에서 두 서버의 `enabled` 값을 `true`로 설정했다.

일반 터미널에서 실제 실행할 때는 아래 명령으로 다시 테스트한다.

```bash
HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp test wishlist-court

HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes mcp test wishlist-court-broken
```

실제 채팅 실행 예:

```bash
HERMES_HOME=/home/ubtwt/Projects/wishilist-court-mcp/.hermes \
  /home/ubtwt/.local/bin/hermes chat
```
