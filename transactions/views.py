from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, ListView
from . models import Transaction
from .forms import Withdraw_Form, DepositeForm, Loan_Form, TransferMoneyForm
from .constants import DEPOSIT, WITHDRAWAL, LOAN, LOAN_PAID, TRANSFER
from django.contrib import messages
from datetime import datetime
from django.db.models import Sum
from django.views import View
from django.urls import reverse_lazy
from django.views.generic import FormView
from accounts.models import UserBankAccount

#for sending emails
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount 
    })

    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()


class TransectionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = "transactions/transantion_form.html"
    model = Transaction
    title = ''
    success_url = reverse_lazy("transaction_report")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'account':self.request.user.account
        })
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title':self.title
        })
        context["status"] = Transaction.is_bankrupt
        return context
    
class DepositView(TransectionCreateMixin):
    form_class = DepositeForm
    title = 'Deposit'

    def get_initial(self):
        initial = {'transaction_type': DEPOSIT}
        return initial

    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.account
        account.balance += amount 
        account.save(
            update_fields=[
                'balance'
            ]
        )

        messages.success(
            self.request,
            f'{"{:,.2f}".format(float(amount))}$ was deposited to your account successfully'
        )

        send_transaction_email(self.request.user, amount, "Deposit Email", "transactions/deposit_money.html")

        return super().form_valid(form)

class WithDrawView(TransectionCreateMixin):
    form_class = Withdraw_Form
    title = "WithDraw Money"

    def get_initial(self):
        initial = {"transaction_type":WITHDRAWAL}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        self.request.user.account.balance -= form.cleaned_data.get('amount')
        self.request.user.account.save(update_fields=['balance'])
        messages.success(self.request, f"Money Withdraw Successfully!")
        
        send_transaction_email(self.request.user, amount, "Deposit Email", "transactions/withdraw_money.html")

        return super().form_valid(form)

class LoanRequestView(TransectionCreateMixin):
    form_class = Loan_Form
    title = "Request For Loan"

    def get_initial(self):
        initial = {"transaction_type":LOAN}
        return initial
    
    def form_valid(self, form):
        amount = form.cleaned_data.get("amount")
        current_loan_count = Transaction.objects.filter(account = self.request.user.account, transaction_type = LOAN, loan_approve = True).count()

        if current_loan_count >= 3:
            return HttpResponse("You have cross your limit of taking loan!")

        messages.success(self.request, f"Loan Request sent Successfully! Admin will approve your request very soon!")

        send_transaction_email(self.request.user, amount, "Loan Request Email", "transactions/loan_request_email.html")
        
        return super().form_valid(form)

class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transactions/transaction_report.html"
    balance = 0
    model = Transaction

    def get_queryset(self):
        queryset =  super().get_queryset().filter(
            account = self.request.user.account
        )

        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')

        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            queryset = queryset.filter(timestamp__date__gte=start_date, timestamp__date__lte=end_date)

            self.balance = Transaction.objects.filter(
                timestamp__date__gte=start_date, timestamp__date__lte=end_date
            ).aggregate(Sum('amount'))['amount__sum']

        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'account':self.request.user.account
        })
        return context
    
class PayLoanView(LoginRequiredMixin, View):
    def get(self, request, loan_id):
        loan = get_object_or_404(Transaction, id = loan_id)

        if loan.loan_approve:
            user_account = loan.account

            if loan.amount < user_account.balance:
                user_account.balance -= loan.amount
                loan.balance_after_transactions = user_account.balance
                user_account.save()
                loan.loan_approve = True
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect('loan_list')
            
            else:
                messages.error(self.request, "Loan request is greater than available balance!")
            return redirect('loan_list')
            
class LoanListView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "transactions/loan_request.html"
    context_object_name = "loans"
    
    def get_queryset(self):
        user_account = self.request.user.account
        queryset = Transaction.objects.filter(account = user_account, transaction_type=LOAN)
        return queryset


class MoneyTransferView(FormView, LoginRequiredMixin):
    form_class = TransferMoneyForm
    template_name = "transactions/money_transfer.html"
    success_url = reverse_lazy("transfer_money")

    def form_valid(self, form):
        user_account = self.request.user.account
        sender_id = form.cleaned_data.get('sender_id')
        amount = form.cleaned_data.get('amount_for_transfer')

        sender_acc = UserBankAccount.objects.filter(account_no = sender_id).first()

        if user_account.balance == 0:
            messages.error(self.request, "Your Account is empty!")

        if sender_acc is not None:
            user_account.balance -= amount
            sender_acc.balance += amount

            user_account.save(
                update_fields=[
                    'balance'
                ]
            )
            sender_acc.save(
                update_fields=[
                    'balance'
                ]
            )
            messages.success(self.request, "Money transferred Successfully!")

        else:
            messages.error(self.request, "Account doesn't found!")

        return super().form_valid(form)