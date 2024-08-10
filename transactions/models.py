from django.db import models
from accounts.models import UserBankAccount
from transactions.constants import TRANSACTION_TYPE

# Create your models here.
class Transaction(models.Model):
    account = models.ForeignKey(to=UserBankAccount, related_name="transactions", on_delete=models.CASCADE)
    # an user may have multiple transactions
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    balance_after_transactions = models.DecimalField(decimal_places=2, max_digits=12)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    loan_approve = models.BooleanField(default=False)

    #for transfer money
    amount_for_transfer = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    #sender_id = models.ForeignKey(to=UserBankAccount, related_name="sender_details", on_delete=models.CASCADE, blank=True, null=True)
    sender_id = models.IntegerField(blank=True, null=True)

    class Meta:
        ordering = ['timestamp'] # for order the transactions depending on time