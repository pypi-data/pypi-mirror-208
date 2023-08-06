from rest_framework import serializers
from user_sessions.models import Session


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = (
            "expire_date",
            "user_agent",
            "last_activity",
            "ip",
        )
