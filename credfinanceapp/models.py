from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver

from rest_framework.authtoken.models import Token


# Create your models here.


class MyAccountManager(BaseUserManager):
	def create_user(self, email, first_name, last_name, password=None):
		if not email:
			raise ValueError('Users must have an email address')
		if not first_name and last_name:
			raise ValueError('Please include your full name')

		user = self.model(
			email=self.normalize_email(email),
			first_name=first_name,
            last_name=last_name,
		)

		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, email, first_name, last_name, password):
		user = self.create_user(
			email=self.normalize_email(email),
			password=password,
			first_name=first_name,
            last_name=last_name,
		)
		user.is_admin = True
		user.is_staff = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=60, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_joined	= models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = MyAccountManager()

    def __str__(self):
	    return self.email

    def has_perm(self, perm, obj=None):
	    return self.is_admin

    def has_module_perms(self, app_label):
	    return True



# post save method for to create token for new account
@receiver(post_save, sender=Account)
def create_auth_token(sender, instance, created, **kwargs):
    if created:
        token = Token.objects.create(user=instance)



class UserProfile(models.Model):
	user = models.OneToOneField(Account, on_delete=models.CASCADE)
	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	bvn = models.IntegerField(blank=True, null=True)
	bvn_verified = models.BooleanField(default=False)
	profile_picture = models.ImageField(upload_to='profile_pictures', default='default_profile_pic.jpg')

	def __str__(self):
		return self.user.email



class Wallet(models.Model):
	wallet_category = models.CharField(max_length=255)

	def __str__(self):
		return self.wallet_category



class UserWallet(models.Model):
	owner = models.ForeignKey(Account, on_delete=models.CASCADE)
	wallet = models.ManyToManyField(Wallet, blank=True)

	def __str__(self):
		return self.owner.email



class WalletBalance(models.Model):
	owner = models.ForeignKey(Account, on_delete=models.CASCADE)
	wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
	balance = models.DecimalField(max_digits=8, decimal_places=2)

	def __str__(self):
		return self.owner.email




