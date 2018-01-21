2


class LoadError(ValueError):
    def __init__(self, errors):
        self.errors = errors


class TableModificationFailedError(ValueError):
    pass


class InsertFailedError(TableModificationFailedError):
    def __init__(self, table, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table
        self.item = item


class UpdateFailedError(TableModificationFailedError):
    def __init__(self, table, item, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table
        self.item = item
