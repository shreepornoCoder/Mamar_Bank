from typing import Any
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django import forms
from .constants import ACCOUNT_TYPE, GENDER
from django.contrib.auth.models import User
from . models import UserBankAccount, UserAddress, Bank

class UserRegistrationForm(UserCreationForm):
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type":'date'}))
    gender = forms.ChoiceField(choices=GENDER)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'account_type', 'gender', 'birth_date', 'postal_code', 'country', 'city', 'street_address']
        #password1 -> enter pass
        #passwor21 -> confirm pass

    def save(self, commit=True):
        our_user = super().save(commit=False)

        if commit == True:
            our_user.save() #saved data in user model
            account_type = self.cleaned_data.get('account_type')
            gender = self.cleaned_data.get('gender')
            postal_code = self.cleaned_data.get('postal_code')
            country = self.cleaned_data.get('country')
            birth_date = self.cleaned_data.get('birth_date')
            city = self.cleaned_data.get('city')
            street_address = self.cleaned_data.get('street_address')

            UserAddress.objects.create(
                user = our_user, 
                street_address = street_address, 
                city = city, 
                postal_code = postal_code,
                country = country
            )
            UserBankAccount.objects.create(
                user = our_user, 
                account_type = account_type,
                gender = gender, 
                birth_date = birth_date,
                account_no = 1000 + our_user.id
            )

        return our_user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-100 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })

class UserUpdateForm(forms.ModelForm):
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=100)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=100)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={"type":'date'}))
    gender = forms.ChoiceField(choices=GENDER)
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class':(
                    'appearance-none block w-full bg-gray-200 '
                    'text-gray-100 border border-gray-200 rounded '
                    'py-3 px-4 leading-tight focus:outline-none '
                    'focus:bg-white focus:border-gray-500'
                )
            })

        if self.instance: #user account
            try:
                user_account = self.instance.account
                user_address = self.instance.address 

            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None

            if user_account:
                self.fields['account_type'].initial = user_account.account_type
                self.fields['gender'].initial = user_account.gender 
                self.fields['birth_date'].initial = user_account.birth_date
                self.fields['street_address'].initial = user_address.street_address
                self.fields['city'].initial = user_address.city
                self.fields['postal_code'].initial = user_address.postal_code
                self.fields['country'].initial = user_address.country

    def save(self, commit = True):
        user = super().save(commit=True)
        if commit:
            user.save()

            # get_or_create() -> if user doesn't have account it will create a new one, else we will the account that already exits
            user_account, created = UserBankAccount.objects.get_or_create(user = user) 
            user_address, created = UserAddress.objects.get_or_create(user = user)

            user_account.account_type = self.cleaned_data['account_type']
            user_account.gender = self.cleaned_data['gender']
            user_account.birth_date = self.cleaned_data['birth_date']
            user_account.save()

            user_address.street_address = self.cleaned_data['street_address']
            user_address.city = self.cleaned_data['city']
            user_address.country = self.cleaned_data['country']
            user_address.save()

        return user

class BankForm(forms.ModelForm):
    class Meta:
        model = Bank
        fields = "__all__"

class ChangePasswordFormUser(PasswordChangeForm):
    class Meta:
        old_password = forms.CharField(widget=forms.PasswordInput())
        new_password = forms.CharField(widget=forms.PasswordInput())
        confirm_password = forms.CharField(widget=forms.PasswordInput()) 