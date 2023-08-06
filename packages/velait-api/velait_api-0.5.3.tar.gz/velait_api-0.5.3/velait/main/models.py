from uuid import uuid4

from django.db import models
from auditlog.registry import auditlog
from safedelete import HARD_DELETE_NOCASCADE
from safedelete.models import SafeDeleteModel
from django.contrib.postgres.indexes import BrinIndex
from django.utils.translation import gettext_lazy as _


class BaseModel(SafeDeleteModel):
    """ BaseModel should be added to every model """
    _safedelete_policy = HARD_DELETE_NOCASCADE

    uuid = models.UUIDField(_("Идентификатор"), unique=True, default=uuid4, editable=False)

    created_at = models.DateTimeField(_("дата создания"), auto_now_add=True)
    created_by_id = models.UUIDField(_("Создатель"), null=True)

    updated_at = models.DateTimeField(_("дата изменения"), auto_now=True)
    updated_by_id = models.UUIDField(_("Кто изменил"), null=True)

    queryable_fields = ("uuid", "created_at", "updated_at", "created_by_id", "updated_by_id")
    orderable_fields = ("uuid", "created_at", "updated_at", "created_by_id", "updated_by_id")

    class Meta:
        abstract = True
        indexes = (
            models.Index(fields=('id',)),
            BrinIndex(fields=('uuid',)),
        )
        ordering = (
            'uuid',
        )


register_model_audit = auditlog.register
