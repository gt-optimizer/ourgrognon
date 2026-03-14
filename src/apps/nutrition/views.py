from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.response import TemplateResponse
from thefuzz import process
from .models import CiqualFood
from .services import calculate_nutrition
from apps.recipes.models import Recipe, RecipeIngredient


@login_required
def ciqual_search(request):
    """HTMX — retourne les aliments CIQUAL correspondant à la requête."""
    q = request.GET.get('q', '').strip()
    ingredient_id = request.GET.get('ingredient_id')


    if not q:
        for val in request.GET.getlist('q'):
            if val.strip():
                q = val.strip()
                break

    if len(q) < 2:
        return TemplateResponse(request, 'nutrition/partials/ciqual_results.html', {
            'results': [],
            'ingredient_id': ingredient_id,
        })

    # Recherche floue sur tous les noms CIQUAL
    all_foods = CiqualFood.objects.values_list('id', 'name')
    names = {food[1]: food[0] for food in all_foods}

    matches = process.extract(q, names.keys(), limit=None)
    # Filtrer score > 40 et trier par score décroissant
    matches = [(name, score) for name, score in matches if score > 40]
    matches.sort(key=lambda x: x[1], reverse=True)

    food_ids = [names[name] for name, score in matches]
    foods = CiqualFood.objects.filter(id__in=food_ids)
    # Conserver l'ordre du score
    foods_by_id = {f.id: f for f in foods}
    results = [foods_by_id[fid] for fid in food_ids if fid in foods_by_id]
    print("q=", q, "matches=", len(matches), "results=", len(results))

    return TemplateResponse(request, 'nutrition/partials/ciqual_results.html', {
        'results': results,
        'ingredient_id': ingredient_id,
    })


@login_required
@require_POST
def ciqual_associate(request):
    """Sauvegarde l'association RecipeIngredient → CiqualFood."""
    ingredient_id = request.POST.get('ingredient_id')
    ciqual_id = request.POST.get('ciqual_id')

    ingredient = get_object_or_404(RecipeIngredient, pk=ingredient_id)
    # Vérifier que l'auteur de la recette est bien le user connecté
    if ingredient.recipe.author != request.user:
        return JsonResponse({'error': 'Permission refusée'}, status=403)

    if ciqual_id:
        ciqual = get_object_or_404(CiqualFood, pk=ciqual_id)
        ingredient.ciqual_food = ciqual
    else:
        ingredient.ciqual_food = None

    ingredient.save()
    return JsonResponse({
        'success': True,
        'ingredient_name': ingredient.name,
        'ciqual_name': ingredient.ciqual_food.name if ingredient.ciqual_food else None,
    })


@login_required
def nutrition_modal(request, recipe_pk):
    """HTMX — contenu du modal d'association CIQUAL."""
    recipe = get_object_or_404(Recipe, pk=recipe_pk, author=request.user)
    ingredients = recipe.ingredients.select_related('ciqual_food').all()
    return TemplateResponse(request, 'nutrition/partials/modal_content.html', {
        'recipe': recipe,
        'ingredients': ingredients,
    })


@login_required
def nutrition_summary(request, recipe_pk):
    """HTMX — tableau nutritionnel affiché sur la fiche recette."""
    recipe = get_object_or_404(Recipe, pk=recipe_pk)
    data = calculate_nutrition(recipe)
    print("DATA:", data)
    return TemplateResponse(request, 'nutrition/partials/summary.html', {
        'recipe': recipe,
        'data': data,
    })