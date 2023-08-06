from flask import request


class KwargsFlask:
    @classmethod
    def get_kwargs(cls, SETTINGS):
        return {
            'remote_addr': cls.remote_addr_validate(),
            'user': cls.user_validate(SETTINGS),
        }

    @classmethod
    def remote_addr_validate(cls):
        try:
            return {k: v for k, v in request.headers.items()}
        except RuntimeError:
            pass

    @classmethod
    def user_validate(cls, SETTINGS):
        try:
            headers = {}
            for header in SETTINGS.USER_VALIDATE_HEADERS:
                headers.update(
                    {
                        header: request.headers.get(header)
                    }
                )
            return str(headers)
        except RuntimeError:
            pass
