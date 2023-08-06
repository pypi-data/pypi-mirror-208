class DQLError(RuntimeError):
    pass


class NotFoundError(Exception):
    pass


class DatasetNotFoundError(NotFoundError):
    pass


class StorageNotFoundError(NotFoundError):
    pass


class PendingIndexingError(Exception):
    """An indexing operation is already in progress."""
