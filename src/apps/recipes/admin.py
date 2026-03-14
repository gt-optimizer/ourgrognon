from django.contrib import admin
from .models import Recipe, RecipeIngredient, RecipeStep


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 3
    fields = ['quantity', 'unit', 'name', 'ciqual_food']


class RecipeStepInline(admin.StackedInline):
    model = RecipeStep
    extra = 1
    fields = ['order', 'description', 'photo']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'servings', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['title', 'description']
    inlines = [RecipeIngredientInline, RecipeStepInline]
    readonly_fields = ['created_at', 'updated_at']