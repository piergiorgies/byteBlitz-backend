from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.mapping import Contest, Problem, Submission, User
from app.schemas.general import Statistics

def get_dashboard_stats(session: Session):
    """
    Get dashboard statistics
    """
    try:
        users = session.query(User).count()

        problems = session.query(Problem).filter(Problem.is_public == True).count()

        contests = session.query(Contest).count()

        submissions = session.query(Submission).count()

        return Statistics(
            users=users,
            problems=problems,
            contests=contests,
            submissions=submissions
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))