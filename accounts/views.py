from django.shortcuts import render, redirect
from django.views.generic import FormView
from django.contrib.auth import login, logout
from accounts.forms import UserRegistrationForm, UserUpdateForm
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View

# Create your views here.
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