from sqlalchemy.exc import IntegrityError


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class UserNotFacebookAuthed(InvalidUsage):
    def __init__(self):
        InvalidUsage.__init__(
            self,
            "User must be Facebook authenticated to perform this action",
            status_code=403)


class UserNotAdmin(InvalidUsage):
    def __init__(self):
        InvalidUsage.__init__(
            self,
            "User must be an Admin to perform this action",
            status_code=403)
