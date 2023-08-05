from apidevtools.media import processing
from apidevtools.security import hasher
from apidevtools import inf

from .. import schemas
from ..const import db


async def create_user(user: schemas.UserCreate) -> schemas.User:
    user.password = hasher.hash(password=user.password)
    if not user.avatar_url:
        user.avatar_url = await avatar.default().url()
    db_user = await db.insert(user, schemas.User)
    return db_user


async def get_user(user_id: int = None, email: str = None, schema: type = schemas.User) -> schemas.User | None:
    field, value = ('email', email) if email else ('id', user_id)
    query, args = f'SELECT * FROM "user" WHERE "{field}" = $1;', (value, )
    db_user = (await db.select(query, args, schema, reldepth=1)).first()
    return db_user


async def get_users(limit: int = inf, offset: int = 0, schema: type = schemas.User) -> list[schemas.User]:
    query, args = 'SELECT * FROM "user" LIMIT $1 OFFSET $2;', (limit, offset)
    db_users = (await db.select(query, args, schema, reldepth=1)).all()
    return db_users


async def update_user(user_id: int, user: schemas.UserCreate) -> schemas.User:
    db_user = await get_user(user_id=user_id, schema=schemas.User)
    user.avatar_url = db_user.avatar_url if not user.avatar_url else user.avatar_url
    # user = schemas.User(**dict(user))
    db_user = await db.update(user, dict(id=user_id), schemas.User)
    return db_user


async def delete_user(user_id: int) -> schemas.User:
    db_user = await db.delete(dict(id=user_id), schemas.User, 'user')
    return db_user
