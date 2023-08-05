from apidevtools import Schema


class ItemBase(Schema):
    __tablename__ = 'item'

    title: str
    description: str = None

    def pretty(self) -> 'Schema':
        self.title = self.title.capitalize()
        return self


class ItemCreate(ItemBase):
    ...


class ItemCreateCrud(ItemBase):
    user_id: int


class Item(ItemCreateCrud):
    id: int
    