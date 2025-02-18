import requests
from django.shortcuts import render, redirect
from main_app.models import Book
from django.http import HttpResponse
from django.views.generic import ListView
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.conf import settings

class Home(LoginView):
    template_name = 'home.html'

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
        'bookshelf': bookshelf,
    })

def book_search(request):
    search_results = []
    if 'q' in request.GET:
        query = request.GET.get('q', '')
        api_key = settings.GOOGLE_BOOKS_API_KEY
        url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if 'items' in data:
                    for item in data['items']:
                        volume_info = item.get('volumeInfo', {})
                        book_data = {
                            'id': item.get('id'),
                            'title': volume_info.get('title', 'Unknown Title'),
                            'authors': volume_info.get('authors', ['Unknown Author'])[0],
                            'cover_url': volume_info.get('imageLinks', {}).get('thumbnail', ''),
                            'isbn_13': next((id_info['identifier'] for id_info in volume_info.get('industryIdentifiers', [])
                                      if id_info['type'] == 'ISBN_13'), None),
                            'page_count': volume_info.get('pageCount', 0),
                        }
                        search_results.append(book_data)
        except requests.RequestException as e:
            print(f"Error fetching books: {e}")
    
    return render(request, 'books/search.html', {'results': search_results})