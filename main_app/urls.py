from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('bookshelf/', views.bookshelf, name='bookshelf'),
    path('bookshelf/<int:book_id>/', views.book_detail, name='bookshelf-detail'),
    path('bookshelf/<int:pk>/remove/', views.BookDelete.as_view(), name='book-remove'),
    path('bookshelf/<int:book_id>/update-notes/', views.update_notes, name='update-notes'),
    path('bookshelf/<int:book_id>/update-progress/', views.update_progress, name='update-progress'),
    path('bookshelf/<int:book_id>/update-rating/', views.update_rating, name='update-rating'),
    path('bookshelf/<int:book_id>/update-status/', views.update_status, name='update-status'),
    path('bookshelf/search/', views.book_search, name='book-search'),
    path('bookshelf/add/', views.book_add, name='book-add'),
]
