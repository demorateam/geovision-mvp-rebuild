from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import User


class UserRepository:
    """Data access for User records."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_phone(self, phone: str) -> User | None:
        return self.db.scalar(select(User).where(User.phone == phone))

    def add(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
