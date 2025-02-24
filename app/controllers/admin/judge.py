from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from hashlib import sha256
from app.models.mapping import User, UserType
from app.models.role import Role
from app.schemas import JudgeResponse, JudgeCreate, JudgeListResponse


def get_judges(limit : int, offset : int, searchFilter: str, session: Session) -> JudgeListResponse:
    """
    Get the judge list
    """

    try:
        # get the judge list
        judge_role: UserType = session.query(UserType).filter(UserType.permissions == Role.JUDGE).one_or_none()

        if not judge_role:
            raise HTTPException(status_code=404, detail="Judge role not found")
        
        query = session.query(User).where(User.user_type_id == judge_role.id)
        if searchFilter:
            query = query.filter(User.username.ilike(f"%{searchFilter}%"))
        
        
        count = query.count()
        judges = query.limit(limit).offset(offset).all()

        dto = []
        for judge in judges:
            # check if the registration date is less than 30 minutes
            status = False
            if judge.registered_at > datetime.now() - timedelta(minutes=30):
                status = True
            dto.append(JudgeResponse(id=judge.id, name=judge.username, status=status, last_connection=judge.registered_at))
        
        return JudgeListResponse(judges=dto, count=count)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def create_judge(judge: JudgeCreate, session: Session):
    """
    Create a new judge
    """

    try:
        # get the judge type
        judge_type = session.query(UserType).filter(UserType.permissions == Role.JUDGE).one_or_none()

        existing = session.query(User).where(User.username == judge.name).one_or_none()

        if existing:
            raise HTTPException(status_code=400, detail="Judge already exists")

        if not judge_type:
            raise HTTPException(status_code=500, detail="Judge type not found in the database")

        hash = sha256(f'{judge.name}:{judge.key}'.encode()).hexdigest()
        # create the judge
        new_judge = User(
            username=judge.name,
            email=judge.name,
            user_type_id=judge_type.id,
            password_hash=hash,
            salt='',
            deletion_date=None
        )

        session.add(new_judge)
        session.commit()
        return {"message": "Judge added successfully"}, 201

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def delete_judge(id: int, session: Session):
    """
    Delete a judge
    
    Args:
        id: int
    """
    try:
        # get the judge
        judge = session.query(User).where(User.id == id).one_or_none()

        if not judge:
            raise HTTPException(status_code=404, detail="Judge not found")

        # delete the judge
        session.delete(judge)
        session.commit()
        
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
