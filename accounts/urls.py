from django.urls import path
from accounts.views import UserRegistrationView, UserLogInView, UserLogoutView, UserProfileView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="register"),
    path('login/', UserLogInView.as_view(), name="login"),
    path('logout/', UserLogoutView.as_view(), name="logout"),
    path('profile/', UserProfileView.as_view(), name="profile"),
]
