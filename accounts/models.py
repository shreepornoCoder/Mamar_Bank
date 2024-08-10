from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from accounts.constants import ACCOUNT_TYPE, GENDER

# Create your models here.
class UserBankAccount(models.Model):
    user = models.OneToOneField(to=User, related_name="account", on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True) # account no won't be same
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER)
    inital_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0, max_digits=12, decimal_places=2)

    def __str__(self):
        return str(self.account_no)

class UserAddress(models.Model):
    user = models.OneToOneField(to=User, related_name='address', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100, default="")
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user.email)
    
class Bank(models.Model):
    is_bankrupt = models.BooleanField(default=False)
