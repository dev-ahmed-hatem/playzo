from django.contrib import admin
from .models import User
from django.contrib.auth.models import Group
from .forms import UserAdminForm

admin.site.register(User, UserAdminForm)
admin.site.unregister(Group)
