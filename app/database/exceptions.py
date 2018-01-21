class DatabaseError(ValueError):
    pass


class SerializationError(ValueError):
    pass


class LoadError(SerializationError):
    def __init__(self, errors):
        self.errors = errors


class NotFoundError(DatabaseError):
    def __init__(self, table, _id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table
        self._id = _id


class TableModificationFailedError(DatabaseError):
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


class DeletionFailedException(TableModificationFailedError):
    def __init__(self, table, _id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = table
        self._id = _id
