from ..middleware.thread_local_user_middleware import get_current_authenticated_user


class Auth:
    @staticmethod
    def get_current_user():
        return get_current_authenticated_user()
