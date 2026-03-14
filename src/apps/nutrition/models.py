from django.db import models


class Allergen(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Allergène")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Allergène"
        verbose_name_plural = "Allergènes"
        ordering = ['name']

    def __str__(self):
        return self.name

class CiqualFood(models.Model):
    code = models.CharField(max_length=20, unique=True, verbose_name="Code CIQUAL")
    name = models.CharField(max_length=200, verbose_name="Aliment")

    # Valeurs pour 100g
    energy_kj = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Énergie (kJ/100g)")
    proteins = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Protéines (g/100g)")
    carbs = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Glucides (g/100g)")
    sugars = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Sucres (g/100g)")
    fat = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Lipides (g/100g)")
    saturated_fat = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="AG saturés (g/100g)")
    fiber = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Fibres (g/100g)")
    cholesterol = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Cholestérol (mg/100g)")
    salt = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Sel (g/100g)")
    allergens = models.ManyToManyField(
        Allergen,
        blank=True,
        related_name='foods',
        verbose_name="Allergènes"
    )

    class Meta:
        verbose_name = "Aliment CIQUAL"
        verbose_name_plural = "Aliments CIQUAL"
        ordering = ['name']

    def __str__(self):
        return self.name