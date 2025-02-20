import random
from datetime import date
import requests
from django.conf import settings
from .models import Quote, Book

# Fallback quotes in case API fails
FALLBACK_QUOTES = [
    {
        "text": "A reader lives a thousand lives before he dies. The man who never reads lives only one.",
        "author": "George R.R. Martin",
        "book_title": "A Dance with Dragons"
    },
    {
        "text": "Books are a uniquely portable magic.",
        "author": "Stephen King",
        "book_title": "On Writing: A Memoir of the Craft"
    },
    {
        "text": "There is no friend as loyal as a book.",
        "author": "Ernest Hemingway",
        "book_title": None
    },
    {
        "text": "That's the thing about books. They let you travel without moving your feet.",
        "author": "Jhumpa Lahiri",
        "book_title": "The Namesake"
    },
    {
        "text": "Sleep is good, he said, and books are better.",
        "author": "George R.R. Martin",
        "book_title": "A Dance with Dragons"
    },
    {
        "text": "We read to know we're not alone.",
        "author": "William Nicholson",
        "book_title": "Shadowlands"
    },
    {
        "text": "It is what you read when you don't have to that determines what you will be when you can't help it.",
        "author": "Oscar Wilde",
        "book_title": None
    },
    {
        "text": "The more that you read, the more things you will know. The more that you learn, the more places you'll go.",
        "author": "Dr. Seuss",
        "book_title": "I Can Read With My Eyes Shut!"
    },
    {
        "text": "Until I feared I would lose it, I never loved to read. One does not love breathing.",
        "author": "Harper Lee",
        "book_title": "To Kill a Mockingbird"
    },
    {
        "text": "Reading is the basic tool in the living of a good life.",
        "author": "Mortimer J. Adler",
        "book_title": "How to Read a Book"
    },
    {
        "text": "The person who deserves most pity is a lonesome one on a rainy day who doesn't know how to read.",
        "author": "Benjamin Franklin",
        "book_title": None
    },
    {
        "text": "Reading is an exercise in empathy; an exercise in walking in someone else's shoes for a while.",
        "author": "Malorie Blackman",
        "book_title": None
    },
    {
        "text": "A book is a dream that you hold in your hand.",
        "author": "Neil Gaiman",
        "book_title": None
    },
    {
        "text": "Reading gives us someplace to go when we have to stay where we are.",
        "author": "Mason Cooley",
        "book_title": None
    },
    {
        "text": "Books are a form of political action. Books are knowledge. Books are reflection. Books change your mind.",
        "author": "Toni Morrison",
        "book_title": None
    }
]

def get_or_create_daily_quote():
    """Get today's quote or create a new one"""
    today = date.today()
    
    # Try to get today's quote
    today_quote = Quote.objects.filter(date_shown=today).first()
    if today_quote:
        return today_quote
    
    # If no quote exists for today, try to fetch a new one
    try:
        # Get a random author from user's books
        authors = Book.objects.values_list('author', flat=True).distinct()
        if not authors:
            raise Exception("No authors found")
        
        author = random.choice(list(authors))
        print(f"Searching for quotes by {author}")
        
        # Search for quotes by this author
        api_url = 'https://www.googleapis.com/books/v1/volumes'
        # Try different search queries to find quotes
        search_queries = [
            f'inauthor:"{author}" "said" OR "wrote" OR "quote"',
            f'inauthor:"{author}" "famous quotes"',
            f'"{author}" "best quotes"',
            f'"{author}" "memorable quotes"'
        ]
        
        all_quotes = []
        
        for query in search_queries:
            print(f"Trying search query: {query}")
            params = {
                'q': query,
                'key': settings.GOOGLE_BOOKS_API_KEY,
                'maxResults': '40'
            }
            
            response = requests.get(api_url, params=params)
            if response.status_code != 200:
                print(f"API request failed for query: {query}")
                continue
            
            data = response.json()
            if 'items' not in data:
                print(f"No items found for query: {query}")
                continue
            
            print(f"Found {len(data['items'])} items for query: {query}")
            
            # Try to find quotes in the description or snippet
            for item in data['items']:
                volume_info = item.get('volumeInfo', {})
                # Look in multiple fields for quotes
                search_fields = [
                    volume_info.get('description', ''),
                    item.get('searchInfo', {}).get('textSnippet', ''),
                    volume_info.get('subtitle', ''),
                    volume_info.get('snippet', '')
                ]
                
                # Look for quotes with proper quotation marks in each field
                quote_patterns = [
                    ('"', '"'),
                    ('"', '"'),
                    ('"', '"'),
                    ('\'', '\''),
                    ('\u201C', '\u201D'),  # Unicode quotes
                ]
                
                for field in search_fields:
                    if not field:  # Skip empty fields
                        continue
                        
                    for start_quote, end_quote in quote_patterns:
                        start = 0
                        while True:
                            start = field.find(start_quote, start)
                            if start == -1:
                                break
                            end = field.find(end_quote, start + 1)
                            if end == -1:
                                break
                            quote_text = field[start + 1:end].strip()
                            # Ensure it's a proper quote with reasonable length and structure
                            if (20 < len(quote_text) < 200 and  # Not too short or too long
                                any(quote_text.endswith(p) for p in '.!?') and  # Proper ending
                                not quote_text.startswith('http') and  # Not a URL
                                not any(skip in quote_text.lower() for skip in [
                                    'chapter', 'page', 'volume', 'book', 
                                    'novel', 'story', 'plot', 'summary',
                                    'autobiography', 'biography', 'review'
                                ])):  # Skip descriptions and summaries
                                print(f"Found potential quote: {quote_text[:50]}...")
                                all_quotes.append((quote_text, volume_info.get('title')))
                            start = end + 1
        
        if all_quotes:
            print(f"Found {len(all_quotes)} total quotes")
            # Choose the longest quote
            quote_text, book_title = max(all_quotes, key=lambda x: len(x[0]))
            print(f"Selected quote: {quote_text[:50]}...")
            quote = Quote.objects.create(
                text=quote_text,
                author=author,
                book_title=book_title,
                date_shown=today
            )
            return quote
        
        raise Exception("No suitable quotes found in API response")
        
    except Exception as e:
        print(f"Error fetching quote: {str(e)}")
        # Use a fallback quote
        fallback = random.choice(FALLBACK_QUOTES)
        quote = Quote.objects.create(
            text=fallback['text'],
            author=fallback['author'],
            book_title=fallback['book_title'],
            date_shown=today
        )
        return quote
