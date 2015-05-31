import re
from slackclient import SlackClient
import emoji


class SlackWrapper(object):
    RE_REMOVE_FORMATTING = re.compile(r'<([@#!])?([^>|]+)(?:\|([^>]+))?>')

    RE_MAIL_TO = re.compile(r'^mailto:')

    RE_EMOJI = re.compile(r'(:\w+:)')

    SMART_QUOTES_REPLACE = [
        (r"(^|[-\u2014\s(\[\"])'", ur"\1\u2018"), #opening singles
        (r"'", ur"\u2019"), #closing singles and apostrophes
        (r'(^|[-\u2014/\[(\u2018\s])"', ur"\1\u201c"), #opening doubles
        (r'"', ur"\u201d"), # closing double    s
        (r'--', ur"\u2014") # em-dashes
    ]

    def __init__(self, token):
        self.slack_client = SlackClient(token)
        self.channels = {}
        self.users = {}

    def rtm_connect(self):
        ret = self.slack_client.rtm_connect()

        for channel in self.slack_client.server.channels:
            self.channels[channel.id] = channel

        for user in self.slack_client.server.users:
            self.users[user.id] = user

        return ret

    def rtm_read(self):
        data = self.slack_client.rtm_read()
        for item in data:
            self.process_changes(item)
            if item.get('type') == 'message' and 'text' in item:
                item['text'] = self.remove_formatting(item['text'])

            yield item

    def process_changes(self, data):
        if "type" in data.keys():
            if data["type"] in ['channel_created', 'im_created']:
                channel = self.slack_client.server.channels[-1]
                self.channels[channel.id] = channel

    def replace_reference(self, matchobj):
        typ, link, label = matchobj.groups()
        if typ == '@':
            if label:
                return label
            else:
                user = self.users.get(link)
                if user:
                    return '@%s' % user.name

        elif typ == '#':
            if label:
                return label
            channel = self.channels.get(link)
            if channel:
                return '#%s' % channel.name

        elif typ == '!':
            if link in ['everyone', 'channel', 'group']:
                return '@%s' % link

        else:
            link = self.RE_MAIL_TO.sub('', link)
            if label and label not in link:
                return '%s (%s)' % (label, link)
            else:
                return link

    def remove_formatting(self, text):
        text = self.RE_REMOVE_FORMATTING.sub(self.replace_reference, text)
        text = self.add_smart_quotes(text)
        text = self.replace_emoji_unicode(text)
        return text

    @staticmethod
    def add_smart_quotes(text):
        for key, val in SlackWrapper.SMART_QUOTES_REPLACE:
            text = re.sub(key, val, text)

        return text

    @staticmethod
    def replace_emoji_unicode(text):
        return emoji.emojize(text, use_aliases=True)

    def get_channel_by_name(self, channel_name):
        for channel in self.channels.values():
            if channel.name == channel_name:
                return channel

        return None