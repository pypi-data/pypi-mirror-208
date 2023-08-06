from abc import ABC
from typing import Optional

from lgt.common.python.lgt_logging import log
from lgt.common.python.slack_client.slack_client import SlackClient
from lgt.common.python.slack_client.web_client import get_system_slack_credentials, SlackWebClient
from pydantic import BaseModel
from lgt_data.mongo_repository import LeadMongoRepository, BotMongoRepository, \
    UserLeadMongoRepository, GarbageLeadsMongoRepository, SpamLeadsMongoRepository
from lgt_data.model import SlackReplyModel
from ..basejobs import BaseBackgroundJobData, BaseBackgroundJob

"""
Update messages conversations
"""


class ConversationRepliedJobData(BaseBackgroundJobData, BaseModel):
    channel_id: Optional[str]
    ts: str


class ConversationRepliedJob(BaseBackgroundJob, ABC):
    @property
    def job_data_type(self) -> type:
        return ConversationRepliedJobData

    def exec(self, data: ConversationRepliedJobData):
        bots = BotMongoRepository().get()
        lead = LeadMongoRepository().get(timestamp=data.ts, channel_id=data.channel_id)
        if not lead:
            return

        creds = get_system_slack_credentials(lead, bots)
        if not creds:
            log.warning(f"Lead: {lead.id}, bot credentials are not valid")
            return

        client = SlackClient(creds.token, creds.cookies)
        resp = client.conversations_replies(lead.message.channel_id, data.ts)
        if not resp["ok"]:
            return

        if not resp.get("messages"):
            return

        replies = []
        bot_name = lead.message.name
        bot = BotMongoRepository().get_by_id(bot_name)
        web_client = SlackWebClient(bot.token, bot.cookies)
        for slack_reply in resp["messages"][1:]:
            reply = SlackReplyModel.from_slack_response(slack_reply)
            user_response = web_client.get_profile(reply.user)
            if user_response["ok"]:
                reply.username = user_response.get("user").get("real_name")
            if not reply.attachments and lead.message.urls_in_message:
                for attachment in lead.message.urls_in_message:
                    reply.attachments.append(client.get_attachments(
                        lead.message.channel_id, lead.message.message_id, attachment))
            replies.append(reply.to_dic())

        set_dict = {
            "replies": replies,
        }
        pipeline = {"message.timestamp": data.ts}
        if data.channel_id:
            pipeline['message.channel_id'] = data.channel_id
        LeadMongoRepository().collection().update_many(pipeline, {"$set": set_dict})
        UserLeadMongoRepository().collection().update_many(pipeline, {"$set": set_dict})
        GarbageLeadsMongoRepository().collection().update_many(pipeline, {"$set": set_dict})
        SpamLeadsMongoRepository().collection().update_many(pipeline, {"$set": set_dict})