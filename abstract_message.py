class AbstractMessage:
    def construct_message(self, message_type, message):
        return f"{message_type}:{message}"

    def request(self, message):
        return self.construct_message('request', str(message))

    def error(self, message):
        return self.construct_message('error', str(message))

    def data(self, message):
        return self.construct_message('data', str(message))

    def response(self, message):
        return self.construct_message('response', str(message))

    def event(self, message):
        return self.construct_message('event', str(message))

    def log(self, message):
        return self.construct_message('log', str(message))

    def set(self, message):
        return self.construct_message('set', str(message))
    
    def pid(self, message):
        return self.construct_message('pid', str(message))