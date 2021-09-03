from rest_framework import serializers
from .models import Account


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True)
    bvn = serializers.IntegerField(required=False)

    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters."})
        if password.isnumeric():
            raise serializers.ValidationError({"password": "Password must contain only numbers."})
        if password and password2 and password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})
        
        
        new_account = Account(
            email=self.validated_data['email'],
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name']
        )
        new_account.set_password(password)
        new_account.save()
        return new_account

    class Meta:
        model = Account
        fields = (
            'first_name',
            'last_name',
            'email',
            'bvn',
            'password',
            'password2',
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True}
            }



class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)


    def save(self):
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        
        if password != password2:
            raise serializers.ValidationError({"password": "Passwords must match."})
        
        user = self.context['request'].user
        
        try:
            account = Account.objects.get(email=self.validated_data['email'])
            if account != user:
                return serializers.ValidationError({'response':'You are unauthorized'})
            if not account.check_password(self.validated_data['old_password']):
                raise serializers.ValidationError({"old_password": "Old password is not correct"})

        except Account.DoesNotExist:
            raise serializers.ValidationError({"email": "Email does not exist."})
        
        account.set_password(password)
        account.save()
        return account

    
    class Meta:
        model = Account
        fields = ('email', 'password', 'password2', 'old_password')
        extra_kwargs = {
            'password': {'write_only': True},
            'password2': {'write_only': True},
            'old_password': {'write_only': True}
            }