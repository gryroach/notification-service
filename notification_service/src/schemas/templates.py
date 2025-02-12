# stdlib
from uuid import UUID

# thirdparty
from pydantic import BaseModel


class CreateTemplate(BaseModel):
    name: str
    subject: str
    body: str


class UpdateTemplate(BaseModel):
    name: str | None
    subject: str | None
    body: str | None


class TemplateDB(BaseModel):
    id: UUID
    name: str
    subject: str
    body: str
