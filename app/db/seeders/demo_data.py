import asyncio

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import AsyncSessionFactory
from app.modules.auth.security import hash_password
from app.modules.projects.model import Project
from app.modules.users.model import User


USERS = [
    {
        "name": "Admin User",
        "email": "admin@example.com",
        "password": "Admin1234",
        "role": "ADMIN",
    },
    {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "John1234",
        "role": "TEAM_MEMBER",
    },
    {
        "name": "Test Manager",
        "email": "manager@example.com",
        "password": "Manager123",
        "role": "MANAGER",
    },
]

PROJECT_NAME = "Weekly Report System"


async def seed_user(session, data: dict) -> User:
    result = await session.execute(
        select(User).where(User.email == data["email"])
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            name=data["name"],
            email=data["email"],
            password_hash=hash_password(data["password"]),
            role=data["role"],
            is_active=True,
        )
        session.add(user)
        await session.flush()

        print(f'Created user: {data["email"]}')
        return user

    user.name = data["name"]
    user.password_hash = hash_password(data["password"])
    user.role = data["role"]
    user.is_active = True

    print(f'Updated user: {data["email"]}')
    return user


async def seed_project(session, member: User) -> Project:
    result = await session.execute(
        select(Project)
        .options(selectinload(Project.users))
        .where(Project.name == PROJECT_NAME)
    )
    project = result.scalar_one_or_none()

    if project is None:
        project = Project(
            name=PROJECT_NAME,
            description=None,
            users=[member],
        )
        session.add(project)
        await session.flush()

        print(f"Created project: {PROJECT_NAME}")
        print(f"Assigned {member.email} to {PROJECT_NAME}")

        return project

    if all(user.id != member.id for user in project.users):
        project.users.append(member)
        print(f"Assigned {member.email} to {PROJECT_NAME}")
    else:
        print(f"{member.email} is already assigned to {PROJECT_NAME}")

    return project


async def main() -> None:
    async with AsyncSessionFactory() as session:
        try:
            seeded_users = {}

            for data in USERS:
                user = await seed_user(session, data)
                seeded_users[data["email"]] = user

            await seed_project(
                session,
                seeded_users["john@example.com"],
            )

            await session.commit()
            print("Demo data seeded successfully.")

        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())