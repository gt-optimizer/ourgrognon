from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.recipes.models import Recipe
from .models import Comment


@login_required
def comment_create(request, recipe_pk):
    recipe = get_object_or_404(Recipe, pk=recipe_pk)
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            Comment.objects.create(
                recipe=recipe,
                author=request.user,
                text=text
            )
            messages.success(request, "Commentaire publié.")
        else:
            messages.warning(request, "Le commentaire ne peut pas être vide.")
    return redirect('recipes:detail', pk=recipe_pk)