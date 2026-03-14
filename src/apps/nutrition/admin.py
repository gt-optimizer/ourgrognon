from django.contrib import admin
from .models import Allergen, CiqualFood


@admin.register(Allergen)
class AllergenAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(CiqualFood)
class CiqualFoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'energy_kj', 'proteins', 'carbs', 'fat', 'fiber', 'get_allergens']
    search_fields = ['name', 'allergens__name']
    filter_horizontal = ['allergens']

    @admin.display(description='Allergènes')
    def get_allergens(self, obj):
        return ', '.join(a.name for a in obj.allergens.all())