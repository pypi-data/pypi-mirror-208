class InvalidReplicationMethodException(Exception):
    """Exception for errors related to replication methods"""

    def __init__(self, replication_method, message=None):
        msg = f"Invalid replication method {replication_method}!"

        if message is not None:
            msg = f'{msg} {message}'

        super().__init__(msg)


class UnsupportedKeyTypeException(Exception):
    """Raised if key type is not supported"""


class InvalidDateTimeException(Exception):
    """Raised if we find an invalid date-time value"""


class SyncException(Exception):
    """Raised if we there is an exception while syncing"""


class NoReadPrivilegeException(Exception):
    """Raised if the user has no read privilege on the Mongo DB"""

    def __init__(self, user, db_name):
        msg = f"The user '{user}' has no read privilege on the database '{db_name}'!"
        super().__init__(msg)
