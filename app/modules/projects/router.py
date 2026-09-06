from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.auth.security import get_current_user, require_roles
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import ProjectCreateRequest, ProjectMemberUpdateRequest, ProjectResponse, ProjectUpdateRequest
from app.modules.projects.service import ProjectService
from app.modules.users.model import User
from app.modules.users.repository import UserRepository


router = APIRouter(prefix="/projects", tags=["Projects"])


def get_project_service(session: AsyncSession) -> ProjectService:
    return ProjectService(session, ProjectRepository(session), UserRepository(session))


@router.get("", response_model=list[ProjectResponse])
async def get_projects(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[ProjectResponse]:
    return await get_project_service(session).get_all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ProjectResponse:
    return await get_project_service(session).get_by_id(project_id)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> ProjectResponse:
    return await get_project_service(session).create(data)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> ProjectResponse:
    return await get_project_service(session).update(project_id, data)


@router.put("/{project_id}/members", response_model=ProjectResponse)
async def assign_project_members(
    project_id: int,
    data: ProjectMemberUpdateRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> ProjectResponse:
    return await get_project_service(session).assign_members(project_id, data.user_ids)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> Response:
    await get_project_service(session).delete(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)