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
    path('books/<int:book_id>/notes/', views.update_notes, name='update-notes'),
    path('books/<int:book_id>/progress/', views.update_progress, name='update-progress'),
    #path('books/<int:book_id>/update/', views.book_update, name='book-update'),
    path('bookshelf/<int:pk>/remove/', views.BookDelete.as_view(), name='book-remove'),
]
