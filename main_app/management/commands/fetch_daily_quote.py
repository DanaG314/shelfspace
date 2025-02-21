from django.core.management.base import BaseCommand
from main_app.utils import get_or_create_daily_quote

class Command(BaseCommand):
    help = 'Fetches and stores a new quote for today'

    def handle(self, *args, **options):
        try:
            quote = get_or_create_daily_quote()
            self.stdout.write(self.style.SUCCESS(f'Successfully created quote: "{quote.text}" - {quote.author}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating quote: {str(e)}'))
