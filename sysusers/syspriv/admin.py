from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import System, Account, Role, AdContainer, Department
from .forms import SystemPasswordForm
class SystemAdmin(admin.ModelAdmin):
    form = SystemPasswordForm

admin.site.register(System, SystemAdmin)

class RoleAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'system', 'internal_id', 'name', 'description']
    def has_add_permission(self, request, obj=None):
        return False
admin.site.register(Role, RoleAdmin)


class UserAdmin(admin.ModelAdmin):
    readonly_fields = ['id', 'system', 'internal_id', 'login', 'first_name', 'last_name', 'roles']
    def has_add_permission(self, request, obj=None):
        return False
admin.site.register(Account, UserAdmin)

admin.site.register(AdContainer)
admin.site.register(Department)
