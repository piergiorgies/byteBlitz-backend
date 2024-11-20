from typing import Annotated
from app.models import User
from fastapi import Depends, HTTPException
from app.auth_util.jwt import get_current_user, get_judge

class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_current_user)]):
        if user.user_type.code in self.allowed_roles:
            return True
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")

class JudgeChecker:
    def __init__(self):
        pass
    def __call__(self, judge: Annotated[User, Depends(get_judge)]):
        if judge:
            return True
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
