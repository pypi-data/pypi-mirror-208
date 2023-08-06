## Overview
## Documentation
## Installation
```
pip install apidevtools
```
### Package dependencies
includes ```None```

speedups ```pip install aiodns ujson cchardet uvloop```

depending on modules [optional] ```pip install pydantic loguru pillow numpy argon2-cffi cryptography aiohttp```

### Per module dependencies
- simpleorm
    - orm ```pip install pydantic loguru```
        - connectors
            - mysql ```pip install aiomysql```
            - postgresql ```pip install asyncpg```
            - sqlite ```pip install aiosqlite```
    - redis ```pip install aioredis```
- security
    - hasher ```pip install argon2-cffi```
    - encryptor ```pip install cryptography```
- media
    - imgproc ```pip install pillow numpy```
    - telegraph ```pip install aiohttp```
- logman ```pip install loguru```
