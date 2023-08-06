name = "lgt_jobs"

from .jobs.user_balance_update import UpdateUserBalanceJob, UpdateUserBalanceJobData
from .jobs.conversation_replied import ConversationRepliedJob, ConversationRepliedJobData
from .jobs.reactions_added import ReactionAddedJobData, ReactionAddedJob
from .jobs.send_slack_message import SendSlackMessageJob, SendSlackMessageJobData
from .jobs.user_limits_update import UpdateUserDataUsageJob, UpdateUserDataUsageJobData
from .jobs.analytics import (TrackAnalyticsJob, TrackAnalyticsJobData)
from .jobs.archive_leads import (ArchiveLeadsJob, ArchiveLeadsJobData)
from .jobs.bot_stats_update import (BotStatsUpdateJob, BotStatsUpdateJobData)
from .jobs.chat_history import (LoadChatHistoryJob, LoadChatHistoryJobData)
from .jobs.update_slack_profile import (UpdateUserSlackProfileJob, UpdateUserSlackProfileJobData)
from .jobs.reindex_conversation_history import ReIndexUserLeadsConversationHistoryJob, ReIndexUserLeadsConversationHistoryJobData
from .jobs.clear_user_analytics import ClearUserAnalyticsJobData, ClearUserAnalyticsJob
from .jobs.connected_workspaces import ConnectSlackAccount, ConnectSlackAccountJobData

from .basejobs import (BaseBackgroundJobData, BaseBackgroundJob, InvalidJobTypeException)
from .smtp import (SendMailJob, SendMailJobData)
from .runner import (BackgroundJobRunner)
from .simple_job import (SimpleTestJob, SimpleTestJobData)

jobs_map = {
    "SimpleTestJob": SimpleTestJob,
    "BotStatsUpdateJob": BotStatsUpdateJob,
    "ArchiveLeadsJob": ArchiveLeadsJob,
    "ConnectSlackAccount": ConnectSlackAccount,
    "SendMailJob": SendMailJob,
    "TrackAnalyticsJob": TrackAnalyticsJob,
    "LoadChatHistoryJob": LoadChatHistoryJob,
    "UpdateUserSlackProfileJob": UpdateUserSlackProfileJob,
    "UpdateUserDataUsageJob": UpdateUserDataUsageJob,
    "ConversationRepliedJob": ConversationRepliedJob,
    "ReactionAddedJob": ReactionAddedJob,
    "SendSlackMessageJob": SendSlackMessageJob,
    "UpdateUserBalanceJob": UpdateUserBalanceJob,
    "ReIndexUserLeadsConversationHistoryJob": ReIndexUserLeadsConversationHistoryJob,
    "ClearUserAnalyticsJob": ClearUserAnalyticsJob
}
__all__ = [
    # Jobs
    SimpleTestJob,
    BotStatsUpdateJob,
    ArchiveLeadsJob,
    ConnectSlackAccount,
    SendMailJob,
    SimpleTestJob,
    LoadChatHistoryJob,
    UpdateUserSlackProfileJob,
    TrackAnalyticsJob,
    UpdateUserDataUsageJob,
    ConversationRepliedJob,
    ReactionAddedJob,
    SendSlackMessageJob,
    UpdateUserBalanceJob,
    ReIndexUserLeadsConversationHistoryJob,
    ClearUserAnalyticsJob,

    # module classes
    BackgroundJobRunner,
    BaseBackgroundJobData,
    BaseBackgroundJob,
    InvalidJobTypeException,
    BotStatsUpdateJobData,
    ArchiveLeadsJobData,
    ConnectSlackAccountJobData,
    SendMailJobData,
    SimpleTestJobData,
    LoadChatHistoryJobData,
    UpdateUserSlackProfileJobData,
    TrackAnalyticsJobData,
    UpdateUserDataUsageJobData,
    ConversationRepliedJobData,
    ReactionAddedJobData,
    SendSlackMessageJobData,
    UpdateUserBalanceJobData,
    ReIndexUserLeadsConversationHistoryJobData,
    ClearUserAnalyticsJobData,

    # mapping
    jobs_map
]
