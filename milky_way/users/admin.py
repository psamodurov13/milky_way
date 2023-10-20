from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User
from django.utils.translation import gettext_lazy as _


class CustomAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("last_name", "first_name", "second_name", "email", "phone", "office")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(User, CustomAdmin)