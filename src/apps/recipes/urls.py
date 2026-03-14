from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.recipe_list, name='list'),
    path('<int:pk>/', views.recipe_detail, name='detail'),
    path('nouvelle/', views.recipe_create, name='create'),
    path('<int:pk>/modifier/', views.recipe_update, name='update'),
    path('<int:pk>/supprimer/', views.recipe_delete, name='delete'),
]