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
    path('mot-de-passe/modifier/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change.html',
             success_url='/mot-de-passe/modifier/succes/'
         ),
         name='password_change'),
    path('mot-de-passe/modifier/succes/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'
         ),
         name='password_change_done'),
]