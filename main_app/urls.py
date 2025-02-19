from django.urls import path
from . import views 

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),
    path('bookshelf/', views.bookshelf, name='bookshelf'),
    path('bookshelf/<int:book_id>/', views.book_detail, name='bookshelf-detail'),
    path('bookshelf/search/', views.book_search, name='book-search'),
    path('bookshelf/add/', views.book_add, name='book-add'),
    path('bookshelf/create/', views.BookCreate.as_view(), name='book-create'),
    #path('books/<int:book_id>/update/', views.book_update, name='book-update'),
    #path('books/<int:book_id>/delete/', views.book_delete, name='book-delete'),
]
