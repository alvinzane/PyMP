# coding=utf-8


class Plugin(object):

    def init(self, context):
        raise NotImplementedError()

    def read_handshake(self, context):
        raise NotImplementedError()

    def send_handshake(self, context):
        raise NotImplementedError()

    def read_auth(self, context):
        raise NotImplementedError()

    def send_auth(self, context):
        raise NotImplementedError()

    def read_auth_result(self, context):
        raise NotImplementedError()

    def send_auth_result(self, context):
        raise NotImplementedError()

    def read_query(self, context):
        raise NotImplementedError()

    def send_query(self, context):
        raise NotImplementedError()

    def read_query_result(self, context):
        raise NotImplementedError()

    def send_query_result(self, context):
        raise NotImplementedError()

    def cleanup(self, context):
        raise NotImplementedError()

    def shutdown(self, context):
        raise NotImplementedError()
