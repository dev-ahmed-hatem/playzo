from django.contrib.auth.admin import UserAdmin
from .models import User


class UserAdminForm(UserAdmin):
    model = User

    list_display = ('username', 'name', 'role', 'is_superuser')
    list_filter = ('username', 'name', 'role', 'is_superuser')
    fieldsets = [
        ("Personal Information", {'fields': ['name', 'role']}),
        ("Authentication", {'fields': ['username', 'password']}),
        ("Permissions", {'fields': ['is_active', 'is_superuser', 'user_permissions']}),
        ("Custom Permissions", {'fields': ['permissions']}),
    ]
    add_fieldsets = [
        (None, {'fields': ['username', 'password1', 'password2', 'name', 'role', 'is_active', 'is_superuser']}),
    ]
