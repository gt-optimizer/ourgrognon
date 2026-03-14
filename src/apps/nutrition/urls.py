from django.urls import path
from . import views

app_name = 'nutrition'

urlpatterns = [
    path('ciqual/search/', views.ciqual_search, name='search'),
    path('ciqual/associate/', views.ciqual_associate, name='associate'),
    path('recettes/<int:recipe_pk>/nutrition/modal/', views.nutrition_modal, name='modal'),
    path('recettes/<int:recipe_pk>/nutrition/', views.nutrition_summary, name='summary'),
]