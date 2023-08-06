class Config:
    def __init__(self):
        self.HEADERS = True
        self._USER_VALIDATE_HEADERS = [
            'X-User-Id',
            'X-Auth-User-Id'
        ]

    @property
    def USER_VALIDATE_HEADERS(self):
        return self._USER_VALIDATE_HEADERS

    @USER_VALIDATE_HEADERS.setter
    def USER_VALIDATE_HEADERS(self, value):
        if isinstance(value, list):
            raise ValueError(f'{value} must be a list in USER_VALIDATE')
        self._USER_VALIDATE = value
