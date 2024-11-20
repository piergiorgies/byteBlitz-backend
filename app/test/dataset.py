from datetime import datetime, timedelta
from typing import List
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
        contests : List[Contest] = [
            Contest(
                id = 1,
                name = "Brixia Coding Challenge",
                description = "A contest for tests",
                start_datetime = datetime.now() - timedelta(days=10),
                end_datetime = datetime.now() - timedelta(days=5),
            ),
            Contest(
                id = 2,
                name = "IEEEXtreme ver.18",
                description = "Another contest for tests",
                start_datetime = datetime.now() - timedelta(days=5),
                end_datetime = datetime.now() + timedelta(days=5),
            ),
            Contest(
                id = 3,
                name = "Reply Code Challenge",
                description = "The n-th contest for tests",
                start_datetime = datetime.now() + timedelta(days=5),
                end_datetime = datetime.now() + timedelta(days=10),
            )
        ]
        session.add_all(contests)

        # languages
        languages : List[Language] = [
            Language(
                id = 1,
                name = "Java",
                file_extension = ".java"
            ),
            Language(
                id = 2,
                name = "Python",
                file_extension = ".py"
            ),
            Language(
                id = 3,
                name = "C++",
                file_extension = ".cpp"
            ),
            Language(
                id = 4,
                name = "JavaScript",
                file_extension = ".js"
            )
        ]
        session.add_all(languages)

        # submission_results
        submission_results : List[SubmissionResult] = [
            SubmissionResult(
                id = 1,
                code = 1,
                description = "Accepted"
            ),
            SubmissionResult(
                id = 2,
                code = 2,
                description = "Time limit exceded"
            ),
            SubmissionResult(
                id = 3,
                code = 3,
                description = "Memory limit exceded"
            ),
            SubmissionResult(
                id = 4,
                code = 4,
                description = "Wrong answer"
            ),
            SubmissionResult(
                id = 5,
                code = 5,
                description = "Compilation error"
            )
        ]
        session.add_all(submission_results)

        # teams
        # FIXME: NOT IMPLEMENTED YET

        # user_types FIXME: incomplete (more types + wrong permissions)
        user_types : List[UserType] = [
            UserType(
                id = 1,
                code = "admin",
                description = "System administrator",
                permissions = 1
            ),
            UserType(
                id = 2,
                code = "user",
                description = "An authenticated user, a contest participant",
                permissions = 0
            )
        ]
        session.add_all(user_types)

        # contest_teams
        # FIXME: NOT IMPLEMENTED YET

        # users FIXME: incomplete (more users for different types)
        users : List[User] = []
        admin_password, admin_salt = _hash_password(password="admin123")
        users.append(
            User(
                id = 1,
                username = "admin",
                email = "admin@admin.com",
                password_hash = admin_password,
                salt = admin_salt,
                user_type_id = 1
            )
        )
        user_password, user_salt = _hash_password(password="user123")
        users.append(
            User(
                id = 2,
                username = "user",
                email = "user@user.com",
                password_hash = user_password,
                salt = user_salt,
                user_type_id = 2
            )
        )
        p1_password, p1_salt = _hash_password(password="p1_123")
        users.append(
            User(
                id = 3,
                username = "participant1",
                email = "participant1@participant.com",
                password_hash = p1_password,
                salt = p1_salt,
                user_type_id = 2
            )
        )
        p2_password, p2_salt = _hash_password(password="p2_123")
        users.append(
            User(
                id = 4,
                username = "participant2",
                email = "participant2@participant.com",
                password_hash = p2_password,
                salt = p2_salt,
                user_type_id = 2
            )
        )
        p3_password, p3_salt = _hash_password(password="p3_123")
        users.append(
            User(
                id = 5,
                username = "participant3",
                email = "participant3@participant.com",
                password_hash = p3_password,
                salt = p3_salt,
                user_type_id = 2
            )
        )
        session.add_all(users)

        # contest_users
        contest_users : List[ContestUser] = [
            ContestUser(
                contest_id = 1,
                user_id = 3,
                score = 200
            ),
            ContestUser(
                contest_id = 1,
                user_id = 4,
                score = 130
            ),
            ContestUser(
                contest_id = 1,
                user_id = 5,
                score = 345
            ),
            ContestUser(
                contest_id = 2,
                user_id = 3,
                score = 90
            ),
            ContestUser(
                contest_id = 2,
                user_id = 5,
                score = 69
            ),
            ContestUser(
                contest_id = 3,
                user_id = 4,
                score = 0
            )
        ]
        session.add_all(contest_users)

        # problems
        problems : List[Problem] = [
            Problem(
                id = 1,
                title = "Bonio the Painter",
                description = "Help Bonio paint the most amount of houses. " + lorem.paragraph(),
                points = 0,
                is_public = True,
                author_id = 1
            ),
            Problem(
                id = 2,
                title = "Mystical Muffins",
                description = "Try to eat more muffins than Nizzo. " + lorem.paragraph(),
                points = 100,
                is_public = True,
                author_id = 1
            ),
            Problem(
                id = 3,
                title = "Princess Kibo",
                description = "Save the princess, save Kibo! " + lorem.paragraph(),
                points = 0,
                is_public = False,
                author_id = 1
            ),
            Problem(
                id = 4,
                title = "Armchair Reseller",
                description = "Apo is in the need for a successor. Find the best one in the branch. " + lorem.paragraph(),
                points = 100,
                is_public = True,
                author_id = 1
            ),
            Problem(
                id = 5,
                title = "Missed Straight",
                description = "As we are not great poker players, identify the best combination for this hand. " + lorem.paragraph(),
                points = 100,
                is_public = False,
                author_id = 1
            ),
            Problem(
                id = 6,
                title = "Casapound Propaganda",
                description = "Find the most brainwashed article between casapound blog posts. " + lorem.paragraph(),
                points = 200,
                is_public = False,
                author_id = 1
            ),
            Problem(
                id = 7,
                title = "Cansat Into Space",
                description = "Eliminate k consecutive tunisian from the competition. " + lorem.paragraph(),
                points = 80,
                is_public = True,
                author_id = 1
            ),
            Problem(
                id = 8,
                title = "Balcan Fight",
                description = "Nuk ka me gjuhe ballkanike!! " + lorem.paragraph(),
                points = 100,
                is_public = True,
                author_id = 1
            ),
            Problem(
                id = 9,
                title = "Color Blindness got Me Crazy",
                description = "Help Berna pass this ImPoSsIbLe Captcha. " + lorem.paragraph(),
                points = 300,
                is_public = False,
                author_id = 1
            )
        ]
        session.add_all(problems)

        # team_users
        # FIXME: NOT IMPLEMENTED YET

        # contest_problems
        contest_problems : List[ContestProblem] = [
            ContestProblem(
                contest_id = 1,
                problem_id = 1,
                publication_delay = 0
            ),
            ContestProblem(
                contest_id = 1,
                problem_id = 2,
                publication_delay = 30
            ),
            ContestProblem(
                contest_id = 1,
                problem_id = 4,
                publication_delay = 60
            ),
            ContestProblem(
                contest_id = 1,
                problem_id = 5,
                publication_delay = 120
            ),
            ContestProblem(
                contest_id = 2,
                problem_id = 3,
                publication_delay = 0
            ),
            ContestProblem(
                contest_id = 2,
                problem_id = 6,
                publication_delay = 45
            ),
            ContestProblem(
                contest_id = 2,
                problem_id = 7,
                publication_delay = 90
            ),
            ContestProblem(
                contest_id = 3,
                problem_id = 8,
                publication_delay = 0
            ),
            ContestProblem(
                contest_id = 3,
                problem_id = 9,
                publication_delay = 180
            )
        ]
        session.add_all(contest_problems)

        # problem_constraints
        problem_constraints : List[ProblemConstraint] = [
            ProblemConstraint(
                problem_id = 1,
                language_id = 1,
                memory_limit = 512,
                time_limit = 1000
            ),
            ProblemConstraint(
                problem_id = 1,
                language_id = 2,
                memory_limit = 256,
                time_limit = 2000
            ),
            ProblemConstraint(
                problem_id = 1,
                language_id = 3,
                memory_limit = 128,
                time_limit = 12500
            ),
            ProblemConstraint(
                problem_id = 1,
                language_id = 4,
                memory_limit = 1024,
                time_limit = 500
            ),
            ProblemConstraint(
                problem_id = 2,
                language_id = 1,
                memory_limit = 512,
                time_limit = 1500
            ),
            ProblemConstraint(
                problem_id = 2,
                language_id = 2,
                memory_limit = 256,
                time_limit = 2500
            ),
            ProblemConstraint(
                problem_id = 4,
                language_id = 3,
                memory_limit = 512,
                time_limit = 3000
            ),
            ProblemConstraint(
                problem_id = 4,
                language_id = 4,
                memory_limit = 128,
                time_limit = 5000
            )
        ]
        session.add_all(problem_constraints)

        # problem_test_cases
        problem_test_cases : List[ProblemTestCase] = [
            ProblemTestCase(
                id = 1,
                number = 1,
                notes = "Test notes",
                input = "a" * 10000,
                output = "24",
                points = 0,
                is_pretest = True,
                problem_id = 2
            ),
            ProblemTestCase(
                id = 2,
                number = 2,
                notes = "Test notes",
                input = "((()||((/))/))",
                output = "(()())",
                points = 20,
                is_pretest = False,
                problem_id = 2
            ),
            ProblemTestCase(
                id = 3,
                number = 3,
                notes = "Test notes",
                input = "bcc - Brixia Coding Challenge",
                output = "|^_^|",
                points = 10,
                is_pretest = False,
                problem_id = 2
            ),
            ProblemTestCase(
                id = 4,
                number = 1,
                notes = "Test notes",
                input = "1, 3, 5, 7, 9",
                output = "11",
                points = 0,
                is_pretest = True,
                problem_id = 4
            ),
            ProblemTestCase(
                id = 5,
                number = 2,
                notes = "Test notes",
                input = "phoenixInput",
                output = "phoenixOutput",
                points = 50,
                is_pretest = False,
                problem_id = 4
            )
        ]
        session.add_all(problem_test_cases)

        # submissions
        submissions : List[Submission] = [
            Submission(
                id = 1,
                notes = "Test notes",
                score = 0,
                submitted_code = """
                    import java.util.Arrays;

                    public class Knapsack {
                        public static int knapsack(int W, int[] weights, int[] values, int n) {
                            int[][] dp = new int[n + 1][W + 1];

                            for (int i = 0; i <= n; i++) {
                                for (int w = 0; w <= W; w++) {
                                    if (i == 0 || w == 0) {
                                        dp[i][w] = 0;
                                    } else if (weights[i - 1] <= w) {
                                        dp[i][w] = Math.max(values[i - 1] + dp[i - 1][w - weights[i - 1]], dp[i - 1][w]);
                                    } else {
                                        dp[i][w] = dp[i - 1][w];
                                    }
                                }
                            }
                            return dp[n][W];
                        }

                        public static void main(String[] args) {
                            int[] values = {60, 100, 120};
                            int[] weights = {10, 20, 30};
                            int W = 50;
                            int n = values.length;
                            System.out.println("Maximum value in Knapsack = " + knapsack(W, weights, values, n));
                        }
                    }
                """,
                problem_id = 2,
                user_id = 3,
                language_id = 1,
                submission_result_id = 2
            ),
            Submission(
                id = 2,
                notes = "Test notes",
                score = 69,
                submitted_code = """
                    def is_safe(board, row, col):
                        for i in range(col):
                            if board[row][i] == 1:
                                return False
                        for i, j in zip(range(row, -1, -1), range(col, -1, -1)):
                            if board[i][j] == 1:
                                return False
                        for i, j in zip(range(row, len(board)), range(col, -1, -1)):
                            if board[i][j] == 1:
                                return False
                        return True

                    def solve_n_queens_util(board, col):
                        if col >= len(board):
                            return True
                        for i in range(len(board)):
                            if is_safe(board, i, col):
                                board[i][col] = 1
                                if solve_n_queens_util(board, col + 1):
                                    return True
                                board[i][col] = 0
                        return False

                    def solve_n_queens(n):
                        board = [[0 for _ in range(n)] for _ in range(n)]
                        if not solve_n_queens_util(board, 0):
                            return "Solution does not exist"
                        return board

                    # Example usage
                    n = 4
                    solution = solve_n_queens(n)
                    for row in solution:
                        print(row)
                """,
                problem_id = 2,
                user_id = 3,
                language_id = 2,
                submission_result_id = 1
            ),
            Submission(
                id = 3,
                notes = "Test notes",
                score = 0,
                submitted_code = """
                    import numpy as np
                    from scipy.optimize import linprog

                    # Coefficients of the objective function
                    c = [-1, -2]  # Example coefficients for maximization

                    # Coefficients for the inequality constraints
                    A = [[1, 1], [2, 1], [1, 2]]
                    b = [10, 20, 15]

                    # Bounds for each variable
                    x0_bounds = (0, None)
                    x1_bounds = (0, None)

                    # Solve the linear programming problem
                    res = linprog(c, A_ub=A, b_ub=b, bounds=[x0_bounds, x1_bounds], method='highs')

                    # Output the results
                    print('Optimal value:', -res.fun)
                    print('Optimal solution:', res.x)
                """,
                problem_id = 4,
                user_id = 4,
                language_id = 2,
                submission_result_id = 5
            ),
            Submission(
                id = 4,
                notes = "Test notes",
                score = 100,
                submitted_code = """
                    # Sorting Algorithm

                    function bubbleSort(arr) {
                        let n = arr.length;
                        let swapped;
                        do {
                            swapped = false;
                            for (let i = 0; i < n - 1; i++) {
                                if (arr[i] > arr[i + 1]) {
                                    [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                                    swapped = true;
                                }
                            }
                            n--;
                        } while (swapped);
                        return arr;
                    }

                    // Example usage:
                    const array = [64, 34, 25, 12, 22, 11, 90];
                    console.log(bubbleSort(array));
                """,
                problem_id = 4,
                user_id = 5,
                language_id = 4,
                submission_result_id = 1
            )
        ]
        session.add_all(submissions)

        # contest_submissions
        contest_submissions : List[ContestSubmission] = [
            ContestSubmission(
                contest_id = 1,
                submission_id = 1
            ),
            ContestSubmission(
                contest_id = 3,
                submission_id = 2
            ),
            ContestSubmission(
                contest_id = 1,
                submission_id = 3
            ),
            ContestSubmission(
                contest_id = 3,
                submission_id = 4
            )
        ]
        session.add_all(contest_submissions)

        # submission_test_cases
        submission_test_cases : List[SubmissionTestCase] = [
            SubmissionTestCase(
                id = 1,
                number = 1,
                notes = "Test notes",
                memory = 235,
                time = 750,
                result_id = 3,
                submission_id = 4
            ),
            SubmissionTestCase(
                id = 2,
                number = 1,
                notes = "Test notes",
                memory = 410,
                time = 667,
                result_id = 5,
                submission_id = 3
            ),
            SubmissionTestCase(
                id = 3,
                number = 1,
                notes = "Test notes",
                memory = 150,
                time = 320,
                result_id = 4,
                submission_id = 2
            ),
            SubmissionTestCase(
                id = 4,
                number = 1,
                notes = "Test notes",
                memory = 98,
                time = 191,
                result_id = 1,
                submission_id = 1
            )
        ]
        session.add_all(submission_test_cases)

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