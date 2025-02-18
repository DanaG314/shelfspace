from django.urls import path
from . import views 

urlpatterns = [
    #path('', views.Home, name='home'),
    path('', views.Home.as_view(), name='home'),
    path('accounts/signup/', views.signup, name='signup'),
    path('about/', views.about, name='about'),
    path('bookshelf/', views.bookshelf, name='bookshelf'),
    path('bookshelf/<int:book_id>/', views.book_detail, name='bookshelf-detail'),
    path('bookshelf/search/', views.book_search, name='book-search'),
    # path('bookshelf/add/', views.book_add, name='book-add'),
]
