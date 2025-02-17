from fastapi import APIRouter, Depends, HTTPException

from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.util.jwt import get_current_user

from app.schemas import ProblemRead
from app.database import get_session

router = APIRouter(
    tags=["Problems"],
    prefix="/problems"
)


