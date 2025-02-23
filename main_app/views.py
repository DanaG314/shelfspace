import requests
from django.shortcuts import render, redirect
from main_app.models import Book
from django.views.generic import TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import DeleteView
from django import forms
from django.utils import timezone
from django.db.models import Q


class Home(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_books'] = Book.objects.all().order_by('-created_at')[:4]
        return context


class BookDelete(DeleteView):
    model = Book
    success_url = '/bookshelf'


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('bookshelf')
        else:
            error_message = 'Invalid sign up - try again'
    else:
        form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

def book_detail(request, book_id):
    book = Book.objects.get(id=book_id)
    return render(request, 'books/detail.html', {
        'book': book,
    })

def book_search(request):
    search_results = []
    error = None
    if 'q' in request.GET:
        query = request.GET.get('q', '')
        api_url = 'https://www.googleapis.com/books/v1/volumes'
        
        try:
            params = {
                'q': query,
                'key': settings.GOOGLE_BOOKS_API_KEY,
                'maxResults': '40'
            }
            
            response = requests.get(api_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'items' in data:
                    for item in data['items']:
                        volume_info = item.get('volumeInfo', {})
                        image_links = volume_info.get('imageLinks', {})
                        
                        cover_url = image_links.get('large', '') or image_links.get('medium', '') or image_links.get('small', '') or image_links.get('thumbnail', '')
                        if cover_url:
                            cover_url = cover_url.replace('http://', 'https://').replace('&zoom=1', '&zoom=0')
                        
                        book_data = {
                            'id': item.get('id'),
                            'title': volume_info.get('title', ''),
                            'author': volume_info.get('authors', ['Unknown Author'])[0],
                            'cover_url': cover_url,
                            'isbn_13': next((id.get('identifier') for id in volume_info.get('industryIdentifiers', []) 
                                          if id.get('type') == 'ISBN_13'), None),
                            'page_count': volume_info.get('pageCount', 0),
                            'summary': volume_info.get('description', '')
                        }
                        search_results.append(book_data)
                else:
                    error = "No books found matching your search."
            else:
                error = f"API Error: {response.status_code}"
                print(f"Error response: {response.text}")
                
        except requests.RequestException as e:
            error = f"Error fetching books: {str(e)}"
            print(f"Request error: {str(e)}")
        except Exception as e:
            error = f"Unexpected error: {str(e)}"
            print(f"Unexpected error: {str(e)}")
    
    return render(request, 'books/search.html', {
        'results': search_results,
        'error': error,
        'query': request.GET.get('q', '')
    })


@login_required
def update_notes(request, book_id):
    if request.method == 'POST':
        book = Book.objects.get(id=book_id)
        book.notes = request.POST.get('notes', '')
        book.save()
        messages.success(request, 'Notes updated successfully!')
    return redirect('bookshelf-detail', book_id=book_id)

@login_required
def update_progress(request, book_id):
    if request.method == 'POST':
        book = Book.objects.get(id=book_id)
        new_page = int(request.POST.get('current_page', 0))
        
        new_page = max(0, min(new_page, book.total_pages))
        book.current_page = new_page
        
        if new_page == book.total_pages:
            book.status = 'completed'
        elif new_page > 0 and book.status == 'plan_to_read':
            book.status = 'reading'
            if not book.started_at:
                book.started_at = timezone.now()
        
        book.save()
        messages.success(request, 'Reading progress updated!')
    return redirect('bookshelf-detail', book_id=book_id)

@login_required
def book_add(request):
    if request.method == 'POST':
        google_books_id = request.POST.get('google_books_id')
        
        api_url = f'https://www.googleapis.com/books/v1/volumes/{google_books_id}'
        params = {
            'key': settings.GOOGLE_BOOKS_API_KEY
        }
        
        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                book_data = response.json()
                volume_info = book_data.get('volumeInfo', {})
                
                raw_title = volume_info.get('title', '')
                raw_authors = volume_info.get('authors', ['Unknown Author'])
                raw_author_string = ', '.join(raw_authors)
                
                title = raw_title[:497] + '...' if len(raw_title) > 500 else raw_title
                author_string = raw_author_string[:497] + '...' if len(raw_author_string) > 500 else raw_author_string
                
                image_links = volume_info.get('imageLinks', {})
                cover_url = image_links.get('large', '') or image_links.get('medium', '') or image_links.get('small', '') or image_links.get('thumbnail', '')
                if cover_url:
                    cover_url = cover_url.replace('http://', 'https://').replace('&zoom=1', '&zoom=0')
                    cover_url = cover_url[:200]
                
                try:
                    isbn13 = None
                    industry_identifiers = volume_info.get('industryIdentifiers', [])
                    for identifier in industry_identifiers:
                        if identifier.get('type') == 'ISBN_13':
                            isbn13 = identifier.get('identifier', '')[:13]
                            break

                    description = volume_info.get('description', '')
                    if description:
                        description = description.replace('<p>', '').replace('</p>', '\n\n')
                        description = description.replace('<br>', '\n').replace('<br/>', '\n')
                        description = description.replace('&quot;', '"').replace('&amp;', '&')
                    
                    book = Book.objects.create(
                        user=request.user,
                        title=title[:500],
                        author=author_string[:500],
                        cover_url=cover_url,
                        isbn13=isbn13,
                        summary=description,
                        total_pages=volume_info.get('pageCount', 0),
                        status='plan_to_read'
                    )
                except Exception as field_error:
                    raise Exception(f"Error with book fields: {str(field_error)}")
                
                messages.success(request, f'"{book.title}" has been added to your bookshelf!')
                return redirect('bookshelf')
            else:
                messages.error(request, 'Could not fetch book details. Please try again.')
        except Exception as e:
            messages.error(request, f'Error adding book: {str(e)}')
    
    return redirect('book-search')


@login_required
def update_rating(request, book_id):
    if request.method == 'POST':
        book = Book.objects.get(id=book_id)
        rating = request.POST.get('rating')
        if rating:
            book.rating = int(rating)
        else:
            book.rating = None
        book.save()
        messages.success(request, 'Rating updated successfully!')
    return redirect('bookshelf-detail', book_id=book_id)

@login_required
def update_status(request, book_id):
    if request.method == 'POST':
        book = Book.objects.get(id=book_id)
        new_status = request.POST.get('status')
        if new_status in dict(Book.STATUS_CHOICES):
            book.status = new_status
            if new_status == 'reading' and not book.started_at:
                book.started_at = timezone.now()
            elif new_status == 'completed':
                book.current_page = book.total_pages
            book.save()
            messages.success(request, 'Status updated successfully!')
    return redirect('bookshelf-detail', book_id=book_id)

@login_required
def bookshelf(request):
    books = Book.objects.filter(user=request.user)
    
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query)
        )
    
    status = request.GET.get('status')
    if status and status != 'all':
        books = books.filter(status=status)
    
    sort_by = request.GET.get('sort', 'title')
    sort_order = request.GET.get('order', 'asc')
    
    sort_mapping = {
        'title': 'title',
        'author': 'author',
        'rating': 'rating',
        'updated_at': 'updated_at'
    }
    
    sort_field = sort_mapping.get(sort_by, 'title')
    if sort_order == 'desc':
        sort_field = f'-{sort_field}'
    books = books.order_by(sort_field)
    
    from .utils import get_or_create_daily_quote
    quote = get_or_create_daily_quote()
    
    return render(request, 'books/bookshelf.html', {
        'books': books,
        'search_query': search_query,
        'quote': quote,
        'current_sort': sort_by,
        'current_order': sort_order,
        'current_status': status or 'all'
    })
