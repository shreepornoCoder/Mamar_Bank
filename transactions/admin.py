from typing import Any
from django.contrib import admin
from .models import Transaction
from .views import send_transaction_email

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ["account", "amount", "balance_after_transactions", "transaction_type", "loan_approve"]

    def save_model(self, request, obj, form, change):
        obj.account.balance += obj.amount
        obj.balance_after_transaction = obj.account.balance
        send_transaction_email(obj.account.user, obj.amount, "Loan Approval", "transactions/loan_approval.html")
        obj.account.save()
        return super().save_model(request, obj, form, change)
