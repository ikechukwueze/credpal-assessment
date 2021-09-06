import re
from django.contrib import auth
from django.contrib.auth import tokens
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str, smart_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import EmailMessage


from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from .models import Account, UserProfile, Wallet, WalletBalance, UserWallet


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, min_length=2)
    last_name = serializers.CharField(required=True, min_length=2)
    password = serializers.CharField(required=True, min_length=8, max_length=30, write_only=True)
    bvn = serializers.IntegerField(required=False)

    class Meta:
        model = Account
        fields = (
            'first_name',
            'last_name',
            'email',
            'bvn',
            'password',
        )
    
    def validate(self, attrs):
        first_name = attrs.get('first_name', '')
        last_name = attrs.get('last_name', '')
        password = attrs.get('password', '')
        
        if not (first_name.isalnum() or last_name.isalnum()):
            raise serializers.ValidationError({'error':'Name must be alphanumeric'})

        if password.isnumeric():
            raise serializers.ValidationError({'error':'Password must be alphanumeric'})
        
        bvn = attrs.get('bvn', None)
        if bvn is not None:
            if len(str(bvn)) != 11:
                raise serializers.ValidationError({'error':'Invalid BVN'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('bvn', '')
        return Account.objects.create_user(**validated_data)




class SignInSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    tokens = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = Account
        fields = ('email', 'password', 'tokens')

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')
        user = auth.authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed('Invalid credentials')
        
        attrs['tokens'] = user.tokens()
        return attrs



class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True, min_length=8, write_only=True)
    old_password = serializers.CharField(required=True, min_length=8, write_only=True)

    class Meta:
        model = Account
        fields = ('new_password', 'old_password')
    
    def validate(self, attrs):
        old_password = attrs.get('old_password', '')
        new_password = attrs.get('new_password', '')
        
        user = self.context['request'].user
        if not user.check_password(old_password):
            raise serializers.ValidationError({"error": "Old password incorrect"})
        return attrs
        
        

class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.CharField(read_only=True)
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    bvn_verified = serializers.CharField(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = (
            'user',
            'first_name',
            'last_name',
            'bvn',
            'bvn_verified',
            'profile_picture',
        )





class WalletSerializer(serializers.ModelSerializer):
    wallet_category = serializers.CharField(read_only=True)

    class Meta:
        model = Wallet
        fields = ('wallet_category',)




class UserWalletSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = UserWallet
        fields = ('wallet',)



class WalletBalanceSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = WalletBalance
        fields = '__all__'



class TransferFundsSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    wallet = WalletSerializer(read_only=True)
    category = serializers.CharField(required=True, write_only=True)
    receiver = serializers.EmailField(required=True, write_only=True)
    amount = serializers.DecimalField(max_digits=8, decimal_places=2, min_value=500, write_only=True, required=True)

    class Meta:
        model = WalletBalance
        fields = ('owner', 'wallet', 'category', 'receiver', 'amount')
    
    def validate(self, attrs):
        #category = attrs.pop('category', '')
        sender_wallet = attrs.pop('category')
        amount = attrs.get('amount', 0)
        receiver = attrs.pop('receiver', '')

        try:
            sender_wallet = Wallet.objects.get(wallet_category=sender_wallet)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'error':'Invalid Wallet type'})

        try:
            receiver_account = Account.objects.get(email=receiver)
            receiver_profile = UserProfile.objects.get(user=receiver_account)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({'error':'Recipient does not exist'})

        sender = self.context['request'].user
        sender_profile = UserProfile.objects.get(user=sender)
        if not sender_profile.bvn_verified:
            raise serializers.ValidationError({'error':'BVN not verified. You can not perform this transaction'})

        sender_acc = WalletBalance.objects.get(owner=sender_profile, wallet=sender_wallet)
        if sender_acc.balance < amount:
            raise serializers.ValidationError({'error': 'Insufficient funds.'})
        
        attrs['sender'] = sender_profile
        attrs['receiver'] = receiver_profile
        attrs['wallet'] = sender_wallet
        return attrs

    



class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    class Meta:
        fields = ['email']
    
    def validate(self, attrs):
        email = attrs.get('email', '')
        try:
            Account.objects.filter(email=email).exists()
            user = Account.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)

            current_site = get_current_site(request=self.context['request']).domain
            relative_link = reverse('api-password-reset', kwargs={'uidb64':uidb64, 'token':token})
            absolute_url = 'http://' + current_site + relative_link
            email_body = f'Use this link to reset your password {absolute_url}'
            data = {
                'email_body':email_body,
                'to_email': user.email,
                'email_subject':'Reset your password'
                }
            email_message = EmailMessage(
                subject=data['email_subject'],
                body = data['email_body'],
                to = (data['to_email'],)
            )
            email_message.send()

        except ObjectDoesNotExist:
            raise serializers.ValidationError({'error':'Account does not exist'})

        return super().validate(attrs)



class ResetPasswordSerializer(serializers.Serializer):

    password = serializers.CharField(min_length=8, required=True, write_only=True)
    token = serializers.CharField(required=True, write_only=True)
    uidb64 = serializers.CharField(required=True, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']
    
    def validate(self, attrs):
        password = attrs.get('password')
        token = attrs.get('token')
        uidb64 = attrs.get('uidb64')
        
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', 401)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', 401)
        
        return attrs