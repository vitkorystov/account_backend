from django.contrib import admin
from .models import AccountsModel


class AccountsAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'name', 'balance', 'hold', 'status')
    list_display_links = ('unique_id', 'name')
    search_fields = ('name',)


admin.site.register(AccountsModel, AccountsAdmin)
