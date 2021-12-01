from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserAdminCreationForm, UserAdminChangeForm


User = get_user_model()

# Remove Group Model from admin. We're not using it.
# admin.site.unregister(Group)


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the custom User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['email', 'date_joined', 'get_full_name', 'last_joined', 'is_active', 'is_superuser',
                    'is_customer',
                    'is_superuser', 'is_seller',]
    list_filter = ['date_joined', 'email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ( 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_superuser', 'is_customer', 'is_seller','is_active', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}  # add required field
         ),
    )
    search_fields = ['email']
    ordering = ['email']
    readonly_fields = ('id', 'date_joined', 'last_joined')  # to prevent from changing
    # filter_horizontal = ()   # Enabling this distorts Gropus and permission table


class CustomerAdmin(admin.ModelAdmin):
    list_display = ['__str__']


# Register your models here.
admin.site.register(User, UserAdmin)


