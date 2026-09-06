from enum import StrEnum


class UserRole(StrEnum):
    TEAM_MEMBER = "TEAM_MEMBER"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


class UserStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INVITED = "INVITED"
    INACTIVE = "INACTIVE"


class ProjectStatus(StrEnum):
    ACTIVE = "ACTIVE"
    PLANNING = "PLANNING"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"