

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.db.models import F


from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.utils.encoding import DjangoUnicodeDecodeError, smart_str
from django.utils.http import urlsafe_base64_decode
from .forms import SignUpForm


from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken


from .models import Account, UserProfile, Wallet, WalletBalance
from .serializers import RegistrationSerializer, ResetPasswordEmailRequestSerializer, SignInSerializer, ChangePasswordSerializer
from .serializers import WalletBalanceSerializer, TransferFundsSerializer, ResetPasswordSerializer
from .serializers import UserProfileSerializer
from .custom_utils import create_profile_and_wallet



# API VIEWS

class RegistrationView(generics.GenericAPIView):

    serializer_class = RegistrationSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)
        new_account = serializer.save()
        bvn = serializer.validated_data.get('bvn', None)
        create_profile_and_wallet(new_account=new_account, bvn=bvn)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class SignInView(generics.GenericAPIView):

    serializer_class = SignInSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)



class ChangePasswordView(generics.GenericAPIView):

    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated, )

    def patch(self, request):
        user_data = request.data
        context = {'request':request}
        serializer = self.serializer_class(data=user_data, context=context)
        serializer.is_valid(raise_exception=True)

        account = request.user
        account.set_password(serializer.validated_data['new_password'])
        account.save()

        response = {'success': True, 'message':'Password was changed successfully'}
        return Response(response, status=status.HTTP_200_OK)




class ResetPasswordView(generics.GenericAPIView):

    permission_classes = (AllowAny, )
    serializer_class = ResetPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {'success': True, 'message':'Password was reset successfully'}
        return Response(response, status=status.HTTP_200_OK)
        



class RetrieveUpdateProfileView(generics.RetrieveUpdateAPIView):

    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'email'

    def get_queryset(self):
        return self.queryset.filter(email=self.request.user.email)




class RetrieveWalletBalanceView(generics.RetrieveAPIView):

    queryset = WalletBalance.objects.all()
    serializer_class = WalletBalanceSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'pk'
    
    

class TransferFundsView(generics.GenericAPIView):

    serializer_class = TransferFundsSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_data = request.data
        context = {'request': request}
        serializer = self.serializer_class(data=user_data, context=context)
        serializer.is_valid(raise_exception=True)

        sender = serializer.validated_data.pop('sender')
        receiver = serializer.validated_data.pop('receiver')
        
        wallet = serializer.validated_data.pop('wallet')
        amount = serializer.validated_data.pop('amount')
        
        sender_acc = WalletBalance.objects.get(owner=sender, wallet=wallet)
        receiver_acc = WalletBalance.objects.get(owner=receiver, wallet=wallet)

        with transaction.atomic():
            if sender_acc.balance > amount:
                sender_acc.balance = F('balance') - amount
                sender_acc.save(update_fields=['balance'])
                receiver_acc.balance = F('balance') + amount
                receiver_acc.save(update_fields=['balance'])
                response = {'success': True, 'message':'Transaction complete'}
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {'success': False, 'message':'Transaction was not successful'}
                return Response(response, status=status.HTTP_400_BAD_REQUEST)




class RequestPasswordResetEmailView(generics.GenericAPIView):

    serializer_class = ResetPasswordEmailRequestSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        context = {'request': request}
        print(request.data)
        serializer = self.serializer_class(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        response = {'success': True, 'message':'Password reset email sent'}
        return Response(response, status=status.HTTP_200_OK)




class PasswordTokenCheckView(generics.GenericAPIView):
    
    permission_classes = (AllowAny,)
    
    def get(self, request, uidb64, token):
        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = Account.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error':'Token invalid, request'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({
                'success':True,
                'message':'Valid credentials',
                'uidb64':uidb64,
                'token':token
                })
        except DjangoUnicodeDecodeError as identifier:
            if not PasswordResetTokenGenerator.check_token(user):
                return Response({'error':'Token is not valid'}, status=status.HTTP_401_UNAUTHORIZED)














#VIEWS

@login_required(login_url='sign_in_view')
def home_page(request):
    context = {}
    user_profile = UserProfile.objects.get(email=request.user.email)
    wallet_balance = WalletBalance.objects.filter(owner=user_profile)

    context['user'] = user_profile
    context['wallets'] = wallet_balance
    return render(request, 'credfinanceapp/index.html', context=context)



def sign_up_view(request):
    sign_up_form = SignUpForm()
    if request.method == "POST":
        sign_up_form = SignUpForm(request.POST)
        if sign_up_form.is_valid():
            new_account = sign_up_form.save()
            email = sign_up_form.cleaned_data.get("email")
            password = sign_up_form.cleaned_data.get("password1")
            bvn = sign_up_form.cleaned_data.get("bvn", None)

            create_profile_and_wallet(new_account=new_account, bvn=bvn)
            new_user = authenticate(request, email=email, password=password)
            login(request, new_user)
            return redirect("home_page")

    return render(
        request, 
        "credfinanceapp/sign-up.html",
        {"signupform": sign_up_form}
    )



def sign_in_view(request):
    if request.method == "POST":
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home_page")
        else:
            messages.error(request, "Invalid username or password")
    
    return render(
        request, 
        "credfinanceapp/sign-in.html",
    )


def sign_out_view(request):
    logout(request)
    return redirect("sign_in_view")





















