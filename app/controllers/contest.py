from datetime import datetime
from fastapi.responses import JSONResponse
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, aliased
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.models.role import Role
from app.util.role_checker import RoleChecker
from app.database import get_object_by_id
from app.models.mapping import User, ContestUser, Contest
from app.models.mapping import Problem, ContestProblem, ProblemConstraint, Language
from app.models.mapping import Submission, ContestSubmission, SubmissionTestCase
from app.schemas import (
    ContestListResponse, 
    Scoreboard, ContestInfo, ContestInfos, ContestUserInfo, 
    ProblemInfo, PastContest, UpcomingContest
)

def get_scoreboard(id: int, session: Session) -> Scoreboard:
    try:
        cs = aliased(ContestSubmission)
        s = aliased(Submission)
        stc = aliased(SubmissionTestCase)
        c = aliased(Contest)
        u = aliased(User)

        result = session.query(
            s.user_id,
            u.username,
            s.problem_id,
            func.max(s.score).label("max_score"))\
            .join(cs, cs.submission_id == s.id)\
            .join(c, c.id == cs.contest_id)\
            .join(stc, stc.submission_id == s.id)\
            .join(u, u.id == s.user_id)\
            .filter(c.id == id)\
            .filter(s.is_pretest_run == False)\
            .group_by(s.user_id, u.username, s.problem_id)\
            .order_by(s.user_id, s.problem_id)\
            .all()
        
        # create a list of problems resolved by each user and the total score
        user_scores = {}
        for user_id, username, problem_id, max_score in result:
            if username not in user_scores:
                user_scores[username] = {
                    "user_id": user_id,
                    "problems": {},
                    "total_score": 0
                }
            user_scores[username]["problems"][problem_id] = max_score
            user_scores[username]["total_score"] += max_score
        # sort the users by total score
        sorted_user_scores = sorted(user_scores.values(), key=lambda x: x["total_score"], reverse=True)

        # create the scoreboard
        return Scoreboard(rankings=sorted_user_scores)


    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))


def list_problems(id: int, user: User, session: Session) -> ContestListResponse:
    """
    List problems in a contest

    Args:
        id: int

    Returns:
        ListResponse: problems
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")

        is_admin_maintainer = RoleChecker.hasRole(user, Role.CONTEST_MAINTAINER)
        query = session.query(ContestProblem).filter(ContestProblem.contest_id == id)
        if not is_admin_maintainer:
            is_user = RoleChecker.hasRole(user, Role.USER)
            if is_user and user in contest.users:
                query = query.filter(
                    or_(
                        and_( # solo che contest in corso (basato su pub_delay) o se già finito
                            Contest.start_datetime <= datetime.now(),
                            Contest.end_datetime > datetime.now(),
                            ContestProblem.publication_delay <= (datetime.now() - Contest.start_datetime).total_seconds() / 60
                        ),
                        Contest.end_datetime <= datetime.now()
                    )
                )
            else: # solo se già finito (utente non iscritto al contest)
                query = query.filter(Contest.end_datetime <= datetime.now())

        contest_problems : List[ContestProblem] = query.all()

        return {"data": [ContestProblem.model_validate(obj=problem) for problem in contest_problems], "count": len(contest_problems)}

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def get_contest_info(session: Session, contests: List[Contest]) -> List[ContestInfo]:
    """Helper function to fetch contest details"""
    result = []
    for contest in contests:
        problems_count = session.query(ContestProblem).filter(ContestProblem.contest_id == contest.id).count()
        users_count = session.query(ContestUser).filter(ContestUser.contest_id == contest.id).count()
        submissions_count = session.query(ContestSubmission).filter(ContestSubmission.contest_id == contest.id).count()

        result.append(ContestInfo(
            id=contest.id,
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime,
            duration=int((contest.end_datetime - contest.start_datetime).total_seconds() / 3600),
            n_problems=problems_count,
            n_participants=users_count,
            n_submissions=submissions_count
        ))
    return result

def list_with_info(session: Session) -> ContestInfos:
    """List contests with additional data"""
    try:
        now = datetime.now()
        ongoing_contests = session.query(Contest).filter(Contest.start_datetime <= now, Contest.end_datetime > now, Contest.is_public == True).limit(5).all()
        past_contests = session.query(Contest).filter(Contest.end_datetime <= now, Contest.is_public == True).limit(5).all()
        upcoming_contests = session.query(Contest).filter(Contest.start_datetime > now, Contest.is_public == True).limit(5).all()

        return ContestInfos(
            ongoing=get_contest_info(session, ongoing_contests),
            past=get_contest_info(session, past_contests),
            upcoming=get_contest_info(session, upcoming_contests)
        )
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def read_past(id: int, session: Session):
    """
    Return a past contest by id

    Args:
        id: int
        session: Session

    Returns:
        contest: PastContest
    """
    try:
        contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        # check if it is a past contest
        if contest.end_datetime > datetime.now():
            raise HTTPException(status_code=400, detail="Contest is not yet finished")
        
        problems = session.query(Problem).join(ContestProblem, Problem.id == ContestProblem.problem_id).filter(ContestProblem.contest_id == id).all()
        problem_languages = session.query(ProblemConstraint).join(Language, ProblemConstraint.language_id == Language.id).filter(ProblemConstraint.problem_id.in_([problem.id for problem in problems])).all()

        languages = {}
        for problem_language in problem_languages:
            if problem_language.problem_id not in languages:
                languages[problem_language.problem_id] = []
            languages[problem_language.problem_id].append(problem_language.language_name)
        
        problems_info = []
        for problem in problems:
            problems_info.append(ProblemInfo(
                title=problem.title,
                points=problem.points,
                languages=languages[problem.id]
            ))
            
        user_infos = [ContestUserInfo.model_validate(obj=user) for user in contest.users]

        number_of_submissions = session.query(ContestSubmission).filter(ContestSubmission.contest_id == id).count()

        scoreboard = get_scoreboard(id, session)

        return PastContest(
            id=contest.id,
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime,
            duration=int((contest.end_datetime - contest.start_datetime).total_seconds() / 3600),
            n_submissions=number_of_submissions,
            problems=problems_info,
            scoreboard=scoreboard,
            users=user_infos
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

def read_upcoming(id: int, session: Session) -> UpcomingContest:
    """
    Return an upcoming contest by id

    Args:
        id: int
        session: Session

    Returns:
        contest: ContestRead
    """
    try:
        contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        # check if it is an upcoming contest
        if contest.start_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Contest has already started")
        
        problems = session.query(Problem).join(ContestProblem, Problem.id == ContestProblem.problem_id).filter(ContestProblem.contest_id == id).all()
        problem_languages = session.query(ProblemConstraint).join(Language, ProblemConstraint.language_id == Language.id).filter(ProblemConstraint.problem_id.in_([problem.id for problem in problems])).all()

        languages = {}
        
        for problem_language in problem_languages:
            if problem_language.problem_id not in languages:
                languages[problem_language.problem_id] = []
            languages[problem_language.problem_id].append(problem_language.language_name)
        
        problems_info = [ProblemInfo(title=problem.title, points=problem.points, languages=languages[problem.id]) for problem in problems]

        return UpcomingContest(
            id=contest.id,
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime,
            duration=int((contest.end_datetime - contest.start_datetime).total_seconds() / 3600),
            n_participants=len(contest.users),
            n_problems=len(problems),
            problems=problems_info,
            is_registration_open=contest.is_registration_open
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
def read_ongoing(id: int, user: User, session: Session):
    """
    Return an ongoing contest by id

    Args:
        id: int
        user: User
        session: Session

    Returns:
        contest: ContestRead
    """
    try:
        contest = session.query(Contest).filter(Contest.id == id).first()
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        # check if user is registered to the contest
        if user not in contest.users:
            raise HTTPException(status_code=400, detail="User is not registered to the contest")
        
        # check if it is an ongoing contest
        if contest.start_datetime > datetime.now() or contest.end_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Contest is not ongoing")
        
        now = datetime.now()

        # get all problems that has publication delay minor than the time passed since the start of the contest
        problems = session.query(Problem).join(ContestProblem, Problem.id == ContestProblem.problem_id).filter(
            ContestProblem.contest_id == id,
            ContestProblem.publication_delay <= (now - contest.start_datetime).total_seconds() / 60
        ).order_by(ContestProblem.publication_delay, Problem.title).all()

        # problems = session.query(Problem).join(ContestProblem, Problem.id == ContestProblem.problem_id).filter(ContestProblem.contest_id == id).all()
        problem_languages = session.query(ProblemConstraint).join(Language, ProblemConstraint.language_id == Language.id).filter(ProblemConstraint.problem_id.in_([problem.id for problem in problems])).all()

        languages = {}
        
        for problem_language in problem_languages:
            if problem_language.problem_id not in languages:
                languages[problem_language.problem_id] = []
            languages[problem_language.problem_id].append(problem_language.language_name)
        
        problems_info = [ProblemInfo(id=problem.id, title=problem.title, points=problem.points, languages=languages[problem.id], difficulty=problem.difficulty) for problem in problems]

        user_infos = [ContestUserInfo.model_validate(obj=user) for user in contest.users]

        number_of_submissions = session.query(ContestSubmission).filter(ContestSubmission.contest_id == id).count()

        scoreboard = get_scoreboard(id, session)

        return PastContest(
            id=contest.id,
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime,
            duration=int((contest.end_datetime - contest.start_datetime).total_seconds() / 3600),
            n_submissions=number_of_submissions,
            problems=problems_info,
            scoreboard=scoreboard,
            users=user_infos
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    

def register_to_contest(contest_id: int, user: User, session: Session):
    """
    Register a user to a contest

    Args:
        contest_id: int
        user: User
        session: Session
    """
    try:
        contest = session.query(Contest).filter(Contest.id == contest_id).first()

        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        if contest.is_registration_open == False:
            raise HTTPException(status_code=400, detail="Registration is closed")

        if contest.start_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Contest has already started")
        
        if contest.end_datetime < datetime.now():
            raise HTTPException(status_code=400, detail="Contest has already ended")
        
        if user in contest.users:
            return JSONResponse(status_code=200, content={"message": "User already registered to contest"})
        
        contest_user = ContestUser(contest_id=contest_id, user_id=user.id)
        session.add(contest_user)
        session.commit()

        return JSONResponse(status_code=200, content={"message": "User registered to contest successfully"})
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
