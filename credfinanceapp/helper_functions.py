from .models import UserProfile, Wallet, UserWallet, WalletBalance

def create_profile_and_wallet(new_account, bvn):
    new_user_profile = UserProfile.objects.create(
            user=new_account,
            first_name=new_account.first_name,
            last_name=new_account.last_name
        )

    if bvn is not None:
        new_user_profile.bvn = bvn
        new_user_profile.save()

    default_wallet = Wallet.objects.get(wallet_category='Savings')
    new_account_wallet = UserWallet()
    new_account_wallet.owner = new_account
    new_account_wallet.save()
    new_account_wallet.wallet.add(default_wallet)
    
    WalletBalance.objects.create(
        owner=new_account,
        wallet=default_wallet,
        balance=1000)
