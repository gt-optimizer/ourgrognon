from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .forms import RecipeForm, IngredientFormSet, StepFormSet
from .models import Recipe


@login_required
def recipe_list(request):
    recipes = Recipe.objects.select_related('author').prefetch_related('tags')
    category = request.GET.get('category', '')
    q = request.GET.get('q', '')
    if category:
        recipes = recipes.filter(category=category)
    if q:
        recipes = recipes.filter(
            Q(title__icontains=q) |
            Q(ingredients__name__icontains=q)
        ).distinct()
    return render(request, 'recipes/list.html', {
        'recipes': recipes,
        'category': category,
        'q': q,
        'categories': Recipe.CATEGORY_CHOICES,
    })


@login_required
def recipe_detail(request, pk):
    recipe = get_object_or_404(
        Recipe.objects.select_related('author')
                      .prefetch_related('ingredients', 'steps', 'tags', 'comments__author'),
        pk=pk
    )
    return render(request, 'recipes/detail.html', {'recipe': recipe})

@login_required
def recipe_create(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        ingredient_formset = IngredientFormSet(request.POST)
        step_formset = StepFormSet(request.POST, request.FILES)

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            # 1. Sauvegarder la recette
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()  # tags

            # 2. Sauvegarder les ingrédients
            ingredient_formset.instance = recipe
            ingredient_formset.save()

            # 3. Sauvegarder les étapes avec numérotation auto
            step_formset.instance = recipe
            steps = step_formset.save(commit=False)
            for i, step in enumerate(steps, start=1):
                step.order = i
                step.recipe = recipe
                step.save()
            step_formset.save_m2m()

            messages.success(request, "Recette créée avec succès !")
            return redirect('recipes:detail', pk=recipe.pk)
        else:
            print("Form errors:", form.errors)
            print("Ingredient errors:", ingredient_formset.errors)
            print("Step errors:", step_formset.errors)
    else:
        form = RecipeForm()
        ingredient_formset = IngredientFormSet()
        step_formset = StepFormSet()

    return render(request, 'recipes/form.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'title': 'Nouvelle recette',
    })

@login_required
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        ingredient_formset = IngredientFormSet(request.POST, instance=recipe)
        step_formset = StepFormSet(request.POST, request.FILES, instance=recipe)

        if form.is_valid() and ingredient_formset.is_valid() and step_formset.is_valid():
            recipe = form.save(commit=False)
            recipe.save()
            form.save_m2m()

            ingredient_formset.save()
            for ingredient in ingredient_formset.deleted_objects:
                if ingredient.pk:
                    ingredient.delete()

            step_formset.instance = recipe
            steps = step_formset.save(commit=False)

            for step in step_formset.deleted_objects:
                step.delete()

            for i, step in enumerate(steps, start=1):
                step.order = i
                step.recipe = recipe
                step.save()
            step_formset.save_m2m()

            messages.success(request, "Recette modifiée avec succès !")
            return redirect('recipes:detail', pk=recipe.pk)
        else:
            print("Form errors:", form.errors)
            print("Ingredient errors:", ingredient_formset.errors)
            print("Step errors:", step_formset.errors)
            print("TOTAL FORMS:", request.POST.get('ingredients-TOTAL_FORMS'))
            print("POST data:", {k: v for k, v in request.POST.items() if 'ingredient' in k})
    else:
        form = RecipeForm(instance=recipe)
        ingredient_formset = IngredientFormSet(instance=recipe)
        step_formset = StepFormSet(instance=recipe)

    return render(request, 'recipes/form.html', {
        'form': form,
        'ingredient_formset': ingredient_formset,
        'step_formset': step_formset,
        'title': f'Modifier — {recipe.title}',
        'recipe': recipe,  # ← ajouter
    })

@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, f"« {recipe.title} » a été supprimée.")
        return redirect('recipes:list')
    return render(request, 'recipes/confirm_delete.html', {'recipe': recipe})