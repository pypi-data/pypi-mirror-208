from fastapi import APIRouter, Depends, HTTPException
from apidevtools import inf
from apidevtools.security import hasher

from .. import crud, schemas
from ..const import db


router = APIRouter(tags=['User'])


@router.post('/users/', name='Create user', response_model=dict)
async def _(user: schemas.UserCreate):
    db_user = await crud.get_user(email=user.email, schema=schemas.UserCreate)
    if db_user:
        raise HTTPException(status_code=400, detail=f'Email <{user.email}> already registered')
    db_user = await crud.create_user(user=user)
    return dict(**(await crud.create_token(user=db_user)), user=db_user.dict())


@router.get('/users/{user_id}/', name='Get user by id', response_model=schemas.User)
async def _(user_id: int):
    db_user = await crud.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f'User <{user_id}> not found')
    return db_user


@router.get('/users/', name='Get all users', response_model=list[schemas.User])
async def _(limit: int = inf, offset: int = 0):
    db_users = await crud.get_users(limit=limit, offset=offset)
    return db_users


@router.put('/users/', name='Update my user', response_model=schemas.User)
async def _(user: schemas.UserCreate,
            _user: schemas.User = Depends(crud.get_current_user)):
    db_user = await crud.update_user(user_id=_user.id, user=user)
    return db_user


@router.delete('/users/', name='Delete my user', response_model=schemas.User)
async def _(user: schemas.User = Depends(crud.get_current_user)):
    db_user = await crud.delete_user(user_id=user.id)
    return db_user


@router.put('/users/password/', name='Update user\'s password', response_model=schemas.User)
async def _(password: str, user: schemas.UserCreate,
            _user: schemas.User = Depends(crud.get_current_user)):
    query, args = 'SELECT * FROM "user" WHERE "id" = $1;', (_user.id, )
    db_user = (await db.select(query, args, schemas.User)).first()
    if not hasher.cmp(db_user.password, password):
        raise HTTPException(status_code=401, detail='Invalid password')
    db_user.password = hasher.hash(user.password)
    db_user = await db.update(db_user, dict(id=db_user.id), schemas.User)
    return db_user
