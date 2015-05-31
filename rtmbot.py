from slack import SlackWrapper


class RTMBot(object):
    def __init__(self, token):
        self.slack_client = SlackWrapper(token)

    def connect(self):
        self.slack_client.rtm_connect()

    def start(self):
        self.connect()
        while True:
            for event in self.slack_client.rtm_read():
                self.process(event)
                self.catch_all(event)

    def process(self, data):
        if "type" in data:
            function_name = "process_" + data["type"]
            process_func = getattr(self, function_name, None)
            if process_func and callable(process_func):
                process_func(data)

    def catch_all(self, data):
        pass

