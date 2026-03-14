from django.db import models
from django.conf import settings
from taggit.managers import TaggableManager
import io
from PIL import Image, ExifTags
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile


def optimiser_image(image_field, width=800, height=600):
    """Redimensionne et corrige l'orientation EXIF d'une image."""
    if not image_field:
        return None
    img = Image.open(image_field)
    try:
        exif_data = img._getexif()
        if exif_data:
            exif = {ExifTags.TAGS.get(k, k): v for k, v in exif_data.items()}
            orientation = exif.get('Orientation')
            if orientation == 3:   img = img.rotate(180, expand=True)
            elif orientation == 6: img = img.rotate(270, expand=True)
            elif orientation == 8: img = img.rotate(90, expand=True)
    except Exception:
        pass
    cible = (width, height) if img.width > img.height else (height, width)
    img.thumbnail(cible, Image.Resampling.LANCZOS)
    output = io.BytesIO()
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.save(output, format='JPEG', quality=85)
    output.seek(0)
    return ContentFile(output.read(), name=image_field.name)


class Recipe(models.Model):

    CATEGORY_CHOICES = [
        ('starter', 'Entrée'),
        ('main', 'Plat'),
        ('dessert', 'Dessert'),
        ('appetizer', 'Apéritif'),
        ('other', 'Autre'),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name="Auteur"
    )
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Catégorie"
    )
    servings = models.PositiveSmallIntegerField(verbose_name="Nombre de personnes")
    prep_time = models.PositiveSmallIntegerField(verbose_name="Temps de préparation (min)")
    cook_time = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Temps de cuisson (min)"
    )
    photo = models.ImageField(
        upload_to='recipes/',
        blank=True,
        null=True,
        verbose_name="Photo principale"
    )
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Recette"
        verbose_name_plural = "Recettes"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.photo and isinstance(self.photo.file, (InMemoryUploadedFile, TemporaryUploadedFile)):
            self.photo = optimiser_image(self.photo)
        super().save(*args, **kwargs)


class RecipeIngredient(models.Model):

    UNIT_CHOICES = [
        ('g', 'Grammes'),
        ('kg', 'Kilogrammes'),
        ('ml', 'Millilitres'),
        ('cl', 'Centilitres'),
        ('l', 'Litres'),
        ('tsp', 'Cuillère à café'),
        ('tbsp', 'Cuillère à soupe'),
        ('piece', 'Pièce(s)'),
        ('bunch', 'Bouquet'),
        ('pm', 'Pour mémoire'),
    ]

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredients',
        verbose_name="Recette"
    )
    name = models.CharField(max_length=150, verbose_name="Ingrédient")
    quantity = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Quantité"
    )
    unit = models.CharField(
        max_length=10,
        choices=UNIT_CHOICES,
        blank=True,
        verbose_name="Unité"
    )
    ciqual_food = models.ForeignKey(
        'nutrition.CiqualFood',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recipe_ingredients',
        verbose_name="Aliment CIQUAL"
    )

    density_g_per_ml = models.DecimalField(
        max_digits=5, decimal_places=3,
        null=True, blank=True,
        verbose_name="Densité (g/ml)",
        help_text="Laisser vide = eau (1g/ml). Ex: huile=0.92, miel=1.4"
    )

    class Meta:
        verbose_name = "Ingrédient"
        verbose_name_plural = "Ingrédients"

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.name}"


class RecipeStep(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name="Recette"
    )
    order = models.PositiveSmallIntegerField(verbose_name="Ordre")
    description = models.TextField(verbose_name="Description")
    photo = models.ImageField(
        upload_to='steps/',
        blank=True,
        null=True,
        verbose_name="Photo de l'étape"
    )

    class Meta:
        verbose_name = "Étape"
        verbose_name_plural = "Étapes"
        ordering = ['order']

    def save(self, *args, **kwargs):
        if self.photo and isinstance(self.photo.file, (InMemoryUploadedFile, TemporaryUploadedFile)):
            self.photo = optimiser_image(self.photo)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Étape {self.order} — {self.recipe.title}"