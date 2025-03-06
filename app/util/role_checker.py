from typing import Annotated
from app.models.mapping import User
from fastapi import Depends, HTTPException
from app.util.jwt import get_current_user, get_judge
from app.models.role import Role

#TODO: merged stuff + TO_TEST every endpoint
class RoleChecker:
    def __init__(self, allowed_roles : list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_current_user)]):
        for required_role in self.allowed_roles:
            if user.user_type.permissions & required_role == required_role:    
                return True
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")

    @staticmethod
    def hasRole(user: User, required_role: Role) -> bool:
        return (user.user_type.permissions & required_role) == required_role

class JudgeChecker:
    def __init__(self):
        pass
    def __call__(self, judge: Annotated[User, Depends(get_judge)]):
        if judge:
            return True
        raise HTTPException(status_code=403, detail="You do not have permission to perform this action")