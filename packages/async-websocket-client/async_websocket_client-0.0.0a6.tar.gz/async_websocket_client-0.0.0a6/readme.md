# WebSockets Groups

Модуль реализующих менеджер групп WebSocket подключений

[![PyPI](https://img.shields.io/pypi/v/async-websocket-client)](https://pypi.org/project/async-websocket-client/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/async-websocket-client)](https://pypi.org/project/async-websocket-client/)
[![GitLab last commit](https://img.shields.io/gitlab/last-commit/rocshers/python/async-websocket-client)](https://gitlab.com/rocshers/python/async-websocket-client)

[![Test coverage](https://codecov.io/gitlab/rocshers:python/async-websocket-client/branch/release/graph/badge.svg?token=RPFNZ8SBQ6)](https://codecov.io/gitlab/rocshers:python/async-websocket-client)
[![Downloads](https://static.pepy.tech/badge/async-websocket-client)](https://pepy.tech/project/async-websocket-client)
[![GitLab stars](https://img.shields.io/gitlab/stars/rocshers/python/async-websocket-client)](https://gitlab.com/rocshers/python/async-websocket-client)

## Functionality

- Регистрация / Удаление WS
- Создание / Удаление групп WS
- Подключение WS в группу
- Поддержка реестров: memory, redis

## Quick start

Установка:

```sh
pip install websockets-groups
```

Подключение:

```python
from fastapi import WebSocket
from websockets_groups import WSGroupsManager, MemoryStorage, BaseDispatcher

ws_groups_manager = WSGroupsManager(MemoryStorage())

class ChatDispatcher(BaseDispatcher):
    pass

@app.websocket('/chats/')
async def ws_view(webdocket: WebSocket, chat_name: str):
    await ws_groups_manager.register_ws(websocket, ChatDispatcher())
```
