from logging import getLogger
from uuid import uuid4

from django.conf import settings
from django.utils import timezone
from auditlog.models import LogEntry
from django.dispatch import receiver
from user_sessions.models import Session
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed

from velait.main.utils import get_user_ip

User = get_user_model()
logger = getLogger(settings.DJANGO_LOGGER_NAME)


@receiver(user_logged_in)
def record_user_logged(sender, user: User, request, **kwargs):
    logger.info(f"User {user.pk} successfully logged in from {get_user_ip(request)} address")


@receiver(user_logged_out)
def record_user_logged_out(sender, request, user: User, **kwargs):
    logger.info(f"User {user.pk} successfully logged out from {get_user_ip(request)} address")


@receiver(user_login_failed)
def record_user_logged_out(sender, credentials: dict, request, **kwargs):
    logger.error(f"User with {credentials} credentials failed login from {get_user_ip(request)} address")


@receiver(pre_save, sender=User)
def add_password_policies(sender, instance: User, **kwargs):
    if instance._password is None:
        return

    try:
        User.objects.filter(pk__exact=instance.pk).exists()
    except User.DoesNotExist:
        return

    instance.password_changed_at = timezone.now()


try:
    from oauth2_provider.models import AccessToken
    from oauth2_provider.signals import app_authorized

    @receiver(app_authorized)
    def record_user_authorized_api(sender, request, token: AccessToken, **kwargs):
        user_ip, user_agent = get_user_ip(request), request.META.get('HTTP_USER_AGENT')

        last_session = Session.objects.create(
            session_key=str(uuid4()),
            session_data=token.token,
            expire_date=token.expires,
            last_activity=token.created,
            user_agent=user_agent,
            ip=user_ip,
            user=token.user,
        )

        logger.info(f"User {token.user} successfully logged in using API from {last_session.ip} address")

except ImportError:
    pass


def apply_logging(sender, instance: LogEntry, **kwargs):
    actor = instance.actor.pk if instance.actor is not None else "Unknown user"
    logger.info(f"{str(instance)} at {instance.timestamp} by {actor}. Changes: {instance.changes}")


post_save.connect(apply_logging, sender=LogEntry)
post_delete.connect(apply_logging, sender=LogEntry)
