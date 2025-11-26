from sqlalchemy.orm import Mapped, mapped_column

from database import BaseModel, intpk, created_at, updated_at


class Client(BaseModel):
    __tablename__ = "clients"

    id: Mapped[intpk]
    phone_number: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]