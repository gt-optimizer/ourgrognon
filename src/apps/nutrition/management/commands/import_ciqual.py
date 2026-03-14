import openpyxl
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from apps.nutrition.models import CiqualFood


def parse_decimal(value):
    """
    Convertit une valeur CIQUAL en Decimal.
    Gère : None, '-', '< 0,2', '49,9' (virgule française)
    """
    if value is None:
        return None
    value = str(value).strip()
    if value in ('-', '', 'NA'):
        return None
    # Valeurs du type "< 0,2" — on prend la valeur numérique
    if value.startswith('<'):
        value = value.replace('<', '').strip()
    # Virgule française → point
    value = value.replace(',', '.')
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


class Command(BaseCommand):
    help = "Importe la base CIQUAL depuis un fichier Excel"

    def add_arguments(self, parser):
        parser.add_argument(
            'filepath',
            type=str,
            help='Chemin vers le fichier CIQUAL .xlsx'
        )

    def handle(self, *args, **options):
        filepath = options['filepath']
        self.stdout.write(f"Ouverture du fichier : {filepath}")

        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active

        created = 0
        updated = 0
        errors = 0

        # Ligne 1 = en-têtes, données à partir de la ligne 2
        for row in ws.iter_rows(min_row=2, values_only=True):
            code = str(row[6]).strip() if row[6] else None
            name = str(row[7]).strip() if row[7] else None

            if not code or not name:
                errors += 1
                continue

            obj, created_flag = CiqualFood.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'energy_kj':      parse_decimal(row[11]),
                    'proteins':       parse_decimal(row[15]),
                    'carbs':          parse_decimal(row[16]),
                    'fat':            parse_decimal(row[17]),
                    'sugars':         parse_decimal(row[18]),
                    'fiber':          parse_decimal(row[26]),
                    'saturated_fat':  parse_decimal(row[31]),
                    'cholesterol':    parse_decimal(row[48]),
                    'salt':           parse_decimal(row[49]),
                }
            )

            if created_flag:
                created += 1
            else:
                updated += 1

        wb.close()

        self.stdout.write(self.style.SUCCESS(
            f"\nImport terminé : {created} créés, {updated} mis à jour, {errors} erreurs"
        ))