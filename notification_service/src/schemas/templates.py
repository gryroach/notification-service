# stdlib
from uuid import UUID

# thirdparty
from jinja2 import Environment, TemplateSyntaxError
from pydantic import BaseModel, field_validator


class TemplateCreate(BaseModel):
    name: str
    subject: str
    body: str
    staff_id: UUID

    @field_validator("body")
    @classmethod
    def body_validate(cls, v: str) -> str:
        env = Environment()
        try:
            env.parse(v)
        except TemplateSyntaxError as e:
            raise ValueError(f"Invalid template body {e}") from e
        return v


class TemplateUpdate(TemplateCreate):
    pass


class TemplateResponse(BaseModel):
    id: UUID
    name: str
    subject: str
    body: str
    staff_id: UUID

    class Config:
        from_attributes = True
