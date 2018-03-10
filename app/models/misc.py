class CachedObj(object):
    def __init__(self, creator_fn):
        self.creator = creator_fn
        self._val = None

    @property
    def value(self):
        if not self._val:
            self._val = self.creator()
        return self._val
