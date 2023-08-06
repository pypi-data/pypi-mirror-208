class DatabaseError(Exception):
    pass


class DeleteError(DatabaseError):
    pass


class SaveError(DatabaseError):
    def __init__(self, message: str, column: str = None):
        super().__init__(message)
        self.column = column
