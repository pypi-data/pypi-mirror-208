import threading

from django.utils.timezone import now

from velait.main.utils import get_user_ip

local_thread = threading.local()


def get_current_data(key: str):
    return getattr(local_thread, key, None)


class LoggingValuesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_ip = get_user_ip(request)

        local_thread.operation_start = now()
        local_thread.user_ip = user_ip
        local_thread.user = request.user

        return self.get_response(request)
