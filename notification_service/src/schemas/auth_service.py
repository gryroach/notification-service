# stdlib
from datetime import date

# thirdparty
from pydantic import BaseModel


class UserData(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    birth_date: date | None
    phone: str | None
    avatar: str | None
