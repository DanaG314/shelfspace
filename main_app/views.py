import requests
from django.shortcuts import render, redirect
from main_app.models import Book
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login
from django.conf import settings
from django.core.cache import cache
from time import sleep
from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.edit import DeleteView
from django import forms
from django.utils import timezone
from django.db.models import Q


class Home(TemplateView):
    template_name = 'home.html'
    success_url = '/bookshelf/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get 4 most recently added books (no user filter)
        context['recent_books'] = Book.objects.all().order_by('-created_at')[:4]
        
        # Add login form for non-authenticated users
        if not self.request.user.is_authenticated:
            context['form'] = AuthenticationForm()
        return context

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('bookshelf')
        return self.render_to_response(self.get_context_data(form=form))

    
class BookDelete(DeleteView):
    model = Book
    success_url = '/bookshelf/'


def about(request):
    return render(request, 'about.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid sign up - try again'
    else:
        form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

def bookshelf(request):
    books = Book.objects.filter(user=request.user)
    return render(request, 'books/bookshelf.html', { 'books': books })

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
            
            print(f"Making request with API key: {settings.GOOGLE_BOOKS_API_KEY}")
            print(f"Full request URL: {api_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}")
            response = requests.get(api_url, params=params, timeout=10)
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text[:500]}...")  
            
            if response.status_code == 200:
                data = response.json()
                print(f"Found {data.get('totalItems', 0)} total items")
                
                if 'items' in data:
                    for item in data['items']:
                        volume_info = item.get('volumeInfo', {})
                        image_links = volume_info.get('imageLinks', {})
                        
                        # Try to get larger image first, fall back to thumbnail
                        cover_url = image_links.get('large', '') or image_links.get('medium', '') or image_links.get('small', '') or image_links.get('thumbnail', '')
                        if cover_url:
                            # Replace zoom level to get higher quality image
                            cover_url = cover_url.replace('http://', 'https://').replace('&zoom=1', '&zoom=0')
                        
                        book_data = {
                            'id': item.get('id'),
                            'title': volume_info.get('title', ''),
                            'author': volume_info.get('authors', ['Unknown Author'])[0],
                            'cover_url': cover_url,
                            'isbn_13': next((id.get('identifier') for id in volume_info.get('industryIdentifiers', []) 
                                          if id.get('type') == 'ISBN_13'), None),
                            'page_count': volume_info.get('pageCount', 0)
                        }
                        print(f"Processing book: {book_data['title']} by {book_data['author']}")
                        search_results.append(book_data)
                else:
                    error = "No books found matching your search."
                    print("No items found in response")
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
                
                print("Raw volume info:", volume_info)
                
                raw_title = volume_info.get('title', '')
                raw_authors = volume_info.get('authors', ['Unknown Author'])
                raw_author_string = ', '.join(raw_authors)
                
                print(f"Raw title (length {len(raw_title)}): {raw_title}")
                print(f"Raw authors: {raw_authors}")
                print(f"Raw author string (length {len(raw_author_string)}): {raw_author_string}")
                
                title = raw_title[:497] + '...' if len(raw_title) > 500 else raw_title
                author_string = raw_author_string[:497] + '...' if len(raw_author_string) > 500 else raw_author_string
                
                print(f"Final title (length {len(title)}): {title}")
                print(f"Final author string (length {len(author_string)}): {author_string}")
                
                # Try to get larger image first, fall back to thumbnail
                image_links = volume_info.get('imageLinks', {})
                cover_url = image_links.get('large', '') or image_links.get('medium', '') or image_links.get('small', '') or image_links.get('thumbnail', '')
                if cover_url:
                    # Replace zoom level to get higher quality image
                    cover_url = cover_url.replace('http://', 'https://').replace('&zoom=1', '&zoom=0')
                    print(f"Cover URL (length {len(cover_url)}): {cover_url}")
                    cover_url = cover_url[:200]
                
                try:
                    isbn13 = None
                    industry_identifiers = volume_info.get('industryIdentifiers', [])
                    for identifier in industry_identifiers:
                        if identifier.get('type') == 'ISBN_13':
                            isbn13 = identifier.get('identifier', '')[:13]
                            print(f"ISBN-13: {isbn13}")
                            break

                    book = Book.objects.create(
                        user=request.user,
                        title=title[:500],
                        author=author_string[:500],
                        cover_url=cover_url,
                        isbn13=isbn13,
                        total_pages=volume_info.get('pageCount', 0),
                        status='plan_to_read'
                    )
                except Exception as field_error:
                    print(f"Field error: {str(field_error)}")
                    raise Exception(f"Error with book fields: {str(field_error)}")
                
                messages.success(request, f'"{book.title}" has been added to your bookshelf!')
                return redirect('bookshelf')
            else:
                messages.error(request, 'Could not fetch book details. Please try again.')
        except Exception as e:
            messages.error(request, f'Error adding book: {str(e)}')
            print(f"Error in book_add: {str(e)}")
            print(f"Title length: {len(title)}")
            print(f"Author length: {len(author_string)}")
    
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
def bookshelf(request):
    books = Book.objects.filter(user=request.user)
    
    # Add search filter
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) | 
            Q(author__icontains=search_query)
        )
    
    # Keep default ordering
    books = books.order_by('-updated_at')
    
    return render(request, 'books/bookshelf.html', {
        'books': books,
        'search_query': search_query,
    })
