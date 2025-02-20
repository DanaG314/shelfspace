from django.core.management.base import BaseCommand
from main_app.utils import get_or_create_daily_quote

"""
This command fetches and stores a new quote for the day.

To run this command automatically every day, set up a cron job:

1. Open your crontab:
   crontab -e

2. Add this line to run it every day at midnight:
   0 0 * * * cd /path/to/your/project && /usr/local/bin/python3 manage.py fetch_daily_quote

Or if using a virtual environment:
   0 0 * * * cd /path/to/your/project && /path/to/venv/bin/python manage.py fetch_daily_quote

The command will:
1. Try to fetch a quote from Google Books API using a random author from your books
2. If that fails, use one of the fallback quotes
3. Store the quote in the database with today's date
"""

class Command(BaseCommand):
    help = 'Fetches and stores a new quote for today'

    def handle(self, *args, **options):
        try:
            quote = get_or_create_daily_quote()
            self.stdout.write(self.style.SUCCESS(f'Successfully created quote: "{quote.text}" - {quote.author}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating quote: {str(e)}'))
