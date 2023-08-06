from enum import Enum, IntFlag


class DedicatedBotState(IntFlag):
    Operational = 0
    Stopped = 1
    ScheduledForDeletion = 2


class UserAccountState(IntFlag):
    Operational = 0
    Suspended = 1


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'


class BotType(str, Enum):
    DEDICATED_BOT = 'dedicated',
    USER_BOT = 'user',
    LEADGURU_BOT = 'leadguru'


class GoogleCloudFolder(str, Enum):
    SLACK_PROFILE_FILES = "Slack_profile"
    TICKET_FILES = "Ticket"


class SourceType(str, Enum):
    SLACK = 'slack'


class UserAction(str, Enum):
    PAUSE_CHANNEL = 'monitoring.pause.channel'
    PAUSE_WORKSPACE = 'monitoring.pause.workspace'
    UNPAUSE_CHANNEL = 'monitoring.unpause.channel'
    UNPAUSE_WORKSPACE = 'monitoring.unpause.workspace'
    STOP_CHANNEL = 'monitoring.stop.channel'
    STOP_WORKSPACE = 'monitoring.stop.workspace'
    START_CHANNEL = 'monitoring.start.channel'
    START_WORKSPACE = 'monitoring.start.workspace'


class StatusConnection:
    IN_PROGRESS = 'In progress',
    COMPLETE = 'Complete',
    FAILED = 'Failed'
