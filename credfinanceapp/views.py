from django.shortcuts import render, redirect

from .models import Account, UserProfile, Wallet, UserWallet, WalletBalance

from .serializers import RegistrationSerializer, ChangePasswordSerializer
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import serializers, status


from django.contrib.auth import login, logout, authenticate
from .forms import SignUpForm

from .helper_functions import create_profile_and_wallet

# Create your views here.


def home_page(request):
    return render(request, 'credfinanceapp/index.html')


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
        "credfinanceapp/sign-up-.html",
        {"signupform": sign_up_form}
    )



def sign_in_view(request):
    return redirect("home_page")


def sign_out_view(request):
    logout(request)
    return redirect("sign_in_view")







@api_view(["POST",])
@permission_classes([AllowAny])
def registration_api_endpoint(request):
    serializer = RegistrationSerializer(data=request.data)
    data = {}
    if serializer.is_valid():
        new_account = serializer.save()
        bvn = serializer.validated_data.get('bvn', None)
        create_profile_and_wallet(new_account=new_account, bvn=bvn)

        data['response'] = 'New account created successfully.'
        data['email'] = new_account.email
        data['first_name'] = new_account.first_name
        data['last_name'] = new_account.last_name
        data['token'] = Token.objects.get(user=new_account).key
        return Response(data, status=status.HTTP_200_OK)
    else:
        data = serializer.errors
        #return Response(serializer.data, status=200)
        return Response(data, status=status.HTTP_400_BAD_REQUEST)



@api_view(["PUT",])
@permission_classes([IsAuthenticated])
def change_password_api_endpoint(request):
    serializer = ChangePasswordSerializer(data=request.data, context={'request':request})
    #user = request.user
    data = {}
    print(serializer)
    
    if serializer.is_valid():
        """
        email = serializer.validated_data['email']
        print(email)
        account = Account.objects.get(email=email)
        print(account)
        print(user)
        if account != user:
            return Response({'response':'You are unauthorized'})"""
        
        serializer.save()
        data['response'] = 'Password changed successfully'
        return Response(data, status=status.HTTP_200_OK)
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
