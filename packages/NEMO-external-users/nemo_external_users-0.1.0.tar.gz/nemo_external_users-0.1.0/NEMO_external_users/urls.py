from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from django.conf import settings


app_name = 'NEMO_external_users'

urlpatterns = [
    path("accounts/login/", views.login_user, name="login"),
    path("accounts/create/", views.create_account, name="create_account"),
    path("accounts/activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("admin/logout/", LogoutView.as_view(next_page="landing" if not settings.LOGOUT_REDIRECT_URL else None),
         name="logout"),
]

