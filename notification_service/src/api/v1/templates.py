# stdlib
from typing import Annotated
from uuid import UUID

# thirdparty
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

# project
from api.v1.pagination import PaginationParams
from db.db import get_session
from repositories.sql.template import TemplateRepository
from schemas.auth import JwtToken
from schemas.templates import TemplateCreate, TemplateResponse, TemplateUpdate
from services.jwt_token import JWTBearer

router = APIRouter()


@router.post(
    "/",
    response_model=TemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_template(
    name: Annotated[str, Form(...)],
    subject: Annotated[str, Form(...)],
    body: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
) -> TemplateResponse:
    try:
        body_content = await body.read()
        body_text = body_content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The template-file cannot be decoded to text (UTF-8).",
        )
    try:
        template = TemplateCreate(name=name, subject=subject, body=body_text, staff_id=token_payload.user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    repo = TemplateRepository(db)
    db_template = await repo.create(obj_in=template)
    return TemplateResponse.model_validate(db_template)


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    dependencies=[Depends(JWTBearer())],
)
async def get_template(
    template_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> TemplateResponse:
    repo = TemplateRepository(db)
    db_template = await repo.get(template_id)
    if db_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return TemplateResponse.model_validate(db_template)


@router.put(
    "/{template_id}",
    response_model=TemplateResponse,
)
async def update_template(
    template_id: UUID,
    name: Annotated[str, Form(...)],
    subject: Annotated[str, Form(...)],
    body: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[JwtToken, Depends(JWTBearer())],
) -> TemplateResponse:
    repo = TemplateRepository(db)
    db_template = await repo.get(template_id)
    if db_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    try:
        body_content = await body.read()
        body_text = body_content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The template-file cannot be decoded to text (UTF-8).",
        )
    try:
        template = TemplateUpdate(name=name, subject=subject, body=body_text, staff_id=token_payload.user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    db_template = await repo.update(db_obj=db_template, obj_in=template)
    return TemplateResponse.model_validate(db_template)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(JWTBearer())],
)
async def delete_template(
    template_id: UUID,
    db: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    repo = TemplateRepository(db)
    db_template = await repo.delete(template_id)
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )


@router.get(
    "/",
    response_model=list[TemplateResponse],
    dependencies=[Depends(JWTBearer())],
)
async def get_all_templates(
    pagination_params: Annotated[PaginationParams, Depends()],
    db: Annotated[AsyncSession, Depends(get_session)],
) -> list[TemplateResponse]:
    repo = TemplateRepository(db)
    templates = await repo.get_multi(
        skip=(pagination_params.page_number - 1) * pagination_params.page_size,
        limit=pagination_params.page_size,
    )
    return [TemplateResponse.model_validate(db_template) for db_template in templates]
