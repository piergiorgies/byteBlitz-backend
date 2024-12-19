from enum import IntFlag

class Role(IntFlag):
    GUEST = 0               # 00000000
    USER = 1                # 00000001
    PROBLEM_MAINTAINER = 2  # 00000010
    CONTEST_MAINTAINER = 4  # 00000100
    USER_MAINTAINER = 8     # 00001000
    ADMIN = 127             # 01111111
    JUDGE = 128             # 10000000