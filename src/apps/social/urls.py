from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('recettes/<int:recipe_pk>/commenter/', views.comment_create, name='comment_create'),
]