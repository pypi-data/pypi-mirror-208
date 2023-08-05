from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import const, routers


app = FastAPI(
    title=const.API_TITLE,
    description=const.API_DESCRIPTION,
    version=const.API_VERSION,
    contact={
        'name': const.API_CONTACT_NAME,
        'url': const.API_CONTACT_URL,
        'email': const.API_CONTACT_EMAIL
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=const.API_CORS_ORIGINS,
    allow_methods=const.API_CORS_METHODS,
    allow_headers=const.API_CORS_HEADERS,
    allow_credentials=const.API_CORS_ALLOW_CREDENTIALS
)

app.include_router(routers.auth_router)
app.include_router(routers.user_router)
app.include_router(routers.item_router)


@app.on_event('startup')
async def startup():
    if await const.db.create_pool():
        # with open('api/build/init.sql', 'r') as file:
        with open('apidevtools/template/template/api/build/init.sql', 'r') as file:
            await const.db.execute(file.read())


@app.on_event('shutdown')
async def shutdown():
    await const.db.close_pool()
