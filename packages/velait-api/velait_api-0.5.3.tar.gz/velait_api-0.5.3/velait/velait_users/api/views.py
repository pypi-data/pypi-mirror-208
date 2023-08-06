from rest_framework import permissions
from rest_framework.generics import ListAPIView

from velait.velait_users.api.serializers import UserSessionSerializer


class UserSessionsView(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSessionSerializer

    def get_queryset(self):
        return self.request.user.session_set.all().order_by('pk')
