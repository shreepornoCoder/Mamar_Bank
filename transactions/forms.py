from typing import Any
from django import forms
from transactions.models import Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type']
    
    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account')
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].disabled = True # it stay disabled
        self.fields['transaction_type'].widget = forms.HiddenInput() # it will stay hidden from user

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transactions = self.account.balance

        return super().save(commit=commit)
    
class DepositeForm(TransactionForm):
    #use clean function by writing clean_ and then field that I want to filter
    def clean_amount(self):
        min_deposite_amount = 100
        amount = self.cleaned_data.get('amount')

        if amount < min_deposite_amount:
            raise forms.ValidationError(f"You need to deposite aleast {min_deposite_amount} $")
        
        return amount
    
class Withdraw_Form(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdraw_amount = 500
        max_withdraw_amount = 20000
        balance = account.balance
        amount = self.cleaned_data.get('amount')

        if amount > balance:
            raise forms.ValidationError(f"You have {balance}$ in your account. You can't withdraw more than your account balance")

        if amount < min_withdraw_amount:
            raise forms.ValidationError(f"You can withdraw at least {min_withdraw_amount}$")
        
        if amount > max_withdraw_amount:
            raise forms.ValidationError(f"You can withdraw less than {max_withdraw_amount}$")
        
        return amount

class Loan_Form(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")

        return amount
    
class TransferMoneyForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["amount_for_transfer", "sender_id"]

    def clean_amount_for_transfer(self):
        amount = self.cleaned_data.get("amount_for_transfer")

        # if amount > self.reuqest.account.balance or 
        if amount <= 0:
            return forms.ValidationError("Inalid Money Amount!")
        
        # if self.account.balance == 0:
        #     return forms.ValidationError("Your balance is empty!")
        
        return amount