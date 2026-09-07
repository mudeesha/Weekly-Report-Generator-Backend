from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.modules.ai.repository import AIRepository
from app.modules.ai.schemas import AIChatRequest, AIChatResponse
from app.modules.ai.service import AIService
from app.modules.auth.security import require_roles
from app.modules.users.model import User


router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.post("/chat", response_model=AIChatResponse)
async def chat(
    data: AIChatRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    current_user: Annotated[User, Depends(require_roles("MANAGER", "ADMIN"))],
) -> AIChatResponse:
    return await AIService(AIRepository(session)).chat(data)