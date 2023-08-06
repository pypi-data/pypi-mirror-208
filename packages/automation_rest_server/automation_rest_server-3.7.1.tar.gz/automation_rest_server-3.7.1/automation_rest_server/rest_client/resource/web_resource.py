
from rest_client.resource.models.helper import rest_get_call


class WebResource(object):

    def __init__(self, session):
        self.session = session

    def get_status(self, ip, port):
        url_ = "http://{0}:{1}/api/web".format(ip, port)
        result = rest_get_call(url_, self.session, 10)
        return result
