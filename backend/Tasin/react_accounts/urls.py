#react_accounts/urls.py
from django.urls import path
from .views import LoginView, SignupView, FrontendAppView

urlpatterns = [
    path('api/login/', LoginView.as_view()),
    path('api/signup/', SignupView.as_view()),
    # Catch-all: serve React app for all other routes
    path('', FrontendAppView.as_view(), name='react-app'),
]
