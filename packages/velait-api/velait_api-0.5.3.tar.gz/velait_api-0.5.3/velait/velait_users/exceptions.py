from django.utils.translation import gettext_lazy as _

from velait.main.exceptions import VelaitError


class UserAuthenticationError(VelaitError):
    name = "auth"
    description = _('Ошибка аутентификации')
    status_code = 400
