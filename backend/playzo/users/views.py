from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from .serializers import UserSerializer
from .models import User


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = User.objects.filter(is_superuser=False)

        search_query = self.request.query_params.get('search', None)

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(username__icontains=search_query) |
                Q(national_id__icontains=search_query) |
                Q(phone__icontains=search_query)
            )

        is_superuser_param = self.request.query_params.get('is_superuser', None)
        if is_superuser_param:
            if is_superuser_param.lower() == 'true':
                queryset = queryset.filter(is_superuser=True)

        return queryset

    @action(detail=True, methods=['GET'])
    def permissions_list(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
            permissions = [str(perm) for perm in user.permissions.all()]
            return Response(permissions)
        except Exception:
            return Response({'detail': _('عميل غير موجود')}, status=status.HTTP_404_NOT_FOUND)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for the currently authenticated user.
    Expected payload:
    {
        "current_password": "old123",
        "new_password": "new123",
        "confirm_password": "new123"
    }
    """
    user = request.user
    data = request.data

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    # Validate current password
    if not user.check_password(current_password):
        return Response(
            {"current_password": ["كلمة المرور الحالية غير صحيحة"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validate new password match
    if new_password != confirm_password:
        return Response(
            {"confirm_password": ["كلمتا المرور غير متطابقتان"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Optional: add validation rules (min length, complexity, etc.)
    if len(new_password) < 8:
        return Response(
            {"new_password": ["كلمة المرور يجب أن تكون 8 أحرف على الأقل"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Save new password
    user.set_password(new_password)
    user.save()

    return Response(
        {"detail": "تم تغيير كلمة المرور بنجاح"},
        status=status.HTTP_200_OK,
    )
