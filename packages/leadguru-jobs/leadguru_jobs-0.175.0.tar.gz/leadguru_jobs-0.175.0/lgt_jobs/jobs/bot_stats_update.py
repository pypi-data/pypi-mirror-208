from abc import ABC
from typing import Optional
from lgt.common.python.slack_client.web_client import SlackWebClient
from lgt_data.mongo_repository import BotMongoRepository, DedicatedBotRepository
from pydantic import BaseModel
from lgt_data.analytics import get_bots_aggregated_analytics
from lgt.common.python.lgt_logging import log
from ..basejobs import BaseBackgroundJob, BaseBackgroundJobData

"""
Update bots statistics
"""


class BotStatsUpdateJobData(BaseBackgroundJobData, BaseModel):
    dedicated_bot_id: Optional[str]
    bot_name: Optional[str]


class BotStatsUpdateJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return BotStatsUpdateJobData

    def exec(self, data: BotStatsUpdateJobData):
        received_messages, filtered_messages = get_bots_aggregated_analytics(
            bot_names=[data.bot_name] if data.bot_name else None,
            dedicated_bot_ids=[data.dedicated_bot_id] if data.dedicated_bot_id else None)

        if data.dedicated_bot_id:
            bots_rep = DedicatedBotRepository()
            bot = bots_rep.get_by_id(data.dedicated_bot_id)
        else:
            bots_rep = BotMongoRepository()
            bot = bots_rep.get_by_id(data.bot_name)

        if not bot:
            return

        client = SlackWebClient(bot.token, bot.cookies)
        if not bot.token or not bot.cookies or bot.invalid_creds:
            log.warning(f"Bot {data.dedicated_bot_id if data.dedicated_bot_id else data.bot_name} "
                        f"has no credentials or has invalid creds.")
            bot.invalid_creds = True
            bots_rep.add_or_update(bot)
            return
        channels_response = client.channels_list()
        if not channels_response['ok']:
            bot.invalid_creds = True
            bots_rep.add_or_update(bot)
            return
        channels = channels_response['channels']
        connected_channels = 0
        channels_users = {}
        active_channels = {}
        users_count = 0
        for channel in channels:
            if channel['is_member']:
                active_channels[channel['id']] = channel['name']
                connected_channels += 1
            num_members = channel.get('num_members', 0)
            channels_users[channel['id']] = num_members
            users_count += num_members

        bot.active_channels = active_channels
        bot.messages_received = received_messages.get(bot.name, 0)
        bot.messages_filtered = filtered_messages.get(bot.name, 0)
        bot.connected_channels = connected_channels
        bot.channels = len(channels)
        bot.channels_users = channels_users
        bot.users_count = users_count
        if bot.recent_messages is None:
            bot.recent_messages = []

        # save only last 50 messages
        bot.recent_messages = bot.recent_messages[-50:]
        bots_rep.add_or_update(bot)
