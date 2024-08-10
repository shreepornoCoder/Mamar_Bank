from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.contrib.auth import login, logout
from accounts.forms import UserRegistrationForm, UserUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm
from .forms import ChangePasswordFormUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash

from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

# Create your views here.
def send_transaction_email(user, amount, subject, template):
    message = render_to_string(template, {
        'user' : user,
        'amount' : amount 
    })

    send_email = EmailMultiAlternatives(subject, '', to=[user.email])
    send_email.attach_alternative(message, "text/html")
    send_email.send()

class UserRegistrationView(FormView):
    form_class = UserRegistrationForm
    success_url = reverse_lazy("register")
    template_name = 'accounts/user_registrations.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        print(user)
        return super().form_valid(form)

class UserProfileView(View):
    template_name = 'accounts/profile.html'

    #When the user visits the profile page, a pre-filled form with the user's information is displayed.
    #just for displaying the form
    def get(self, request):
        form = UserUpdateForm(instance = request.user) # filled with data by this instance = request.user
        return render(request, self.template_name, {"form":form})
    
    # for updating
    def post(self, request):
        form = UserUpdateForm(request.POST, instance=request.user)
        # through request.POST it creates another instance of UserUpdateForm
        if form.is_valid:
            form.save()
            return redirect("homepage")
        
        return render(request, self.template_name, {"form":form})

class UserLogInView(LoginView):
    template_name = "accounts/user_login.html"
    def get_success_url(self):
        return reverse_lazy('homepage')
    
class UserLogoutView(LogoutView):
    def get_success_url(self):
        # if self.request.user.is_authenticated:
        logout(self.request)
        return reverse_lazy("homepage")

def ChangePasswordView(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = SetPasswordForm(user = request.user, data = request.POST)
            if form.is_valid():
                form.save()
                send_transaction_email(request.user, 0, "Password Change", "accounts/pass_change_email.html")
                update_session_auth_hash(request, form.user)
                return redirect('profile')
        else:
            form = SetPasswordForm(user = request.user)

        return render(request, 'accounts/passchange.html', {'form': form})
    
    else:
        return render('profile')


# class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
#     form_class = ChangePasswordForm
#     success_url = reverse_lazy('home')
#     template_name = 'accounts/passchange.html'

#     def form_valid(self, form):
#         messages.success(self.request, "Password Updated Successfully! Check Your Email!")
#         return super().form_valid(form)

#     def form_invalid(self, form):
#         messages.error(self.request, "Something went wrong!")
#         return super().form_invalid(form)