from datetime import datetime, timedelta
from lorem_text import lorem
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models import Contest, Language, SubmissionResult, Team, UserType, ContestTeam, User, ContestUser, Problem
from app.models import TeamUser, ContestProblem, ProblemConstraint, ProblemTestCase, Submission, ContestSubmission, SubmissionTestCase
from app.controllers.auth import _hash_password
from app.config import settings

# Database connection
engine = create_engine(settings.get_connection_string)
session : Session = Session(autocommit=False, autoflush=False, bind=engine)
metadata : MetaData = MetaData()
metadata.reflect(bind=engine)

EXCLUDED_TABLES = ["alembic_version"]

print("Creating test dataset...\n")

try:
    with session.begin():
        
        # Clear all tables
        for table in reversed(metadata.sorted_tables):
            if (table.name not in EXCLUDED_TABLES):
                print(table) #TODO: delete
                #session.execute(table.delete())
        print("\nAll tables have been cleared\n")

        # Create data and bonds between tables
        # contests
        contest1 = Contest(
            id = 1,
            name = "Brixia Coding Challenge",
            description = "A contest for tests",
            start_datetime = datetime.now() - timedelta(days=10),
            end_datetime = datetime.now() - timedelta(days=5),
        )
        contest2 = Contest(
            id = 2,
            name = "IEEEXtreme ver.18",
            description = "Another contest for tests",
            start_datetime = datetime.now() - timedelta(days=5),
            end_datetime = datetime.now() + timedelta(days=5),
        )
        contest3 = Contest(
            id = 3,
            name = "Reply Code Challenge",
            description = "The n-th contest for tests",
            start_datetime = datetime.now() + timedelta(days=5),
            end_datetime = datetime.now() + timedelta(days=10),
        )

        # languages
        java = Language(
            id = 1,
            name = "Java",
            file_extension = ".java"
        )
        python = Language(
            id = 2,
            name = "Python",
            file_extension = ".py"
        )
        cpp = Language(
            id = 3,
            name = "C++",
            file_extension = ".cpp"
        )
        javascript = Language(
            id = 4,
            name = "JavaScript",
            file_extension = ".js"
        )

        # submission_results
        result1 = SubmissionResult(
            id = 1,
            code = 1,
            description = "Accepted"
        )
        result2 = SubmissionResult(
            id = 2,
            code = 2,
            description = "Time limit exceded"
        )
        result3 = SubmissionResult(
            id = 3,
            code = 3,
            description = "Memory limit exceded"
        )
        result4 = SubmissionResult(
            id = 4,
            code = 4,
            description = "Wrong answer"
        )
        result5 = SubmissionResult(
            id = 5,
            code = 5,
            description = "Compilation error"
        )

        # teams
        # FIXME: NOT IMPLEMENTED YET

        # user_types FIXME: incomplete (more types + wrong permissions)
        admin_type = UserType(
            id = 1,
            code = "admin",
            description = "System administrator",
            permissions = 1
        )
        user_type = UserType(
            id = 2,
            code = "user",
            description = "An authenticated user, a contest participant",
            permissions = 0
        )

        # contest_teams
        # FIXME: NOT IMPLEMENTED YET

        # users FIXME: incomplete (more users for different types)
        admin_password, admin_salt = _hash_password(password="admin123")
        admin = User(
            id = 1,
            username = "admin",
            email = "admin@admin.com",
            password_hash = admin_password,
            salt = admin_salt,
            user_type_id = 1
        )
        user_password, user_salt = _hash_password(password="user123")
        user = User(
            id = 2,
            username = "user",
            email = "user@user.com",
            password_hash = user_password,
            salt = user_salt,
            user_type_id = 2
        )
        p1_password, p1_salt = _hash_password(password="p1_123")
        participant1 = User(
            id = 3,
            username = "participant1",
            email = "participant1@participant.com",
            password_hash = p1_password,
            salt = p1_salt,
            user_type_id = 2
        )
        p2_password, p2_salt = _hash_password(password="p2_123")
        participant2 = User(
            id = 4,
            username = "participant2",
            email = "participant2@participant.com",
            password_hash = p2_password,
            salt = p2_salt,
            user_type_id = 2
        )
        p3_password, p3_salt = _hash_password(password="p3_123")
        participant3 = User(
            id = 5,
            username = "participant3",
            email = "participant3@participant.com",
            password_hash = p3_password,
            salt = p3_salt,
            user_type_id = 2
        )

        # contest_users
        c1_u1 = ContestUser(
            contest_id = 1,
            user_id = 1,
            score = 200
        )
        c1_u2 = ContestUser(
            contest_id = 1,
            user_id = 2,
            score = 130
        )
        c1_u3 = ContestUser(
            contest_id = 1,
            user_id = 3,
            score = 345
        )
        c2_u1 = ContestUser(
            contest_id = 2,
            user_id = 1,
            score = 90
        )
        c2_u3 = ContestUser(
            contest_id = 2,
            user_id = 3,
            score = 69
        )
        c3_u2 = ContestUser(
            contest_id = 3,
            user_id = 2,
            score = 0
        )

        # problems
        problem1 = Problem(
            id = 1,
            title = "Bonio the Painter",
            description = "Help Bonio paint the most amount of houses. " + lorem.paragraph(),
            points = 0,
            is_public = True,
            author_id = 1
        )
        problem2 = Problem(
            id = 2,
            title = "Mystical Muffins",
            description = "Try to eat more muffins than Nizzo. " + lorem.paragraph(),
            points = 100,
            is_public = True,
            author_id = 1
        )
        problem3 = Problem(
            id = 3,
            title = "Princess Kibo",
            description = "Save the princess, save Kibo! " + lorem.paragraph(),
            points = 0,
            is_public = False,
            author_id = 1
        )
        problem4 = Problem(
            id = 4,
            title = "Armchair Reseller",
            description = "Apo is in the need for a successor. Find the best one in the branch. " + lorem.paragraph(),
            points = 100,
            is_public = True,
            author_id = 1
        )
        problem5 = Problem(
            id = 5,
            title = "Missed Straight",
            description = "As we are not great poker players, identify the best combination for this hand. " + lorem.paragraph(),
            points = 100,
            is_public = False,
            author_id = 1
        )
        problem6 = Problem(
            id = 6,
            title = "Casapound Propaganda",
            description = "Find the most brainwashed article between casapound blog posts. " + lorem.paragraph(),
            points = 200,
            is_public = False,
            author_id = 1
        )
        problem7 = Problem(
            id = 7,
            title = "Cansat Into Space",
            description = "Eliminate k consecutive tunisian from the competition. " + lorem.paragraph(),
            points = 80,
            is_public = True,
            author_id = 1
        )
        problem8 = Problem(
            id = 8,
            title = "Balcan Fight",
            description = "Nuk ka me gjuhe ballkanike!! " + lorem.paragraph(),
            points = 100,
            is_public = True,
            author_id = 1
        )
        problem9 = Problem(
            id = 9,
            title = "Color Blindness got Me Crazy",
            description = "Help Berna pass this ImPoSsIbLe Captcha. " + lorem.paragraph(),
            points = 300,
            is_public = False,
            author_id = 1
        )

        # team_users
        # FIXME: NOT IMPLEMENTED YET

        # contest_problems
        c1_p1 = ContestProblem(
            contest_id = 1,
            problem_id = 1,
            publication_delay = 0
        )
        c1_p2 = ContestProblem(
            contest_id = 1,
            problem_id = 2,
            publication_delay = 30
        )
        c1_p4 = ContestProblem(
            contest_id = 1,
            problem_id = 4,
            publication_delay = 60
        )
        c1_p5 = ContestProblem(
            contest_id = 1,
            problem_id = 5,
            publication_delay = 120
        )
        c2_p3 = ContestProblem(
            contest_id = 2,
            problem_id = 3,
            publication_delay = 0
        )
        c2_p6 = ContestProblem(
            contest_id = 2,
            problem_id = 6,
            publication_delay = 45
        )
        c2_p7 = ContestProblem(
            contest_id = 2,
            problem_id = 7,
            publication_delay = 90
        )
        c3_p8 = ContestProblem(
            contest_id = 3,
            problem_id = 8,
            publication_delay = 0
        )
        c3_p9 = ContestProblem(
            contest_id = 3,
            problem_id = 9,
            publication_delay = 180
        )

        # problem_constraints
        p1_l1 = ProblemConstraint(
            problem_id = 1,
            language_id = 1,
            memory_limit = 512,
            time_limit = 1000
        )
        p1_l2 = ProblemConstraint(
            problem_id = 1,
            language_id = 2,
            memory_limit = 256,
            time_limit = 2000
        )
        p1_l3 = ProblemConstraint(
            problem_id = 1,
            language_id = 3,
            memory_limit = 128,
            time_limit = 12500
        )
        p1_l4 = ProblemConstraint(
            problem_id = 1,
            language_id = 4,
            memory_limit = 1024,
            time_limit = 500
        )
        p2_l1 = ProblemConstraint(
            problem_id = 2,
            language_id = 1,
            memory_limit = 512,
            time_limit = 1500
        )
        p2_l2 = ProblemConstraint(
            problem_id = 2,
            language_id = 2,
            memory_limit = 256,
            time_limit = 2500
        )
        p4_l3 = ProblemConstraint(
            problem_id = 4,
            language_id = 3,
            memory_limit = 512,
            time_limit = 3000
        )
        p4_l4 = ProblemConstraint(
            problem_id = 4,
            language_id = 4,
            memory_limit = 128,
            time_limit = 5000
        )

        # problem_test_cases FIXME: input_name and output_name must be exchanged with input and output
        # TODO: here
        test_case1 = ProblemTestCase(
            id = -1,
            number = -1,
            notes = "TODO",
            # input = "todo",
            # output = "todo",
            points = 0,
            is_pretest = True,
            problem_id = 1
        )

        # submissions
        # TODO: here

        # contest_submissions
        # TODO: here

        # submission_test_cases
        # TODO: here

        print("\nAll instances have been created")
        print("All instantances have been connected with each other\n")

        # Commit
        session.commit()
        print("\nTest dataset correctly initialized\n")

except SQLAlchemyError as e:
    session.rollback()
    print("Database error: " + str(e))
    raise e
except Exception as e:
    session.rollback()
    print("An unexpected error occurred: " + str(e))
    raise e