from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm as OAuth2Form

from .. import crud, schemas


router = APIRouter(tags=['AUTH'])


@router.post('/auth/token/', name='Generate token', response_model=dict[str, str])
async def _(form: OAuth2Form = Depends(OAuth2Form)):
    db_user = await crud.authenticate_user(email=form.username, password=form.password)
    if not db_user:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    return await crud.create_token(user=db_user)


@router.get('/users/current/', name='Get current user', response_model=schemas.User)
async def _(user: schemas.User = Depends(crud.get_current_user)):
    if not user:
        raise HTTPException(status_code=401, detail='Unauthorized')
    return user
