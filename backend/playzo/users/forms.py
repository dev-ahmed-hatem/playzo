from django.contrib.auth.admin import UserAdmin
from .models import User


class UserAdminForm(UserAdmin):
    model = User

    list_display = ('username', 'name', 'is_superuser', 'is_moderator')
    list_filter = ('username', 'name', 'is_superuser', 'is_moderator')
    fieldsets = [
        ("Personal Information", {'fields': ['name']}),
        ("Authentication", {'fields': ['username', 'password']}),
        ("Permissions", {'fields': ['is_active', 'is_superuser', 'is_moderator', 'user_permissions']}),
        ("Custom Permissions", {'fields': ['permissions']}),
    ]
    add_fieldsets = [
        (None, {'fields': ['username', 'password1', 'password2', 'name', 'is_active', 'is_superuser', 'is_moderator']}),
    ]
