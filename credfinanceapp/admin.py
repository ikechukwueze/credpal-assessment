from django.contrib import admin
from .models import Account, UserProfile, Wallet, UserWallet, WalletBalance



class AccountAdmin(admin.ModelAdmin):
    readonly_fields = ('password',)

class UserProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('email', 'bvn',)


admin.site.register(Account, AccountAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Wallet)
admin.site.register(UserWallet)
admin.site.register(WalletBalance)