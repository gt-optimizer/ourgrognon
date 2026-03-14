from django import forms
from django.forms import inlineformset_factory
from taggit.forms import TagWidget
from .models import Recipe, RecipeIngredient, RecipeStep


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'title', 'description', 'category',
            'servings', 'prep_time', 'cook_time',
            'photo', 'tags',
        ]
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category':    forms.Select(attrs={'class': 'form-control'}),
            'servings':    forms.NumberInput(attrs={'class': 'form-control'}),
            'prep_time':   forms.NumberInput(attrs={'class': 'form-control'}),
            'cook_time':   forms.NumberInput(attrs={'class': 'form-control'}),
            'photo':       forms.FileInput(attrs={'class': 'form-control'}),
            'tags': TagWidget(attrs={
                'class': 'form-control',
                'placeholder': 'végétarien, rapide…'
            }),
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['quantity', 'unit', 'name']
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Qté'}),
            'unit':     forms.Select(attrs={'class': 'form-control'}),
            'name':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrédient…'}),
        }

    def has_changed(self):
        delete_key = self.add_prefix('DELETE')
        if self.data.get(delete_key) == 'on':
            return True  # ligne à supprimer — laisser Django gérer
        if not self.data.get(self.add_prefix('name')):
            return False
        return super().has_changed()


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['description', 'photo']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'photo':       forms.FileInput(attrs={'class': 'form-control'}),
        }

    def has_changed(self):
        delete_key = self.add_prefix('DELETE')
        if self.data.get(delete_key) == 'on':
            return True
        if not self.data.get(self.add_prefix('description')):
            return False
        return super().has_changed()


# FormSets liés à Recipe
IngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    extra=0,
    can_delete=True,
    min_num=0,          # ← 0 au lieu de 1
    validate_min=False, # ← désactiver
)

StepFormSet = inlineformset_factory(
    Recipe,
    RecipeStep,
    form=RecipeStepForm,
    extra=0,
    can_delete=True,
    min_num=0,          # ← 0 au lieu de 1
    validate_min=False, # ← désactiver
)