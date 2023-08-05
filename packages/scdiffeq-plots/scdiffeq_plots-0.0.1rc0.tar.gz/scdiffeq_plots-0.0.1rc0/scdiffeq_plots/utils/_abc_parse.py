
from abc import ABC
NoneType = type(None)


class NoneTypeMixIn(object):
    def __init__(self, *args, **kwargs):
        ...

    def _is_none(self, val):
        return isinstance(val, NoneType)


class ABCParse(ABC, NoneTypeMixIn):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self._PARAMS = {}
        self._IGNORE = ["self", "__class__"]

    def __parse__(self, kwargs, public=[], private=[], ignore=[]):

        self._IGNORE += ignore

        if len(public) > 0:
            private = list(kwargs.keys())

        for key, val in kwargs.items():
            if not key in self._IGNORE:
                self._PARAMS[key] = val
                if (key in private) and (not key in public):
                    key = f"_{key}"
                setattr(self, key, val)