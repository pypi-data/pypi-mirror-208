from apidevtools import Schema, Relation

from .item import Item


class UserBase(Schema):
    __tablename__ = 'user'

    email: str
    avatar_url: str = None

    def pretty(self) -> Schema:
        self.email = self.email.lower()
        return self


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    items: list[Item] = []

    def relations(self) -> list[Relation]:
        return [
            Relation('item', dict(user_id=self.id), User, 'items', Item, ['*']),
        ]
