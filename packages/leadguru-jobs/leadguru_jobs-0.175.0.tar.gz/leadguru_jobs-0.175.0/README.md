## Some example on how to publish messages for testing purposes


### 1. Load Slack Chat history
``gcloud pubsub topics publish local-background-worker  --message='{ "job_type": "LoadChatHistoryJob", "data": { "user_id": "5d9db09e3710ae3ec4b4592f" } }'``

### 2. Restart BOTS
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "RestartBotsJob", "data": { "bots": [] }}'``

### 3. Update BOTS credentials
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "BotsCredentialsUpdateJob", "data": { "bot_name": "mitrixdataprocessing" }}'``

### 4. Update User BOT credentials
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "UserBotsCredentialsUpdateJob", "data": { "user_id": "5d9db09e3710ae3ec4b4592f", "bot_name": "mitrixdataprocessing" }}'``

### 5. Update user slack profile
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "UpdateUserSlackProfileJob", "data": { "user_id": "5d9db09e3710ae3ec4b4592f", "bot_name": "mitrixdataprocessing" }}'``

### 6. Restart slack dedicated bots
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "RestartDedicatedBotsJob", "data": { "user_id": "5f354dd91554d906e44fadf6" }}'``

### 7. Update emotions
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "ReactionAddedJob", "data": { "message_id": "4f6258b5-75f5-49b4-b288-3e21921b1895", "ts": "1625480670.035200" }}'``

### 8. Update conversation history
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "ConversationRepliedJob", "data": { "message_id": "4f6258b5-75f5-49b4-b288-3e21921b1895", "ts": "1625480670.035200" }}'``

### 9. Bot status update
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "BotStatsUpdateJob", "data": { "bot_name": "mitrixdataprocessing" }}'``
``gcloud pubsub topics publish local-background-worker --message='{ "job_type": "BotStatsUpdateJob", "data": { "dedicated_bot_id": "60d9ab815b22e55e41da81da" }}'``

### 10. update stats
``gcloud pubsub topics publish local-background-worker --message='{"job_type": "UpdateUserDataUsageJob", "data": {"dedicated_bot_id": null, "filtered": false, "bot_name": "kotlinlang", "channel_id": "C0B8M7BUY", "message": "For changes from the server you would need a web socket."}}'``

### 11. update users feed
``
gcloud pubsub topics publish local-background-worker --message='{"job_type": "UpdateUserFeedJob", "data": {"lead_id": "61767a9 3bb463584e0658e1a", "bot_name": "gophers", "dedicated_bot_id": null}}'
``

### 12. update users balances
``
gcloud pubsub topics publish local-background-worker --message='{"job_type": "UpdateUserBalanceJob", "data": {"user_id": "60a6a9a59ef97dc902180512"}}'
``

### 13. Clear User analytics
``
gcloud pubsub topics publish local-background-worker --message='{"job_type": "ClearUserAnalyticsJob", "data": {"user_id": "60a6a9a59ef97dc902180512"}}'
``

