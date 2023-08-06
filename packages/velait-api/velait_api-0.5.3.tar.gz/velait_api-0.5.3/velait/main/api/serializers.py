from django.utils import timezone
from rest_framework import serializers

from velait.main.models import BaseModel


class BaseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = BaseModel
        fields = (
            "id",
            "created_at",
            "created_by_id",
            "updated_at",
            "updated_by_id",
        )
        read_only_fields = (
            "id",
            "created_at",
            "created_by_id",
            "updated_at",
            "updated_by_id",
        )
        abstract = True

    def get_user_id(self, instance):
        raise NotImplementedError("You need to add get_user() function to your serializers")

    def update(self, instance, validated_data):
        try:
            validated_data['updated_by_id'] = self.get_user_id(instance)
            validated_data['updated_at'] = timezone.now()
        except NotImplementedError:
            pass

        return super(BaseSerializer, self).update(instance=instance, validated_data=validated_data)

    def create(self, validated_data):
        try:
            validated_data['created_by_id'] = self.get_user_id(self.context['request'].user)
        except NotImplementedError:
            pass

        return super(BaseSerializer, self).create(validated_data)


__all__ = ['BaseSerializer']
