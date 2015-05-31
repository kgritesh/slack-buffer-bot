This is a slack bot which automatically pushes any message that is posted on a specified channel to the buffer twitter queue

### Setup and Usage

1. Create a new slack bot account via  https://voxapp.slack.com/services/new/bot and get an API token
2. Create a new channel which will be used to post tweets to buffer. Invite the bot to this channel.
3. Create a new buffer app at https://buffer.com/developers/apps/create and keep track of buffer client id, client secret and access token.
4. The bot requires slack and buffer auth tokens to be provided as environment variables. You need to export following variables to run this bot locally
    
        export BUFFER_CLIENT_ID="your buffer client id"
        export BUFFER_CLIENT_SECRET="your buffer client secret"
        export BUFFER_ACCESS_TOKEN="your buffer access token"
        export BUFFER_SLACK_CHANNEL="slack channel to be used to post to buffer"
        export SLACK_TOKEN="Slack Auth Token"
        
5. Run the bot as 

        python bufferbot.py 
    
  and you are set. Now you can post any message to the buffer channel and it will be automatically put to your buffer account's twitter queue.
    
