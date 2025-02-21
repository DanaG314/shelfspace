from django.core.management.base import BaseCommand
from main_app.models import Book
from django.conf import settings
import requests
import time

class Command(BaseCommand):
    help = 'Fetch missing descriptions for books from Google Books API'

    def handle(self, *args, **options):
        books = Book.objects.filter(summary__isnull=True)
        total = books.count()
        self.stdout.write(f'Found {total} books without descriptions')

        for i, book in enumerate(books, 1):
            self.stdout.write(f'Processing book {i}/{total}: {book.title}')
            
            query = f'intitle:{book.title} inauthor:{book.author}'
            api_url = 'https://www.googleapis.com/books/v1/volumes'
            
            try:
                params = {
                    'q': query,
                    'key': settings.GOOGLE_BOOKS_API_KEY
                }
                response = requests.get(api_url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'items' in data:
                        for item in data['items']:
                            volume_info = item.get('volumeInfo', {})
                            if volume_info.get('title') == book.title:
                                description = volume_info.get('description', '')
                                if description:
                                    description = description.replace('<p>', '').replace('</p>', '\n\n')
                                    description = description.replace('<br>', '\n').replace('<br/>', '\n')
                                    description = description.replace('&quot;', '"').replace('&amp;', '&')
                                    book.summary = description
                                    book.save()
                                    self.stdout.write(self.style.SUCCESS(f'Updated description for {book.title}'))
                                    break
                
                time.sleep(1)
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing {book.title}: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS('Finished updating book descriptions'))
