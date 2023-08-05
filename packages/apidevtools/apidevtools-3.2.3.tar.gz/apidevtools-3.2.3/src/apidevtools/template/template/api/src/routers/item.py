from fastapi import APIRouter, Depends, HTTPException
from apidevtools import inf

from .. import crud, schemas


router = APIRouter(tags=['Item'])


@router.post('/items/', name='Create item', response_model=schemas.Item)
async def _(item: schemas.ItemCreate,
            user: schemas.User = Depends(crud.get_current_user)):
    db_item = await crud.create_item(user_id=user.id, item=item)
    return db_item


@router.get('/items/{item_id}/', name='Get item by id', response_model=schemas.Item)
async def _(item_id: int,
            user: schemas.User = Depends(crud.get_current_user)):
    db_item = await crud.get_item(item_id=item_id)
    return db_item


@router.get('/users/{user_id}/items/', name='Get all items by user id', response_model=list[schemas.Item])
async def _(user_id: int, limit: int = inf, offset: int = 0,
            user: schemas.User = Depends(crud.get_current_user)):
    db_user = await crud.get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=f'User <{user_id}> not found')
    db_items = await crud.get_items(user_id=user_id, limit=limit, offset=offset)
    return db_items


@router.put('/items/', name='Update item by id', response_model=schemas.Item)
async def _(item_id: int, item: schemas.ItemCreate,
            user: schemas.User = Depends(crud.get_current_user)):
    db_user = await crud.update_item(item_id=item_id, item=item)
    return db_user


@router.delete('/items/', name='Delete item by id', response_model=schemas.Item)
async def _(item_id: int,
            user: schemas.User = Depends(crud.get_current_user)):
    db_item = await crud.delete_item(item_id=item_id)
    return db_item
