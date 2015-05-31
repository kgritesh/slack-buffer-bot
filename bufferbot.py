import os
from buffpy import API
from buffpy.managers.profiles import Profiles
from twitter_text import TwitterText
from rtmbot import RTMBot


class TwitterValidationError(Exception):
    pass


def validate_tweet(message):
    twitter_text = TwitterText(message)
    ret = twitter_text.validation.tweet_invalid()
    if not ret:
        return True
    else:
        if ret == 'Too long':
            ret = 'Too Long (%d) characters' % len(message)

        raise TwitterValidationError(ret)


class BufferBot(RTMBot):
    def __init__(self, buffer_client_id, buffer_client_secret,
                 buffer_access_token, buffer_slack_channel,
                 slack_token):

        super(BufferBot, self).__init__(slack_token)
        self.buffer_channel_name = buffer_slack_channel
        self.buffer_client = API(client_id=buffer_client_id,
                                 client_secret=buffer_client_secret,
                                 access_token=buffer_access_token)

        self.twitter_profile = Profiles(api=self.buffer_client)\
            .filter(service='twitter')[0]
        self.buffer_channel = None

    def connect(self):
        super(BufferBot, self).connect()
        self.buffer_channel = \
            self.slack_client.get_channel_by_name(self.buffer_channel_name)

    def process_message(self, data):
        subtype = data.get('subtype')
        user_id = data.get('user')
        user = user_id and self.slack_client.users[user_id]

        if data['channel'] == self.buffer_channel.id and subtype not in \
            ['message_changed', 'bot_message', 'message_deleted'] and \
                (user is None or user.name != 'slackbot'):

            message = data['text']
            self.send_tweet(message)

    def send_tweet(self, message):
        try:
            validate_tweet(message)
            self.twitter_profile.updates.new(message)
            print "Status Update Pushed: %s" % message
        except TwitterValidationError, ex:
            print "Invalid Tweet: %s" % ex.message
            self.buffer_channel.send_message("Invalid Tweet: %s" % ex.message)

if __name__ == '__main__':
    buffer_bot = BufferBot(os.environ['BUFFER_CLIENT_ID'],
                           os.environ['BUFFER_CLIENT_SECRET'],
                           os.environ['BUFFER_ACCESS_TOKEN'],
                           os.environ['BUFFER_SLACK_CHANNEL'],
                           os.environ['SLACK_TOKEN'])

    buffer_bot.start()