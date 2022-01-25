from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from prospector.apps.users.models import User


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    pass
