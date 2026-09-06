from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.model import Project
from app.modules.projects.repository import ProjectRepository
from app.modules.projects.schemas import (
    ProjectCreateRequest,
    ProjectUpdateRequest,
)
from app.modules.users.repository import UserRepository


class ProjectService:
    def __init__(
        self,
        session: AsyncSession,
        project_repository: ProjectRepository,
        user_repository: UserRepository,
    ):
        self.session = session
        self.project_repository = project_repository
        self.user_repository = user_repository

    async def get_all(self) -> list[Project]:
        return await self.project_repository.get_all()

    async def get_by_id(
        self,
        project_id: int,
    ) -> Project:
        project = await self.project_repository.get_by_id(
            project_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        return project

    async def create(
        self,
        data: ProjectCreateRequest,
    ) -> Project:
        project = Project(
            name=data.name.strip(),
            description=data.description,
        )

        self.project_repository.add(project)

        await self.session.commit()

        return await self.get_by_id(project.id)

    async def update(
        self,
        project_id: int,
        data: ProjectUpdateRequest,
    ) -> Project:
        project = await self.get_by_id(project_id)

        if data.name is not None:
            project.name = data.name.strip()

        if data.description is not None:
            project.description = data.description

        await self.session.commit()

        return await self.get_by_id(project.id)

    async def delete(
        self,
        project_id: int,
    ) -> None:
        project = await self.get_by_id(project_id)

        await self.project_repository.delete(project)

        await self.session.commit()

    async def assign_members(
        self,
        project_id: int,
        user_ids: list[int],
    ) -> Project:
        project = await self.get_by_id(project_id)

        users = []

        for user_id in user_ids:
            user = await self.user_repository.get_by_id(
                user_id,
            )

            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User {user_id} not found.",
                )

            users.append(user)

        project.users = users

        await self.session.commit()

        return await self.get_by_id(project.id)