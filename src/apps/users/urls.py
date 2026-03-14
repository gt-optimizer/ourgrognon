from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='users/login.html',
        redirect_authenticated_user=True,
    ), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(), name='logout'),
    path('profil/', views.profile, name='profile'),
]