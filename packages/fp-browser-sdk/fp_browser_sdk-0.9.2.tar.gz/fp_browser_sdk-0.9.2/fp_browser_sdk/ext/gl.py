from .module import Module


class Gl(Module):
    def __init__(self):
        super(Gl, self).__init__()
        self._vendor = None
        self._renderer = None
        self._version = None
        self._shading_language_version = None

    def _to_dict(self):
        """
        解析成 dict
        """
        result = {}

        if self._vendor is not None:
            result["gl.vendor"] = self._vendor

        if self._renderer is not None:
            result["gl.renderer"] = self._renderer

        if self._version is not None:
            result["gl.version"] = self._version

        if self._shading_language_version is not None:
            result["gl.shading-language-version"] = self._shading_language_version

        return result

    def set_vendor(self, value: str):
        """
        vendor
        """
        self._vendor = value
        return self

    def set_renderer(self, value: str):
        """
        renderer
        """
        self._renderer = value
        return self

    def set_version(self, value: str):
        """
        version
        """
        self._version = value
        return self

    def set_shading_language_version(self, value: str):
        """
        shading-language-version
        """
        self._shading_language_version = value
        return self
