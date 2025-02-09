from datetime import datetime
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from typing import List

from app.models.role import Role
from app.auth_util.role_checker import RoleChecker
from app.database import get_object_by_id
from app.models import ContestScoreboardDTO, Contest, ListResponse
from app.models import User, ContestUser
# from app.models import Team, ContestTeamDTO
from app.models import Problem, ContestProblem
from app.models import Submission, ContestSubmission
from app.models import ContestCreate, ContestUpdate, ContestRead, ContestScoreboard

#region Contest
def create(contest: ContestCreate, session: Session):
    """
    Create a contest
    
    Args:
        session: Session
        contest: ContestDTO
    
    Returns:
        ContestDTO: contest
    """
    try:
        if contest.start_datetime >= contest.end_datetime:
            raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")
        
        created_contest = Contest(
            name=contest.name,
            description=contest.description,
            start_datetime=contest.start_datetime,
            end_datetime=contest.end_datetime,
        )
        for i in range(contest.user_ids):
            user: User = get_object_by_id(User, session, contest.user_ids[i])
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            created_contest.users.append(user)
        
        for i in range(contest.problems):
            problem: Problem = get_object_by_id(Problem, session, contest.problems[i].problem_id)
            if not problem:
                raise HTTPException(status_code=404, detail="Problem not found")
            contest_problem = ContestProblem(
                contest_id=created_contest.id,
                problem_id=problem.id,
                publication_delay=contest.problems[i].publication_delay
            )
            created_contest.contest_problems.append(contest_problem)

        session.add(created_contest)
        session.commit()

        return contest
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def list(limit : int, offset : int, searchFilter: str, user : User, session : Session) -> ListResponse:
    """
    List contests
    
    Args:
        limit: limit in sql query
        offset: offset in sql query
        user: User
        session: Session
    
    Returns:
        [ContestDTO]: contests
    """
    try:
        is_admin_maintainer = RoleChecker.hasRole(user, Role.CONTEST_MAINTAINER)
        query = session.query(Contest)
        if not is_admin_maintainer:
            is_user = RoleChecker.hasRole(user, Role.USER)
            if is_user:
                query = query.filter(
                    or_(
                        Contest.users.any(User.id == user.id),
                        Contest.end_datetime <= datetime.now()
                    )
                )
            else:
                query = query.filter(Contest.end_datetime <= datetime.now())

        if searchFilter:
            query = query.filter(Contest.name.ilike(f"%{searchFilter}%"))
        query.join(Contest.contest_problems)
        count = query.count()
        query = query.limit(limit).offset(offset)
        contests : List[Contest] = query.all()

        return {"data": [ContestRead.model_validate(obj=obj) for obj in contests], "count": count}
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def read(id: int, user: User, session: Session) -> ContestRead:
    """
    Get contest by id
    
    Args:
        id: int

    Returns:
        ContestDTO: contest
    """

    try:
        is_admin_maintainer = RoleChecker.hasRole(user, Role.CONTEST_MAINTAINER)
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        if not is_admin_maintainer:
            is_user = RoleChecker.hasRole(user, Role.USER)
            if not is_user and contest.end_datetime > datetime.now():
                raise HTTPException(status_code=403, detail="You do not have permission to view this contest")
            elif is_user and user not in contest.users:
                raise HTTPException(status_code=403, detail="You do not have permission to view this contest")
        
        return ContestRead.model_validate(obj=contest)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def delete(id: int, session: Session) -> bool:
    """
    Delete contest by id

    Args:
        id: int
    
    Returns:
        bool: deleted
    """

    try:
        contest: Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
        
        session.delete(contest)
        session.commit()
        return True
    
    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
def update(id: int, contest_update: ContestUpdate, session: Session):
    """
    Update contest by id

    Args:
        id: int
        contest_update: ContestUpdate
        session: Session

    Returns:
        ContestRead: Updated contest
    """
    try:
        contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")

        if contest_update.start_datetime and contest_update.end_datetime:
            if contest_update.start_datetime > contest_update.end_datetime:
                raise HTTPException(status_code=400, detail="Start time cannot be greater than end time")

        if contest_update.name:
            contest.name = contest_update.name

        if contest_update.description:
            contest.description = contest_update.description

        if contest_update.start_datetime:
            contest.start_datetime = contest_update.start_datetime

        if contest_update.end_datetime:
            contest.end_datetime = contest_update.end_datetime

        if contest_update.user_ids is not None:
            users = session.query(User).filter(User.id.in_(contest_update.user_ids)).all()
            if len(users) != len(contest_update.user_ids):
                raise HTTPException(status_code=404, detail="One or more users not found")
            contest.users = users

        if contest_update.problems is not None:
            session.query(ContestProblem).filter(ContestProblem.contest_id == contest.id).delete()

            problem_ids = [p.problem_id for p in contest_update.problems]
            problems = session.query(Problem).filter(Problem.id.in_(problem_ids)).all()

            if len(problems) != len(problem_ids):
                raise HTTPException(status_code=404, detail="One or more problems not found")
            
            contest_duration = (contest.end_datetime - contest.start_datetime).total_seconds()
            for item in contest_update.problems:
                if item.publication_delay > contest_duration / 60:
                    raise HTTPException(status_code=400, detail="Problem publication delay is greater than contest duration")
                else:
                    contest.contest_problems.append(
                        ContestProblem(
                            contest_id=contest.id,
                            problem_id=item.problem_id,
                            publication_delay=item.publication_delay
                        )
                    )

        session.commit()
        session.refresh(contest)
        return ContestRead.model_validate(obj=contest)

    except SQLAlchemyError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")

#endregion

#region Contest Scoreboard

def get_scoreboard(id: int, session: Session) -> ContestScoreboardDTO:
    """
    Get the current scoreboard for a specific contest
    
    Args:
        id (int): the id of the related contest
        session (Session):
    
    Returns:
        [ContestScoreboardDTO]: current scoreboard for the given contest
    """

    try:
        contest : Contest = get_object_by_id(Contest, session, id)
        if not contest:
            raise HTTPException(status_code=404, detail="Contest not found")
 
        # get all problems (sorted) in the contest
        problems = session.query(ContestProblem, Problem.title).join(Problem, ContestProblem.problem_id == Problem.id).filter(ContestProblem.contest_id == id, Problem.is_public == True).order_by(ContestProblem.publication_delay, Problem.title).all()
        titles = [title for _, title in problems]
        if not problems:
            raise HTTPException(status_code=404, detail="There are no problems for this contest")

        # get all users in the contest
        users = session.query(ContestUser, User.username).join(User, ContestUser.user_id == User.id).filter(ContestUser.contest_id == id).all()
        scores : dict[str, List[int]] = {username: [0] * len(problems) for _, username in users}
        if not users:
            raise HTTPException(status_code=404, detail="There are no users for this contest")

        # for each user, get the best submissions for each problem
        for contest_user, username in users:
            for i, (contest_problem, _) in enumerate(problems):
                best_submission = session.query(ContestSubmission, Submission.score).join(Submission, ContestSubmission.submission_id == Submission.id).filter(ContestSubmission.contest_id == id, Submission.user_id == contest_user.user_id, Submission.problem_id == contest_problem.problem_id).order_by(Submission.score.desc()).first()
                if best_submission:
                    scores[username][i] = best_submission.score
                
        # 5. sort users by score
        scores = {k: v for k, v in sorted(scores.items(), key=lambda item: sum(item[1]), reverse=True)}
        
        scoreboard : ContestScoreboardDTO = ContestScoreboardDTO(
            userteams = scores.keys(),
            problems = titles,
            scores = scores.values()
        )

        return ContestScoreboardDTO.model_validate(obj=scoreboard)
    
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

def get_scoreboardV2(id: int, session: Session) -> ContestScoreboardDTO:
    """
    Get the current scoreboard for a specific contest

    Args:
        id (int): the contest id
        session (Session): sqlalchemy session
    """
    try:
        query = select(ContestScoreboard).filter(ContestScoreboard.contest_id == id)
        result = session.execute(query).scalars().all()
        return result
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion

def list_problems(id: int, user: User, session: Session) -> ListResponse:
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

#region Contest Team

# def add_teams(id: int, team_ids: List[int], session: Session) -> bool:
#     """
#     Add team to contest

#     Args:
#         id: int
#         team_id: int
    
#     Returns:
#         bool: added
#     """

#     try:
#         contest: Contest = get_object_by_id(Contest, session, id)
#         if not contest:
#             raise HTTPException(status_code=404, detail="Contest not found")
        
#         for team_id in team_ids:
#             team: Team = get_object_by_id(Team, session, team_id)

#             if not team:
#                 raise HTTPException(status_code=404, detail="Team not found")

#             if team in contest.teams:
#                 raise HTTPException(status_code=400, detail="Team already in contest")

#             contest.teams.append(team)
#         session.commit()
#         return True
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
# def remove_teams(id: int, team_ids: List[int], session: Session) -> bool:
#     """
#     Remove team from contest

#     Args:
#         id: int
#         team_id: int

#     Returns:
#         bool: removed
#     """

#     try:
#         contest: Contest = get_object_by_id(Contest, session, id)
#         if not contest:
#             raise HTTPException(status_code=404, detail="Contest not found")
        
#         for team_id in team_ids:
#             team: Team = get_object_by_id(Team, session, team_id)

#             if not team:
#                 raise HTTPException(status_code=404, detail="Team not found")

#             if team not in contest.teams:
#                 raise HTTPException(status_code=404, detail="Team not found in contest")

#             contest.teams.remove(team)
#         session.commit()
#         return True
    
#     except SQLAlchemyError as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         session.rollback()
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))
    
# def list_teams(id: int, session: Session) -> ListResponse:
#     """
#     List teams in a contest

#     Args:
#         id: int

#     Returns:
#         ListResponse: teams
#     """

#     try:
#         contest: Contest = get_object_by_id(Contest, session, id)
#         if not contest:
#             raise HTTPException(status_code=404, detail="Contest not found")
        
#         return {"data": [ContestTeamDTO.model_validate(obj=team) for team in contest.teams], "count": len(contest.teams)}
    
#     except SQLAlchemyError as e:
#         raise HTTPException(status_code=500, detail="Database error: " + str(e))
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="An unexpected error occurred: " + str(e))

#endregion
