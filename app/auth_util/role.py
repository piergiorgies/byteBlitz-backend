from enum import IntFlag

class Role(IntFlag):
    GUEST = 0
    USER = 1
    PROBLEM_MAINTAINER = 2
    CONTEST_MAINTAINER = 4
    USER_MAINTAINER = 8
    ADMIN = 127
    JUDGE = 128