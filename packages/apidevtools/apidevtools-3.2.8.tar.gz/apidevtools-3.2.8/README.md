## Overview
## Documentation
## Installation
```
pip install apidevtools
```
### Package dependencies
```
pip install pydantic loguru pillow numpy argon2-cffi cryptography aiohttp
```
speedups
```
pip install aiodns ujson cchardet uvloop
```
### Per module dependencies
- simpleorm
    - orm
        ```
        pip install pydantic loguru
        ```
        - connectors
            - mysql ```pip install aiomysql```
            - postgresql ```pip install asyncpg```
            - sqlite ```pip install aiosqlite```
    - nosql
        - redis ```pip install aioredis```
- security
    - hasher
        ```
        pip install argon2-cffi
        ```
    - encryptor
        ```
        pip install cryptography
        ```
- media
    - imgproc
        ```
        pip install pillow numpy
        ```
    - telegraph
        ```
        pip install aiohttp
        ```
- logman
    ```
    pip install loguru
    ```
