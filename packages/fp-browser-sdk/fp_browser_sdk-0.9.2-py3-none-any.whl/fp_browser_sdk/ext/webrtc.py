from .module import Module
from .exception import IpErrorException


class Webrtc(Module):
    def __init__(self):
        super(Webrtc, self).__init__()
        self._privite_ip = None
        self._public_v4_ip = None
        self._public_v6_ip = None
        self._host_name = None
        pass

    def _to_dict(self):
        """
        解析成 dict
        """
        result = {
            "webrtc.privite-ip": self._privite_ip,
            "webrtc.public-v4-ip": self._public_v4_ip,
            "webrtc.public-v6-ip": self._public_v6_ip,
            "webrtc.host-name": self._host_name,
        }

        if "webrtc.private-ip" in result:
            if not self._verify_ip(result['webrtc.privite-ip']):
                raise IpErrorException

        if "webrtc.public-ip" in result:
            if not self._verify_ip(result['webrtc.public-v4-ip']) or not self._verify_ip(result['webrtc.public-v6-ip']):
                raise IpErrorException

        return result

    def set_privite_ip(self, value: str):
        """
        局域网 IP
        """
        self._privite_ip = value
        return self

    def set_public_ip(self, value: str):
        """
        外网 v4 IP
        """
        return self.set_public_v4_ip(value)

    def set_public_v4_ip(self, value: str):
        """
        外网 v4 IP
        """
        self._public_v4_ip = value
        return self

    def set_public_v6_ip(self, value: str):
        """
        外网 v6 IP
        """
        self._public_v6_ip = value
        return self

    def set_host_name(self, value: str):
        """
        hostname
        """
        self._host_name = value
        return self
