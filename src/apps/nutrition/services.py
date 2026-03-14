from decimal import Decimal
from .unit_converter import convert_units, INGREDIENT_DENSITIES


# Correspondance UNIT_CHOICES → unité unit_converter
UNIT_MAP = {
    'g':    'g',
    'kg':   'kg',
    'ml':   'ml',
    'cl':   'cl',
    'l':    'litre',
    'tsp':  'cc',
    'tbsp': 'cs',
}

NON_CONVERTIBLE = {'piece', 'bunch', 'pm', ''}


def get_density(ingredient) -> Decimal:
    """Densité g/ml : champ manuel > table unit_converter > défaut 1.0"""
    if ingredient.density_g_per_ml:
        return Decimal(str(ingredient.density_g_per_ml))
    name_lower = ingredient.name.lower()
    for keyword, density in INGREDIENT_DENSITIES.items():
        if keyword == '_default':
            continue
        if keyword in name_lower:
            return density
    return Decimal('1.0')


def ingredient_to_grams(ingredient) -> tuple[Decimal | None, str | None]:
    """
    Convertit la quantité d'un RecipeIngredient en grammes.
    Retourne (grammes, None) ou (None, message_erreur)
    """
    unit = ingredient.unit
    quantity = ingredient.quantity

    if not quantity:
        return None, "Quantité manquante"

    if unit in NON_CONVERTIBLE:
        return None, f"Unité « {unit} » non convertible"

    from_unit = UNIT_MAP.get(unit)
    if not from_unit:
        return None, f"Unité « {unit} » inconnue"

    density = get_density(ingredient)
    grams = convert_units(quantity, from_unit, 'g', density=density)

    if grams is None:
        return None, f"Conversion impossible ({unit} → g)"

    return grams, None


def calculate_nutrition(recipe):
    """
    Calcule les valeurs nutritionnelles d'une recette.

    Retourne un dict :
    {
        'per_100g': { 'energy_kj': x, 'proteins': x, ... },
        'per_serving': { ... },
        'total': { ... },
        'warnings': ['ingrédient X non convertible', ...],
        'coverage_percent': 85,  # % des ingrédients avec données CIQUAL
    }
    """
    NUTRIENTS = ['energy_kj', 'proteins', 'carbs', 'sugars', 'fat', 'saturated_fat', 'fiber', 'salt', 'cholesterol']

    totals = {n: Decimal('0') for n in NUTRIENTS}
    total_grams = Decimal('0')
    warnings = []
    ingredients_with_ciqual = 0
    ingredients_total = 0

    for ing in recipe.ingredients.select_related('ciqual_food').all():
        ingredients_total += 1

        if not ing.ciqual_food:
            warnings.append(f"« {ing.name} » : aucun aliment CIQUAL associé")
            continue

        grams, error = ingredient_to_grams(ing)
        if error:
            warnings.append(f"« {ing.name} » : {error}")
            continue

        ingredients_with_ciqual += 1
        total_grams += grams
        factor = grams / Decimal('100')

        ciqual = ing.ciqual_food
        for nutrient in NUTRIENTS:
            value = getattr(ciqual, nutrient)
            if value is not None:
                totals[nutrient] += Decimal(str(value)) * factor

    # Calcul par 100g et par portion
    def per_100g(totals, total_grams):
        if not total_grams:
            return {n: None for n in NUTRIENTS}
        factor = Decimal('100') / total_grams
        return {n: round(totals[n] * factor, 2) for n in NUTRIENTS}

    def per_serving(totals, servings):
        if not servings:
            return {n: None for n in NUTRIENTS}
        factor = Decimal('1') / Decimal(str(servings))
        return {n: round(totals[n] * factor, 2) for n in NUTRIENTS}

    coverage = (
        round(ingredients_with_ciqual / ingredients_total * 100)
        if ingredients_total else 0
    )

    def enrich(bucket):
        if bucket.get('energy_kj'):
            bucket['energy_kcal'] = round(bucket['energy_kj'] / Decimal('4.184'), 1)
        else:
            bucket['energy_kcal'] = None
        return bucket

    p100 = enrich(per_100g(totals, total_grams))
    ps = enrich(per_serving(totals, recipe.servings))
    tot = enrich({n: round(totals[n], 2) for n in NUTRIENTS})

    return {
        'total': tot,
        'per_100g': p100,
        'per_serving': ps,
        'warnings': warnings,
        'coverage_percent': coverage,
        'total_grams': round(total_grams, 1),
    }