from .module import Module
from .browser_enum import MatchType
from .exception import UrlErrorException


class BasicMatch(Module):
    def __init__(self):
        super(BasicMatch, self).__init__()
        self._target_url = None
        self._match_type = MatchType.FULL
        self._match_break = None
        self._user_agent = None

    def _to_dict(self):
        """
        解析成 dict
        """
        result = {
            "target_url": self._target_url,
            "match_type": self._match_type.value,
            "match_break": self._bool_to_int(self._match_break),
        }

        if self._user_agent is not None:
            result['user_agent'] = self._user_agent

        return result

    def set_target_url(self, value: str):
        """
        目标域名
        """
        self._target_url = value
        return self

    def set_match_type(self, value: MatchType):
        """
        匹配模式
        """
        self._match_type = value
        return self

    def set_match_break(self, value: bool):
        """
        如果是正则匹配，是否匹配成功后就跳出匹配
        """
        self._match_break = value
        return self

    def set_user_agent(self, value: str):
        """
        修改 User-Agent
        """
        self._user_agent = value
        return self
