from enum import IntFlag

class Role(IntFlag):
    ADMIN = 1
    USER = 1 << 1
    GUEST = 1 << 2